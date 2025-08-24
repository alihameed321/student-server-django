from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Q, Count, F, Case, When, Value
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import datetime, timedelta
from ..models import FeeType, StudentFee, PaymentProvider, Payment, PaymentReceipt, FinancialReport
from .serializers import (
    FeeTypeSerializer, StudentFeeSerializer, PaymentProviderSerializer,
    PaymentSerializer, PaymentCreateSerializer, PaymentReceiptSerializer,
    FinancialSummarySerializer, FinancialReportSerializer, EnhancedStudentFeeSerializer,
    MobilePaymentSerializer, PaymentStatisticsSerializer
)
from ..views import generate_receipt_pdf
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# Financial API Views
# Add your financial-related API endpoints here

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_summary(request):
    """
    Get comprehensive financial summary for authenticated student
    Enhanced version with better mobile app support
    """
    try:
        user = request.user
        logger.info(f"Fetching financial summary for user: {user.id}")
        
        # Get all fees for the student with optimized queries
        student_fees = StudentFee.objects.filter(
            student=user
        ).select_related('fee_type').prefetch_related('payments')
        
        # Calculate totals with database aggregation
        fee_aggregates = student_fees.aggregate(
            total_fees=Sum('amount'),
            total_count=Count('id')
        )
        total_fees = fee_aggregates['total_fees'] or Decimal('0.00')
        
        # Calculate pending payments more efficiently
        pending_fees = student_fees.exclude(status='paid')
        pending_payments = sum(fee.remaining_balance for fee in pending_fees)
        
        # Calculate paid amounts with better date filtering
        current_semester_start = timezone.now() - timedelta(days=180)
        paid_this_semester = Payment.objects.filter(
            student=user,
            status='verified',
            verified_at__gte=current_semester_start
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Count overdue fees with proper status handling
        today = timezone.now().date()
        overdue_count = student_fees.filter(
            due_date__lt=today,
            status__in=['pending', 'partial', 'overdue']
        ).count()
        
        # Get recent transactions with better serialization
        recent_transactions = Payment.objects.filter(
            student=user
        ).select_related(
            'fee__fee_type', 'payment_provider', 'verified_by'
        ).order_by('-created_at')[:10]
        
        # Get fee breakdown without annotations (use model property)
        fee_breakdown = student_fees.order_by('-created_at')[:20]  # Limit for mobile performance
        
        # Additional statistics for mobile app
        payment_stats = {
            'total_payments': Payment.objects.filter(student=user).count(),
            'verified_payments': Payment.objects.filter(student=user, status='verified').count(),
            'pending_verification': Payment.objects.filter(student=user, status='pending').count(),
        }
        
        summary_data = {
            'total_fees': total_fees,
            'pending_payments': pending_payments,
            'paid_this_semester': paid_this_semester,
            'overdue_count': overdue_count,
            'recent_transactions': recent_transactions,
            'fee_breakdown': fee_breakdown,
            'payment_statistics': payment_stats,
            'summary_date': timezone.now().isoformat()
        }
        
        serializer = FinancialSummarySerializer(summary_data)
        logger.info(f"Successfully generated financial summary for user: {user.id}")
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating financial summary for user {request.user.id}: {str(e)}")
        return Response(
            {'error': 'Failed to generate financial summary', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class StudentFeeListView(generics.ListAPIView):
    """
    List all fees for the authenticated student with enhanced filtering and mobile support
    """
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        logger.info(f"Fetching student fees for user: {user.id}")
        
        # Base queryset with optimized relations
        queryset = StudentFee.objects.filter(
            student=user
        ).select_related('fee_type').prefetch_related('payments')
        
        # Use model properties instead of annotations
        today = timezone.now().date()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter == 'overdue':
                queryset = queryset.filter(
                    due_date__lt=today,
                    status__in=['pending', 'partial', 'overdue']
                )
            else:
                queryset = queryset.filter(status=status_filter)
        
        # Filter by fee type
        fee_type = self.request.query_params.get('fee_type')
        if fee_type:
            queryset = queryset.filter(fee_type_id=fee_type)
        
        # Filter by outstanding (unpaid) fees
        outstanding_only = self.request.query_params.get('outstanding')
        if outstanding_only and outstanding_only.lower() == 'true':
            queryset = queryset.exclude(status='paid')
        
        # Filter by semester/academic year
        semester = self.request.query_params.get('semester')
        if semester:
            # Assuming semester format like '2024-1' or '2024-2'
            queryset = queryset.filter(description__icontains=semester)
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(fee_type__name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Default ordering by creation date (newest first)
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            # Validate ordering fields to prevent database errors
            valid_fields = ['created_at', '-created_at', 'due_date', '-due_date', 'amount', '-amount', 'status', '-status']
            if ordering in valid_fields:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Enhanced list response with additional metadata"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Get summary statistics
            total_fees = queryset.count()
            # Calculate overdue fees using database fields
            today = timezone.now().date()
            overdue_fees = queryset.filter(
                due_date__lt=today,
                status__in=['pending', 'partial', 'overdue']
            ).count()
            paid_fees = queryset.filter(status='paid').count()
            pending_fees = queryset.exclude(status='paid').count()
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                
                # Add metadata to response
                response.data['metadata'] = {
                    'total_fees': total_fees,
                    'overdue_fees': overdue_fees,
                    'paid_fees': paid_fees,
                    'pending_fees': pending_fees,
                    'filters_applied': {
                        'status': request.query_params.get('status'),
                        'fee_type': request.query_params.get('fee_type'),
                        'outstanding': request.query_params.get('outstanding'),
                        'search': request.query_params.get('search'),
                    }
                }
                return response
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'results': serializer.data,
                'metadata': {
                    'total_fees': total_fees,
                    'overdue_fees': overdue_fees,
                    'paid_fees': paid_fees,
                    'pending_fees': pending_fees,
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching student fees for user {request.user.id}: {str(e)}")
            return Response(
                {'error': 'Failed to fetch student fees', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentFeeDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific fee
    """
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudentFee.objects.filter(
            student=self.request.user
        ).select_related('fee_type')


class PaymentProviderListView(generics.ListAPIView):
    """
    List all active payment providers
    """
    serializer_class = PaymentProviderSerializer
    permission_classes = [IsAuthenticated]
    queryset = PaymentProvider.objects.filter(is_active=True).order_by('name')


class PaymentListView(generics.ListAPIView):
    """
    List all payments for the authenticated student
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Payment.objects.filter(
            student=self.request.user
        ).select_related('fee', 'payment_provider', 'verified_by').order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(payment_date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(payment_date__lte=end_date)
            except ValueError:
                pass
        
        return queryset


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific payment
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(
            student=self.request.user
        ).select_related('fee', 'payment_provider', 'verified_by')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    Create a new payment for selected fees with enhanced validation and transaction management
    """
    user = request.user
    logger.info(f"Payment creation request from user {user.id}: {request.data}")
    
    try:
        # Validate request data
        serializer = PaymentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid payment data from user {user.id}: {serializer.errors}")
            return Response({
                'error': 'Invalid payment data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        logger.info(f"Validated payment data: {validated_data}")
        
        # Use database transaction for atomicity
        with transaction.atomic():
            # Get and validate payment provider
            try:
                payment_provider = PaymentProvider.objects.get(
                    id=validated_data['payment_provider_id'], 
                    is_active=True
                )
                logger.info(f"Payment provider found: {payment_provider.name}")
            except PaymentProvider.DoesNotExist:
                logger.error(f"Invalid payment provider ID: {validated_data['payment_provider_id']}")
                return Response({
                    'error': 'Invalid or inactive payment provider'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract and validate fee data
            fee_ids = [int(fee_data['id']) for fee_data in validated_data['fees']]
            logger.info(f"Requested fee IDs: {fee_ids}")
            
            # Get student fees with proper validation
            student_fees = StudentFee.objects.select_for_update().filter(
                id__in=fee_ids,
                student=user,
                status__in=['pending', 'partial', 'overdue']
            ).select_related('fee_type')
            
            # Validate all requested fees exist and belong to user
            if len(student_fees) != len(fee_ids):
                invalid_fees = set(fee_ids) - set(fee.id for fee in student_fees)
                logger.error(f"Invalid fee IDs for user {user.id}: {invalid_fees}")
                return Response({
                    'error': 'Some fees are invalid, already paid, or do not belong to you',
                    'invalid_fee_ids': list(invalid_fees)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Build fee amounts mapping and validate
            fee_amounts = {}
            calculated_total = Decimal('0.00')
            validation_errors = []
            
            for fee_data in validated_data['fees']:
                fee_id = int(fee_data['id'])
                amount = Decimal(str(fee_data['amount']))
                fee_amounts[fee_id] = amount
                calculated_total += amount
                
                # Find corresponding student fee
                student_fee = next((f for f in student_fees if f.id == fee_id), None)
                if student_fee:
                    if amount > student_fee.remaining_balance:
                        validation_errors.append({
                            'fee_id': fee_id,
                            'fee_name': student_fee.fee_type.name,
                            'error': f'Payment amount {amount} exceeds remaining balance {student_fee.remaining_balance}'
                        })
                    elif amount <= 0:
                        validation_errors.append({
                            'fee_id': fee_id,
                            'fee_name': student_fee.fee_type.name,
                            'error': 'Payment amount must be greater than zero'
                        })
            
            # Check for validation errors
            if validation_errors:
                logger.error(f"Fee amount validation errors for user {user.id}: {validation_errors}")
                return Response({
                    'error': 'Invalid payment amounts',
                    'validation_errors': validation_errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate total amount
            if abs(calculated_total - validated_data['total_amount']) > Decimal('0.01'):
                logger.error(f"Total amount mismatch: calculated {calculated_total}, provided {validated_data['total_amount']}")
                return Response({
                    'error': 'Total amount mismatch',
                    'calculated_total': str(calculated_total),
                    'provided_total': str(validated_data['total_amount'])
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create payments for each fee
            created_payments = []
            payment_date = timezone.now()
            
            for student_fee in student_fees:
                payment_amount = fee_amounts[student_fee.id]
                
                payment = Payment.objects.create(
                    student=user,
                    fee=student_fee,
                    payment_provider=payment_provider,
                    amount=payment_amount,
                    transaction_reference=validated_data.get('transaction_reference', ''),
                    payment_date=payment_date,
                    sender_name=validated_data.get('sender_name', ''),
                    sender_phone=validated_data.get('sender_phone', ''),
                    transfer_notes=validated_data.get('transfer_notes', ''),
                    status='pending'
                )
                created_payments.append(payment)
                logger.info(f"Created payment {payment.id} for fee {student_fee.id} with amount {payment_amount}")
            
            # Prepare response data
            payment_serializer = PaymentSerializer(created_payments, many=True)
            
            response_data = {
                'success': True,
                'message': 'Payment submitted successfully. Awaiting verification.',
                'payment_count': len(created_payments),
                'total_amount': str(calculated_total),
                'payment_provider': payment_provider.name,
                'transaction_reference': validated_data.get('transaction_reference', ''),
                'payments': payment_serializer.data,
                'created_at': payment_date.isoformat()
            }
            
            logger.info(f"Successfully created {len(created_payments)} payments for user {user.id}")
            return Response(response_data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Unexpected error creating payment for user {user.id}: {str(e)}")
        return Response({
            'error': 'Payment creation failed',
            'detail': 'An unexpected error occurred. Please try again or contact support.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outstanding_fees(request):
    """
    Get all outstanding fees for payment with enhanced mobile support
    """
    user = request.user
    logger.info(f"Outstanding fees request from user {user.id}")
    
    try:
        # Get outstanding fees
        outstanding_fees = StudentFee.objects.filter(
            student=user,
            status__in=['pending', 'partial', 'overdue']
        ).select_related('fee_type').order_by('due_date', 'fee_type__name')
        
        # Calculate totals
        total_outstanding = sum(fee.remaining_balance for fee in outstanding_fees)
        overdue_count = sum(1 for fee in outstanding_fees if fee.due_date and fee.due_date < timezone.now().date())
        overdue_amount = sum(fee.remaining_balance for fee in outstanding_fees if fee.due_date and fee.due_date < timezone.now().date())
        
        # Serialize fees
        serializer = StudentFeeSerializer(outstanding_fees, many=True)
        
        response_data = {
            'success': True,
            'outstanding_fees': serializer.data,
            'summary': {
                'total_outstanding': str(total_outstanding),
                'total_count': len(outstanding_fees),
                'overdue_count': overdue_count,
                'overdue_amount': str(overdue_amount),
                'pending_count': len([f for f in outstanding_fees if f.status == 'pending']),
                'partial_count': len([f for f in outstanding_fees if f.status == 'partial'])
            }
        }
        
        logger.info(f"Retrieved {len(outstanding_fees)} outstanding fees for user {user.id}")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving outstanding fees for user {user.id}: {str(e)}")
        return Response({
            'error': 'Failed to retrieve outstanding fees',
            'detail': 'An error occurred while fetching your outstanding fees.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_statistics(request):
    """
    Get comprehensive payment statistics for the authenticated student
    """
    user = request.user
    logger.info(f"Payment statistics request from user {user.id}")
    
    try:
        # Get date ranges
        now = timezone.now()
        current_year = now.year
        current_month = now.month
        twelve_months_ago = now - timedelta(days=365)
        thirty_days_ago = now - timedelta(days=30)
        
        # Total payments made (verified only)
        total_payments = Payment.objects.filter(
            student=user,
            status='verified'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Payments by status with amounts
        payment_stats = Payment.objects.filter(student=user).values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Recent payments (last 30 days)
        recent_payments_count = Payment.objects.filter(
            student=user,
            payment_date__gte=thirty_days_ago
        ).count()
        
        recent_payments_amount = Payment.objects.filter(
            student=user,
            status='verified',
            verified_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Monthly payment summary (last 12 months)
        monthly_payments = Payment.objects.filter(
            student=user,
            status='verified',
            verified_at__gte=twelve_months_ago
        ).extra({
            'month': "strftime('%Y-%m', verified_at)"
        }).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        # Payment provider usage
        provider_stats = Payment.objects.filter(
            student=user,
            status='verified'
        ).select_related('payment_provider').values(
            'payment_provider__name'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')
        
        # Current year statistics
        current_year_payments = Payment.objects.filter(
            student=user,
            status='verified',
            verified_at__year=current_year
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # Format response data
        payment_counts = {}
        payment_amounts = {}
        for stat in payment_stats:
            payment_counts[stat['status']] = stat['count']
            payment_amounts[stat['status']] = str(stat['total_amount'] or Decimal('0.00'))
        
        response_data = {
            'success': True,
            'summary': {
                'total_payments': str(total_payments),
                'total_transactions': Payment.objects.filter(student=user).count(),
                'recent_payments_count': recent_payments_count,
                'recent_payments_amount': str(recent_payments_amount)
            },
            'payment_counts': payment_counts,
            'payment_amounts': payment_amounts,
            'current_year': {
                'total_amount': str(current_year_payments['total'] or Decimal('0.00')),
                'transaction_count': current_year_payments['count'] or 0,
                'year': current_year
            },
            'monthly_summary': [
                {
                    'month': item['month'],
                    'total': str(item['total']),
                    'count': item['count']
                } for item in monthly_payments
            ],
            'provider_usage': [
                {
                    'provider': item['payment_provider__name'],
                    'count': item['count'],
                    'total_amount': str(item['total_amount'])
                } for item in provider_stats
            ]
        }
        
        logger.info(f"Retrieved payment statistics for user {user.id}")
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving payment statistics for user {user.id}: {str(e)}")
        return Response({
            'error': 'Failed to retrieve payment statistics',
            'detail': 'An error occurred while fetching your payment statistics.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_receipt(request, payment_id):
    """
    View payment receipt as PDF with enhanced error handling
    """
    user = request.user
    logger.info(f"Receipt view request from user {user.id} for payment {payment_id}")
    
    try:
        # Validate payment exists and belongs to user
        payment = get_object_or_404(
            Payment.objects.select_related('fee__fee_type', 'payment_provider'),
            id=payment_id,
            student=user,
            status='verified'
        )
        
        logger.info(f"Generating PDF receipt for payment {payment.id}")
        
        # Generate PDF receipt
        pdf_content = generate_receipt_pdf(payment)
        
        if not pdf_content:
            logger.error(f"Failed to generate PDF for payment {payment.id}")
            return Response({
                'error': 'Receipt generation failed',
                'detail': 'Unable to generate receipt PDF. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="receipt_{payment.id}.pdf"'
        response['X-Payment-ID'] = str(payment.id)
        response['X-Payment-Amount'] = str(payment.amount)
        
        logger.info(f"Successfully generated receipt for payment {payment.id}")
        return response
        
    except Payment.DoesNotExist:
        logger.warning(f"Payment {payment_id} not found for user {user.id}")
        return Response({
            'error': 'Payment not found',
            'detail': 'The requested payment receipt was not found or you do not have permission to view it.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error generating receipt for payment {payment_id}, user {user.id}: {str(e)}")
        return Response({
            'error': 'Receipt generation failed',
            'detail': 'An unexpected error occurred while generating the receipt.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_receipt(request, payment_id):
    """
    Download payment receipt as PDF with enhanced error handling
    """
    user = request.user
    logger.info(f"Receipt download request from user {user.id} for payment {payment_id}")
    
    try:
        # Validate payment exists and belongs to user
        payment = get_object_or_404(
            Payment.objects.select_related('fee__fee_type', 'payment_provider'),
            id=payment_id,
            student=user,
            status='verified'
        )
        
        logger.info(f"Generating PDF receipt for download - payment {payment.id}")
        
        # Generate PDF receipt
        pdf_content = generate_receipt_pdf(payment)
        
        if not pdf_content:
            logger.error(f"Failed to generate PDF for payment {payment.id}")
            return Response({
                'error': 'Receipt generation failed',
                'detail': 'Unable to generate receipt PDF. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Format filename with payment details
        filename = f"receipt_{payment.id}_{payment.payment_date.strftime('%Y%m%d')}.pdf"
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['X-Payment-ID'] = str(payment.id)
        response['X-Payment-Amount'] = str(payment.amount)
        response['X-Payment-Date'] = payment.payment_date.isoformat()
        
        logger.info(f"Successfully generated receipt download for payment {payment.id}")
        return response
        
    except Payment.DoesNotExist:
        logger.warning(f"Payment {payment_id} not found for user {user.id}")
        return Response({
            'error': 'Payment not found',
            'detail': 'The requested payment receipt was not found or you do not have permission to download it.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error downloading receipt for payment {payment_id}, user {user.id}: {str(e)}")
        return Response({
            'error': 'Receipt download failed',
            'detail': 'An unexpected error occurred while downloading the receipt.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)