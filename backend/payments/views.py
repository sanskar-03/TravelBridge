import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
from .models import PaymentTransaction
from proposals.models import Proposal
from .serializers import PaymentTransactionSerializer
from .services import calculate_pricing, MockPaymentGateway

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides read-only access to a user's transactions.
    Creation is handled strictly via the /checkout/ endpoint.
    """
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Secure checkout initiation. 
        Ignores any amount/currency sent by the client.
        """
        proposal_id = request.data.get('proposal_id')
        idempotency_key = request.data.get('idempotency_key', str(uuid.uuid4()))

        with transaction.atomic():
            try:
                # Lock the proposal to prevent concurrent checkout processing
                proposal = Proposal.objects.select_for_update().get(id=proposal_id, requester=request.user)
            except Proposal.DoesNotExist:
                return Response({"detail": "Proposal not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

            if proposal.status != Proposal.Status.ACCEPTED:
                return Response({"detail": "Only ACCEPTED proposals can be paid for."}, status=status.HTTP_400_BAD_REQUEST)

            # Idempotency check: if transaction already exists for this proposal, return it
            existing_tx = PaymentTransaction.objects.filter(proposal=proposal).first()
            if existing_tx:
                return Response(PaymentTransactionSerializer(existing_tx).data, status=status.HTTP_200_OK)

            # 1. Authoritative Pricing Calculation
            pricing = calculate_pricing(proposal.proposed_price)

            # 2. Gateway Abstraction: Create Order
            gateway_order = MockPaymentGateway.create_order(
                amount=pricing['total_amount'],
                currency=pricing['currency'],
                receipt_id=str(proposal.id)
            )

            # 3. Create Internal Transaction Record
            tx = PaymentTransaction.objects.create(
                user=request.user,
                proposal=proposal,
                base_amount=pricing['base_amount'],
                platform_fee=pricing['platform_fee'],
                tax_amount=pricing['tax_amount'],
                total_amount=pricing['total_amount'],
                currency=pricing['currency'],
                gateway_order_id=gateway_order['id'],
                idempotency_key=idempotency_key,
                status=PaymentTransaction.Status.PENDING
            )

            return Response(PaymentTransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def webhook(self, request):
        """
        Secure webhook handler for gateway callbacks.
        Idempotent and relies on gateway signature verification.
        """
        signature = request.headers.get('X-Gateway-Signature', '')
        secret = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', 'test_secret')

        if not MockPaymentGateway.verify_webhook_signature(request.body, signature, secret):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST)

        event_data = request.data
        order_id = event_data.get('order_id')
        event_status = event_data.get('status')

        with transaction.atomic():
            try:
                tx = PaymentTransaction.objects.select_for_update().get(gateway_order_id=order_id)
            except PaymentTransaction.DoesNotExist:
                return Response({"detail": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

            # Idempotency: Do not process if already succeeded/failed
            if tx.status in [PaymentTransaction.Status.SUCCEEDED, PaymentTransaction.Status.FAILED]:
                return Response({"detail": "Event already processed."}, status=status.HTTP_200_OK)

            if event_status == 'captured':
                tx.status = PaymentTransaction.Status.SUCCEEDED
                tx.gateway_payment_id = event_data.get('payment_id')
                tx.save()
                
                # Automatically create the canonical Order from the successful payment
                from orders.services import create_order_from_payment
                create_order_from_payment(tx)

            elif event_status == 'failed':
                tx.status = PaymentTransaction.Status.FAILED
                tx.failure_reason = event_data.get('error_description', 'Gateway reported failure.')
                tx.save()

        return Response({"status": "success"}, status=status.HTTP_200_OK)
