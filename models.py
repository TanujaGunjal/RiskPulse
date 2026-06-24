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
