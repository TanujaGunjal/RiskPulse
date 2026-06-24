from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """Model representing a healthcare transaction for fraud detection."""
    
    RISK_TIER_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    caseid = models.CharField(max_length=50, unique=True, db_index=True)
    age = models.IntegerField()
    wealth_idx = models.FloatField()
    education = models.CharField(max_length=100)
    residence = models.CharField(max_length=100)
    has_diabetes = models.BooleanField()
    has_htn = models.BooleanField()
    DVS = models.FloatField()
    TNS = models.FloatField()
    ICS = models.FloatField()
    CCS = models.FloatField()
    HCFD_score = models.FloatField()
    rule_score = models.FloatField()
    anomaly_score = models.FloatField()
    final_risk = models.FloatField(
        help_text="Risk score between 0 and 1"
    )
    risk_tier = models.CharField(
        max_length=20,
        choices=RISK_TIER_CHOICES,
        db_index=True
    )
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['caseid']),
            models.Index(fields=['risk_tier', '-created_at']),
        ]
    
    def __str__(self):
        return f"Transaction {self.caseid} - Risk: {self.get_risk_tier_display()}"


class Alert(models.Model):
    """Model representing alerts generated from high-risk transactions."""
    
    RISK_TIER_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    risk_tier = models.CharField(
        max_length=20,
        choices=RISK_TIER_CHOICES,
        db_index=True
    )
    final_risk = models.FloatField(
        help_text="Risk score at time of alert"
    )
    message = models.TextField()
    is_resolved = models.BooleanField(
        default=False,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Alerts"
        indexes = [
            models.Index(fields=['is_resolved', '-created_at']),
            models.Index(fields=['risk_tier', '-created_at']),
        ]
    
    def __str__(self):
        status = "Resolved" if self.is_resolved else "Open"
        return f"Alert {self.id} - {self.transaction.caseid} ({status})"


class AuditLog(models.Model):
    """Model for tracking audit logs of system actions."""
    
    action = models.CharField(max_length=255)
    user = models.CharField(max_length=150)
    endpoint = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Audit Logs"
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"


class InsuranceDecision(models.Model):
    """Model for storing insurance approval/denial decisions."""
    
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('pending', 'Pending Review'),
        ('conditional', 'Conditional Approval'),
    ]
    
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='insurance_decision'
    )
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default='pending',
        db_index=True
    )
    reason = models.TextField(
        help_text="Reason for insurance decision"
    )
    coverage_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Approved coverage amount in currency"
    )
    denial_reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="If denied, specify reason"
    )
    reviewer = models.CharField(
        max_length=150,
        blank=True,
        help_text="User who made the decision"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Insurance Decisions"
        indexes = [
            models.Index(fields=['decision', '-created_at']),
        ]
    
    def __str__(self):
        return f"Insurance Decision for {self.transaction.caseid} - {self.get_decision_display()}"


class ExplainabilityResult(models.Model):
    """Model for storing HCFD-XAI explainability outputs."""
    
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='explainability'
    )
    
    # Feature importance scores
    feature_importance = models.JSONField(
        default=dict,
        help_text="Feature importance scores from model"
    )
    
    # SHAP or similar explainability values
    shap_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="SHAP values for each feature"
    )
    
    # Rule violations
    rule_violations = models.JSONField(
        default=list,
        help_text="List of medical rule violations"
    )
    
    # Contributing factors
    key_factors = models.JSONField(
        default=list,
        help_text="Top factors contributing to risk score"
    )
    
    # Model metadata
    model_versions = models.JSONField(
        default=dict,
        help_text="Versions of models used (XGBoost, Isolation Forest, etc.)"
    )
    
    explanation_text = models.TextField(
        help_text="Human-readable explanation of the prediction"
    )
    
    confidence_score = models.FloatField(
        default=1.0,
        help_text="Model confidence in prediction (0-1)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Explainability Results"
    
    def __str__(self):
        return f"Explainability for {self.transaction.caseid}"


class ModelMetadata(models.Model):
    """Track ML model versions and performance metrics."""
    
    MODEL_TYPE_CHOICES = [
        ('xgboost', 'XGBoost'),
        ('isolation_forest', 'Isolation Forest'),
        ('autoencoder', 'Autoencoder'),
        ('hcfd', 'HCFD Ensemble'),
        ('rule_engine', 'Rule Engine'),
    ]
    
    model_type = models.CharField(
        max_length=50,
        choices=MODEL_TYPE_CHOICES,
        db_index=True
    )
    model_version = models.CharField(
        max_length=20,
        help_text="e.g., 1.0.0"
    )
    model_path = models.CharField(
        max_length=500,
        help_text="Path to model file (.pkl, .h5, etc.)"
    )
    
    training_dataset = models.CharField(
        max_length=100,
        help_text="e.g., NFHS-5, Custom"
    )
    training_size = models.IntegerField(
        help_text="Number of training samples"
    )
    
    # Performance metrics
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    auc_roc = models.FloatField(null=True, blank=True)
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Currently in use for predictions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Model Metadata"
        indexes = [
            models.Index(fields=['model_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_model_type_display()} v{self.model_version}"
