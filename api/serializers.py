"""
DRF Serializers for healthcare fraud detection API.
"""

from rest_framework import serializers
from .models import Transaction, Alert, AuditLog


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'caseid', 'age', 'wealth_idx', 'education', 'residence',
            'has_diabetes', 'has_htn', 'DVS', 'TNS', 'ICS', 'CCS',
            'HCFD_score', 'rule_score', 'anomaly_score', 'final_risk',
            'risk_tier', 'explanation', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ScoreTransactionSerializer(serializers.Serializer):
    """Serializer for scoring a new transaction."""
    
    caseid = serializers.CharField(max_length=50, required=True)
    age = serializers.IntegerField(min_value=0, max_value=150, required=True)
    wealth_idx = serializers.FloatField(required=False, default=2.5)
    education = serializers.CharField(max_length=100, required=False, default='')
    residence = serializers.CharField(max_length=100, required=False, default='')
    has_diabetes = serializers.BooleanField(required=False, default=False)
    has_htn = serializers.BooleanField(required=False, default=False)
    screening_count = serializers.IntegerField(min_value=0, max_value=10, required=False, default=0)
    told_high_gluc = serializers.BooleanField(required=False, default=False)
    told_high_bp = serializers.BooleanField(required=False, default=False)
    tx_diabetes = serializers.BooleanField(required=False, default=False)
    tx_htn = serializers.BooleanField(required=False, default=False)
    
    def validate_caseid(self, value):
        """Validate that caseid is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Case ID cannot be empty")
        return value


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model."""
    
    transaction_caseid = serializers.CharField(source='transaction.caseid', read_only=True)
    
    class Meta:
        model = Alert
        fields = ['id', 'transaction', 'transaction_caseid', 'risk_tier', 'final_risk', 'message', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'created_at', 'transaction']


class AlertResolveSerializer(serializers.ModelSerializer):
    """Serializer for resolving alerts."""
    
    class Meta:
        model = Alert
        fields = ['id', 'is_resolved', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'user', 'endpoint', 'ip_address', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""
    
    total_transactions = serializers.IntegerField()
    risk_tier_counts = serializers.DictField()
    average_risk = serializers.FloatField()
    total_flagged = serializers.IntegerField()
    monthly_counts = serializers.ListField(child=serializers.DictField())
    top_risk_records = serializers.ListField(child=serializers.DictField())
