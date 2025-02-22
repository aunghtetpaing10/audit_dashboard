from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    approved_by = serializers.StringRelatedField() # Show username instead of ID
    
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'status', 'timestamp', 'is_flagged', 'merchant', 'approved_by']
        
class TransactionApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['status', 'approved_by']

class TransactionToggleFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['is_flagged']