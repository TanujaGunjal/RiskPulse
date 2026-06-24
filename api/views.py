"""
Django REST Framework views for healthcare fraud detection API.

Provides endpoints for transaction scoring, alert management, and reporting.
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F, FloatField
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.http import FileResponse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from io import BytesIO
from datetime import timedelta
import logging

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors

from .models import Transaction, Alert, AuditLog, ExplainabilityResult, InsuranceDecision
from .ml.scorer import compute_final_risk


logger = logging.getLogger(__name__)


class AuditLogMixin:
    """Mixin to automatically log API requests to AuditLog."""
    
    def log_audit(self, request, action: str, endpoint: str):
        """Create an AuditLog entry for the request."""
        try:
            user = getattr(request.user, 'username', 'anonymous')
            ip_address = self.get_client_ip(request)
            
            AuditLog.objects.create(
                action=action,
                user=user,
                endpoint=endpoint,
                ip_address=ip_address,
            )
        except Exception as e:
            logger.error(f"Error logging audit: {e}")
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


class ScoreTransactionView(APIView, AuditLogMixin):
    """
    POST /api/score/
    
    Accept transaction inputs, compute fraud risk score, save to database,
    and create alert if risk is critical.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Score a transaction and save to database."""
        self.log_audit(request, "SCORE_TRANSACTION", "/api/score/")
        
        try:
            # Extract input parameters
            caseid = request.data.get('caseid')
            age = int(request.data.get('age'))
            wealth_idx = float(request.data.get('wealth_idx'))
            education = request.data.get('education', '')
            residence = request.data.get('residence', '')
            has_diabetes = request.data.get('has_diabetes', False)
            has_htn = request.data.get('has_htn', False)
            screening_count = int(request.data.get('screening_count', 0))
            told_high_gluc = request.data.get('told_high_gluc', False)
            told_high_bp = request.data.get('told_high_bp', False)
            tx_diabetes = request.data.get('tx_diabetes', False)
            tx_htn = request.data.get('tx_htn', False)
            
            # Validate required fields
            if not caseid:
                return Response(
                    {'error': 'caseid is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Compute fraud risk
            result = compute_final_risk(
                age=age,
                wealth_idx=wealth_idx,
                screening_count=screening_count,
                has_diabetes=has_diabetes,
                has_htn=has_htn,
                told_high_gluc=told_high_gluc,
                told_high_bp=told_high_bp,
                tx_diabetes=tx_diabetes,
                tx_htn=tx_htn,
            )
            
            # Extract scores
            final_risk = result['final_risk']
            risk_tier = result['risk_tier']
            explanation = result['explanation']
            scores = result['scores']
            
            # Create Transaction record
            transaction = Transaction.objects.create(
                caseid=caseid,
                age=age,
                wealth_idx=wealth_idx,
                education=education,
                residence=residence,
                has_diabetes=has_diabetes,
                has_htn=has_htn,
                DVS=scores['DVS'],
                TNS=scores['TNS'],
                ICS=scores['ICS'],
                CCS=scores['CCS'],
                HCFD_score=scores['HCFD'],
                rule_score=scores['rule_score'],
                anomaly_score=scores['anomaly_score'],
                final_risk=final_risk,
                risk_tier=risk_tier,
                explanation=explanation,
            )
            
            # Create Alert if critical risk
            alert = None
            if final_risk > 0.75:
                alert = Alert.objects.create(
                    transaction=transaction,
                    risk_tier=risk_tier,
                    final_risk=final_risk,
                    message=f"Critical fraud risk detected: {final_risk:.3f}",
                    is_resolved=False,
                )
                self.log_audit(request, "ALERT_CREATED", "/api/score/")
            
            # Create ExplainabilityResult
            explainability = ExplainabilityResult.objects.create(
                transaction=transaction,
                feature_importance={
                    'DVS': float(scores['DVS']),
                    'TNS': float(scores['TNS']),
                    'ICS': float(scores['ICS']),
                    'CCS': float(scores['CCS']),
                    'HCFD': float(scores['HCFD']),
                    'rule_score': float(scores['rule_score']),
                    'anomaly_score': float(scores['anomaly_score']),
                },
                rule_violations=result['rule_violations'],
                key_factors=[f"{k}: {v:.3f}" for k, v in scores.items()],
                model_versions={
                    'scorer': '1.0.0',
                    'isolation_forest': 'v1',
                    'random_forest': 'v1',
                },
                explanation_text=explanation,
                confidence_score=1.0 - (abs(0.5 - final_risk) / 0.5),
            )
            
            # Create InsuranceDecision
            insurance_decision = InsuranceDecision.objects.create(
                transaction=transaction,
                decision='pending',
                reason=f"Risk score {final_risk:.3f} ({risk_tier}). Awaiting review.",
                reviewer='',
            )
            
            return Response({
                'transaction_id': transaction.id,
                'caseid': transaction.caseid,
                'final_risk': final_risk,
                'risk_tier': risk_tier,
                'alert_id': alert.id if alert else None,
                'explainability_id': explainability.id,
                'insurance_decision_id': insurance_decision.id,
                'scores': scores,
                'explanation': explanation,
                'rule_violations': result['rule_violations'],
            }, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {'error': f'Invalid input: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as e:
            # Handle duplicate case ID
            if 'caseid' in str(e):
                return Response(
                    {'error': f'Case ID "{caseid}" already exists. Please use a unique case ID.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            logger.error(f"Error scoring transaction: {e}")
            return Response(
                {'error': 'Database integrity error'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error scoring transaction: {e}")
            return Response(
                {'error': 'Error processing transaction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionPagination(PageNumberPagination):
    """Custom pagination for transaction list."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TransactionListView(APIView, AuditLogMixin):
    """
    GET /api/transactions/
    
    Return paginated list of transactions with optional filtering by risk_tier,
    risk range, and caseid search.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get paginated transaction list with optional filters."""
        self.log_audit(request, "LIST_TRANSACTIONS", "/api/transactions/")
        
        try:
            # Start with all transactions
            queryset = Transaction.objects.all()
            
            # Filter by risk tier
            risk_tier = request.query_params.get('risk_tier')
            if risk_tier:
                queryset = queryset.filter(risk_tier=risk_tier)
            
            # Filter by risk range
            min_risk = request.query_params.get('min_risk')
            max_risk = request.query_params.get('max_risk')
            if min_risk:
                queryset = queryset.filter(final_risk__gte=float(min_risk))
            if max_risk:
                queryset = queryset.filter(final_risk__lte=float(max_risk))
            
            # Search by caseid
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(caseid__icontains=search)
            
            # Paginate results
            paginator = TransactionPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # Serialize results
            results = []
            for transaction in paginated_queryset:
                results.append({
                    'id': transaction.id,
                    'caseid': transaction.caseid,
                    'age': transaction.age,
                    'final_risk': transaction.final_risk,
                    'risk_tier': transaction.risk_tier,
                    'created_at': transaction.created_at,
                    'has_alerts': transaction.alerts.filter(is_resolved=False).exists(),
                })
            
            return paginator.get_paginated_response(results)
        
        except Exception as e:
            logger.error(f"Error listing transactions: {e}")
            return Response(
                {'error': 'Error retrieving transactions'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardStatsView(APIView, AuditLogMixin):
    """
    GET /api/dashboard/stats/
    
    Return dashboard statistics including risk tier counts, averages,
    monthly trends, and top risk records.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get dashboard statistics."""
        self.log_audit(request, "VIEW_DASHBOARD", "/api/dashboard/stats/")
        
        try:
            queryset = Transaction.objects.all()
            
            # Count by risk tier
            risk_tier_counts = dict(
                queryset.values('risk_tier').annotate(count=Count('id')).values_list('risk_tier', 'count')
            )
            
            # Average final risk
            avg_risk = queryset.aggregate(avg=Avg('final_risk'))['avg'] or 0.0
            
            # Total flagged (final_risk > 0.5)
            total_flagged = queryset.filter(final_risk__gt=0.5).count()
            
            # Monthly counts (last 6 months)
            six_months_ago = timezone.now() - timedelta(days=180)
            monthly_data = queryset.filter(
                created_at__gte=six_months_ago
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            monthly_counts = [
                {
                    'month': item['month'].strftime('%Y-%m'),
                    'count': item['count']
                }
                for item in monthly_data
            ]
            
            # Top 5 risk records
            top_risk = queryset.order_by('-final_risk')[:5]
            top_risk_records = [
                {
                    'id': t.id,
                    'caseid': t.caseid,
                    'final_risk': t.final_risk,
                    'risk_tier': t.risk_tier,
                    'created_at': t.created_at,
                }
                for t in top_risk
            ]
            
            return Response({
                'total_transactions': queryset.count(),
                'risk_tier_counts': risk_tier_counts,
                'average_risk': round(avg_risk, 3),
                'total_flagged': total_flagged,
                'monthly_counts': monthly_counts,
                'top_risk_records': top_risk_records,
            })
        
        except Exception as e:
            logger.error(f"Error retrieving dashboard stats: {e}")
            return Response(
                {'error': 'Error retrieving statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertListView(APIView, AuditLogMixin):
    """
    GET /api/alerts/
    
    Return list of unresolved alerts ordered by final_risk descending.
    """
    
    def get(self, request):
        """Get unresolved alerts."""
        self.log_audit(request, "LIST_ALERTS", "/api/alerts/")
        
        try:
            alerts = Alert.objects.filter(
                is_resolved=False
            ).select_related('transaction').order_by('-final_risk')
            
            results = [
                {
                    'id': alert.id,
                    'transaction_id': alert.transaction.id,
                    'caseid': alert.transaction.caseid,
                    'risk_tier': alert.risk_tier,
                    'final_risk': alert.final_risk,
                    'message': alert.message,
                    'created_at': alert.created_at,
                }
                for alert in alerts
            ]
            
            return Response({
                'count': len(results),
                'alerts': results,
            })
        
        except Exception as e:
            logger.error(f"Error listing alerts: {e}")
            return Response(
                {'error': 'Error retrieving alerts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertResolveView(APIView, AuditLogMixin):
    """
    PATCH /api/alerts/<id>/resolve/
    
    Mark an alert as resolved.
    """
    
    def patch(self, request, alert_id):
        """Resolve an alert."""
        self.log_audit(request, "RESOLVE_ALERT", f"/api/alerts/{alert_id}/resolve/")
        
        try:
            alert = get_object_or_404(Alert, id=alert_id)
            alert.is_resolved = True
            alert.save()
            
            return Response({
                'id': alert.id,
                'is_resolved': alert.is_resolved,
                'message': 'Alert resolved successfully',
            })
        
        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return Response(
                {'error': 'Error resolving alert'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportGenerateView(APIView, AuditLogMixin):
    """
    POST /api/reports/generate/
    
    Generate PDF report with transaction statistics.
    """
    
    def post(self, request):
        """Generate PDF report."""
        self.log_audit(request, "GENERATE_REPORT", "/api/reports/generate/")
        
        try:
            report_type = request.data.get('report_type', 'daily')
            
            # Determine date range
            now = timezone.now()
            if report_type == 'daily':
                date_from = now - timedelta(days=1)
                title = f"Daily Report - {now.strftime('%Y-%m-%d')}"
            elif report_type == 'weekly':
                date_from = now - timedelta(weeks=1)
                title = f"Weekly Report - {now.strftime('%Y-%m-%d')}"
            elif report_type == 'monthly':
                date_from = now - timedelta(days=30)
                title = f"Monthly Report - {now.strftime('%Y-%m')}"
            else:
                return Response(
                    {'error': 'Invalid report_type. Use: daily, weekly, monthly'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Query transactions for period
            transactions = Transaction.objects.filter(created_at__gte=date_from)
            
            # Generate PDF
            pdf_buffer = self._generate_pdf(title, transactions)
            
            return FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=f"fraud_detection_{report_type}_{now.strftime('%Y%m%d')}.pdf",
                content_type='application/pdf',
            )
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return Response(
                {'error': 'Error generating report'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_pdf(self, title: str, transactions):
        """Generate PDF document with transaction statistics."""
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=20,
            alignment=1,  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2e5c8a'),
            spaceAfter=10,
            spaceBefore=10,
        )
        
        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary Statistics
        elements.append(Paragraph("Summary Statistics", heading_style))
        
        total_count = transactions.count()
        avg_risk = transactions.aggregate(avg=Avg('final_risk'))['avg'] or 0.0
        critical_count = transactions.filter(risk_tier='critical').count()
        high_count = transactions.filter(risk_tier='high').count()
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Transactions', str(total_count)],
            ['Average Risk Score', f"{avg_risk:.3f}"],
            ['Critical Risk Count', str(critical_count)],
            ['High Risk Count', str(high_count)],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Risk Distribution
        elements.append(Paragraph("Risk Tier Distribution", heading_style))
        
        risk_counts = dict(
            transactions.values('risk_tier').annotate(count=Count('id')).values_list('risk_tier', 'count')
        )
        
        risk_data = [
            ['Risk Tier', 'Count', 'Percentage'],
        ]
        
        for tier in ['low', 'medium', 'high', 'critical']:
            count = risk_counts.get(tier, 0)
            percentage = (count / total_count * 100) if total_count > 0 else 0
            risk_data.append([
                tier.upper(),
                str(count),
                f"{percentage:.1f}%",
            ])
        
        risk_table = Table(risk_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Top Risk Records
        if total_count > 0:
            elements.append(PageBreak())
            elements.append(Paragraph("Top Risk Records", heading_style))
            
            top_transactions = transactions.order_by('-final_risk')[:10]
            
            top_data = [
                ['Case ID', 'Risk Score', 'Risk Tier', 'Date'],
            ]
            
            for tx in top_transactions:
                top_data.append([
                    tx.caseid,
                    f"{tx.final_risk:.3f}",
                    tx.risk_tier.upper(),
                    tx.created_at.strftime('%Y-%m-%d %H:%M'),
                ])
            
            top_table = Table(top_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            top_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(top_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
