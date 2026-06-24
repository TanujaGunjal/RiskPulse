from django.contrib import admin
from .models import Transaction, Alert, AuditLog


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('caseid', 'age', 'final_risk', 'risk_tier', 'created_at')
    list_filter = ('risk_tier', 'created_at', 'has_diabetes', 'has_htn')
    search_fields = ('caseid',)
    readonly_fields = ('created_at', 'caseid')
    fieldsets = (
        ('Transaction Info', {
            'fields': ('caseid', 'age', 'education', 'residence', 'created_at')
        }),
        ('Health Information', {
            'fields': ('has_diabetes', 'has_htn')
        }),
        ('Scores', {
            'fields': ('DVS', 'TNS', 'ICS', 'CCS', 'HCFD_score', 'rule_score', 'anomaly_score')
        }),
        ('Risk Assessment', {
            'fields': ('final_risk', 'risk_tier', 'explanation')
        }),
        ('Wealth Info', {
            'fields': ('wealth_idx',)
        }),
    )


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'risk_tier', 'final_risk', 'is_resolved', 'created_at')
    list_filter = ('risk_tier', 'is_resolved', 'created_at')
    search_fields = ('transaction__caseid',)
    readonly_fields = ('created_at', 'transaction')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'endpoint', 'ip_address', 'timestamp')
    list_filter = ('action', 'user', 'timestamp')
    search_fields = ('user', 'endpoint', 'action')
    readonly_fields = ('timestamp', 'action', 'user', 'endpoint', 'ip_address')
