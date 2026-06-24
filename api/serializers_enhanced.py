"""
New API Serializers for enhanced fraud detection system
"""

from rest_framework import serializers
from .models import (
    Transaction, Alert, AuditLog,
    InsuranceDecision, ExplainabilityResult, ModelMetadata
)


class InsuranceDecisionSerializer(serializers.ModelSerializer):
    """Serializer for insurance decisions."""
    
    transaction_caseid = serializers.CharField(
        source='transaction.caseid',
        read_only=True
    )
    
    class Meta:
        model = InsuranceDecision
        fields = [
            'id', 'transaction', 'transaction_caseid', 'decision',
            'reason', 'coverage_amount', 'denial_reason', 'reviewer',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ExplainabilityResultSerializer(serializers.ModelSerializer):
    """Serializer for explainability results."""
    
    transaction_caseid = serializers.CharField(
        source='transaction.caseid',
        read_only=True
    )
    
    class Meta:
        model = ExplainabilityResult
        fields = [
            'id', 'transaction', 'transaction_caseid',
            'feature_importance', 'shap_values', 'rule_violations',
            'key_factors', 'model_versions', 'explanation_text',
            'confidence_score', 'created_at'
        ]
        read_only_fields = ['created_at']


class ModelMetadataSerializer(serializers.ModelSerializer):
    """Serializer for model metadata."""
    
    class Meta:
        model = ModelMetadata
        fields = [
            'id', 'model_type', 'model_version', 'model_path',
            'training_dataset', 'training_size', 'accuracy',
            'precision', 'recall', 'f1_score', 'auc_roc',
            'is_active', 'created_at', 'updated_at'
        ]


class TransactionDetailSerializer(serializers.ModelSerializer):
    """Extended transaction serializer with related data."""
    
    insurance_decision = InsuranceDecisionSerializer(read_only=True)
    explainability = ExplainabilityResultSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'caseid', 'age', 'wealth_idx', 'education',
            'residence', 'has_diabetes', 'has_htn',
            'DVS', 'TNS', 'ICS', 'CCS', 'HCFD_score',
            'rule_score', 'anomaly_score', 'final_risk', 'risk_tier',
            'explanation', 'insurance_decision', 'explainability',
            'created_at'
        ]
