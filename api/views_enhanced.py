"""
Enhanced API Views for insurance, explainability, and analytics
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import (
    Transaction, Alert, InsuranceDecision,
    ExplainabilityResult, ModelMetadata
)
from .serializers_enhanced import (
    InsuranceDecisionSerializer, ExplainabilityResultSerializer,
    ModelMetadataSerializer, TransactionDetailSerializer
)


class InsuranceDecisionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for insurance decisions.
    
    Endpoints:
        GET    /api/insurance-decisions/          - List all decisions
        POST   /api/insurance-decisions/          - Create new decision
        GET    /api/insurance-decisions/{id}/     - Get decision details
        PATCH  /api/insurance-decisions/{id}/     - Update decision
        DELETE /api/insurance-decisions/{id}/     - Delete decision
        GET    /api/insurance-decisions/stats/    - Get statistics
    """
    
    queryset = InsuranceDecision.objects.all()
    serializer_class = InsuranceDecisionSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get insurance decision statistics."""
        
        total_decisions = InsuranceDecision.objects.count()
        
        decision_counts = InsuranceDecision.objects.values('decision').annotate(
            count=Count('id')
        )
        
        pending = InsuranceDecision.objects.filter(decision='pending').count()
        approved = InsuranceDecision.objects.filter(decision='approved').count()
        denied = InsuranceDecision.objects.filter(decision='denied').count()
        
        # Average coverage amount for approved decisions
        avg_coverage = InsuranceDecision.objects.filter(
            decision='approved',
            coverage_amount__isnull=False
        ).aggregate(Avg('coverage_amount'))['coverage_amount__avg']
        
        # Approval rate
        approval_rate = approved / total_decisions if total_decisions > 0 else 0.0
        
        # Recent decisions (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_count = InsuranceDecision.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        return Response({
            'total_decisions': total_decisions,
            'pending': pending,
            'approved': approved,
            'denied': denied,
            'conditional': InsuranceDecision.objects.filter(
                decision='conditional'
            ).count(),
            'approval_rate': approval_rate,
            'average_coverage': avg_coverage,
            'recent_decisions_7d': recent_count,
        })
    
    @action(detail=True, methods=['post'])
    def mark_pending(self, request, pk=None):
        """Mark decision as pending review."""
        decision = self.get_object()
        decision.decision = 'pending'
        decision.save()
        return Response(
            {'status': 'Decision marked as pending'},
            status=status.HTTP_200_OK
        )


class ExplainabilityResultViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for explainability results.
    
    Endpoints:
        GET    /api/explainability/           - List all results
        GET    /api/explainability/{id}/      - Get result details
        GET    /api/explainability/violation-stats/  - Get violation statistics
    """
    
    queryset = ExplainabilityResult.objects.all()
    serializer_class = ExplainabilityResultSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def violation_stats(self, request):
        """Get statistics on rule violations."""
        
        results = ExplainabilityResult.objects.all()
        
        violation_counts = {}
        total_violations = 0
        
        for result in results:
            for violation in result.rule_violations:
                violation_counts[violation] = violation_counts.get(violation, 0) + 1
                total_violations += 1
        
        # Sort by frequency
        top_violations = sorted(
            violation_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return Response({
            'total_violations': total_violations,
            'unique_violations': len(violation_counts),
            'top_violations': [
                {'violation': v[0], 'count': v[1]} for v in top_violations
            ],
        })


class ModelMetadataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for model metadata (read-only).
    
    Endpoints:
        GET    /api/models/              - List all models
        GET    /api/models/{id}/         - Get model details
        GET    /api/models/active/       - List active models
    """
    
    queryset = ModelMetadata.objects.all()
    serializer_class = ModelMetadataSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active models."""
        active_models = ModelMetadata.objects.filter(is_active=True)
        serializer = self.get_serializer(active_models, many=True)
        return Response(serializer.data)


class AnalyticsDashboardView(viewsets.ViewSet):
    """
    Comprehensive analytics dashboard combining all metrics.
    
    Endpoints:
        GET /api/analytics/dashboard/  - Get all dashboard metrics
        GET /api/analytics/trends/     - Get 30-day trends
        GET /api/analytics/model-performance/  - Get model metrics
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive dashboard metrics."""
        
        # Risk statistics
        transactions = Transaction.objects.all()
        total = transactions.count()
        
        risk_dist = transactions.values('risk_tier').annotate(count=Count('id'))
        
        # Insurance statistics
        insurance_stats = InsuranceDecision.objects.values('decision').annotate(
            count=Count('id')
        )
        
        # Alert statistics
        total_alerts = Alert.objects.count()
        open_alerts = Alert.objects.filter(is_resolved=False).count()
        
        # Average scores
        avg_risk = transactions.aggregate(Avg('final_risk'))['final_risk__avg'] or 0.0
        
        # Violations
        explainability_results = ExplainabilityResult.objects.all()
        total_violations = sum(
            len(result.rule_violations)
            for result in explainability_results
        )
        
        # Model status
        active_models = ModelMetadata.objects.filter(is_active=True).count()
        total_models = ModelMetadata.objects.count()
        
        return Response({
            'transactions': {
                'total': total,
                'risk_distribution': {
                    item['risk_tier']: item['count']
                    for item in risk_dist
                },
                'average_risk_score': avg_risk,
            },
            'insurance': {
                'total_decisions': InsuranceDecision.objects.count(),
                'by_decision': {
                    item['decision']: item['count']
                    for item in insurance_stats
                },
            },
            'alerts': {
                'total': total_alerts,
                'open': open_alerts,
                'resolved': total_alerts - open_alerts,
            },
            'fraud_indicators': {
                'total_violations': total_violations,
                'results_analyzed': explainability_results.count(),
            },
            'models': {
                'active': active_models,
                'total': total_models,
                'status': 'Operational' if active_models > 0 else 'Offline',
            },
            'timestamp': timezone.now(),
        })
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get 30-day trends."""
        
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Daily transaction counts
        daily_data = (
            Transaction.objects
            .filter(created_at__gte=start_date)
            .values('created_at__date')
            .annotate(
                count=Count('id'),
                avg_risk=Avg('final_risk'),
                high_risk=Count('id', filter=Q(risk_tier__in=['high', 'critical']))
            )
            .order_by('created_at__date')
        )
        
        # Daily insurance decisions
        daily_insurance = (
            InsuranceDecision.objects
            .filter(created_at__gte=start_date)
            .values('created_at__date', 'decision')
            .annotate(count=Count('id'))
            .order_by('created_at__date')
        )
        
        return Response({
            'period_days': days,
            'start_date': start_date,
            'daily_transactions': [
                {
                    'date': item['created_at__date'],
                    'count': item['count'],
                    'avg_risk': item['avg_risk'],
                    'high_risk_count': item['high_risk'],
                }
                for item in daily_data
            ],
            'daily_insurance_decisions': list(daily_insurance),
        })
    
    @action(detail=False, methods=['get'])
    def model_performance(self, request):
        """Get model performance metrics."""
        
        models = ModelMetadata.objects.filter(is_active=True)
        
        performance_data = []
        for model in models:
            performance_data.append({
                'model_type': model.get_model_type_display(),
                'version': model.model_version,
                'accuracy': model.accuracy,
                'precision': model.precision,
                'recall': model.recall,
                'f1_score': model.f1_score,
                'auc_roc': model.auc_roc,
                'last_updated': model.updated_at,
            })
        
        return Response({
            'active_models': len(models),
            'model_performance': performance_data,
        })
