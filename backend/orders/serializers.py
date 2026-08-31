from rest_framework import serializers
from .models import Order
from users.serializers import PublicProfileSerializer

class OrderSerializer(serializers.ModelSerializer):
    traveler = PublicProfileSerializer(source='traveler.profile', read_only=True)
    requester = PublicProfileSerializer(source='requester.profile', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'reference_code', 'traveler', 'requester', 'trip', 'package_request',
            'proposal', 'payment', 'agreed_price', 'currency', 'origin_city', 
            'destination_city', 'package_weight_kg', 'status', 'delivery_status', 
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
