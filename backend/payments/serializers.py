from rest_framework import serializers
from .models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'proposal', 'base_amount', 'platform_fee', 'tax_amount', 
            'total_amount', 'currency', 'status', 'gateway_order_id', 'created_at'
        ]
        # ALL fields are strictly read-only to prevent mass assignment/tampering.
        # Payment creation is handled via a dedicated action, not a generic POST.
        read_only_fields = fields
