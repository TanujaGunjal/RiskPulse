"""
URL configuration for fraud detection API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    ScoreTransactionView,
    TransactionListView,
    DashboardStatsView,
    AlertListView,
    AlertResolveView,
    ReportGenerateView,
)
from api.views_enhanced import (
    InsuranceDecisionViewSet,
    ExplainabilityResultViewSet,
    ModelMetadataViewSet,
    AnalyticsDashboardView,
)

# Initialize router for ViewSets
router = DefaultRouter()
router.register(r'insurance-decisions', InsuranceDecisionViewSet, basename='insurance-decision')
router.register(r'explainability', ExplainabilityResultViewSet, basename='explainability')
router.register(r'models', ModelMetadataViewSet, basename='model-metadata')
router.register(r'analytics', AnalyticsDashboardView, basename='analytics')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Transaction scoring
    path('score/', ScoreTransactionView.as_view(), name='score-transaction'),
    
    # Transaction listing and filtering
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    
    # Dashboard statistics
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Alert management
    path('alerts/', AlertListView.as_view(), name='alert-list'),
    path('alerts/<int:alert_id>/resolve/', AlertResolveView.as_view(), name='alert-resolve'),
    
    # Reporting
    path('reports/generate/', ReportGenerateView.as_view(), name='generate-report'),
]
