from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import datetime, timedelta
from ..models import FeeType, StudentFee, PaymentProvider, Payment, PaymentReceipt, FinancialReport
from .serializers import (
    FeeTypeSerializer, StudentFeeSerializer, PaymentProviderSerializer,
    PaymentSerializer, PaymentCreateSerializer, PaymentReceiptSerializer,
    FinancialSummarySerializer, FinancialReportSerializer
)
from ..views import generate_receipt_pdf
import logging

logger = logging.getLogger(__name__)

# Financial API Views
# Add your financial-related API endpoints here

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_summary(request):
    """
    Get comprehensive financial summary for authenticated student
    """
    user = request.user
    
    # Get all fees for the student
    student_fees = StudentFee.objects.filter(student=user).select_related('fee_type')
    
    # Calculate totals
    total_fees = student_fees.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate pending payments (unpaid and partially paid fees)
    pending_fees = student_fees.exclude(status='paid')
    pending_payments = sum(fee.remaining_balance for fee in pending_fees)
    
    # Calculate paid this semester (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    paid_this_semester = Payment.objects.filter(
        student=user,
        status='verified',
        verified_at__gte=six_months_ago
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Count overdue fees
    overdue_count = student_fees.filter(
        due_date__lt=timezone.now().date(),
        status__in=['unpaid', 'partially_paid']
    ).count()
    
    # Get recent transactions (last 10)
    recent_transactions = Payment.objects.filter(
        student=user
    ).select_related('fee', 'payment_provider', 'verified_by').order_by('-created_at')[:10]
    
    # Get fee breakdown
    fee_breakdown = student_fees.order_by('-created_at')
    
    summary_data = {
        'total_fees': total_fees,
        'pending_payments': pending_payments,
        'paid_this_semester': paid_this_semester,
        'overdue_count': overdue_count,
        'recent_transactions': recent_transactions,
        'fee_breakdown': fee_breakdown
    }
    
    serializer = FinancialSummarySerializer(summary_data)
    return Response(serializer.data)


class StudentFeeListView(generics.ListAPIView):
    """
    List all fees for the authenticated student
    """
    serializer_class = StudentFeeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = StudentFee.objects.filter(
            student=self.request.user
        ).select_related('fee_type').order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by fee type
        fee_type = self.request.query_params.get('fee_type')
        if fee_type:
            queryset = queryset.filter(fee_type_id=fee_type)
        
        # Filter overdue fees
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['unpaid', 'partially_paid']
            )
        
        return queryset


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
    Create a new payment for selected fees
    """
    serializer = PaymentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        validated_data = serializer.validated_data
        
        # Get payment provider
        payment_provider = get_object_or_404(
            PaymentProvider, 
            id=validated_data['payment_provider_id'], 
            is_active=True
        )
        
        # Validate fees belong to the user and calculate total
        fee_ids = [fee_data['id'] for fee_data in validated_data['fees']]
        student_fees = StudentFee.objects.filter(
            id__in=fee_ids,
            student=user,
            status__in=['unpaid', 'partially_paid']
        )
        
        if len(student_fees) != len(fee_ids):
            return Response({
                'error': 'Some fees are invalid or already paid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate and validate total amount
        calculated_total = Decimal('0.00')
        fee_amounts = {}
        
        for fee_data in validated_data['fees']:
            fee_id = fee_data['id']
            amount = Decimal(fee_data['amount'])
            fee_amounts[int(fee_id)] = amount
            calculated_total += amount
        
        if calculated_total != validated_data['total_amount']:
            return Response({
                'error': 'Total amount mismatch'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payments for each fee
        created_payments = []
        
        for student_fee in student_fees:
            payment_amount = fee_amounts[student_fee.id]
            
            # Validate payment amount doesn't exceed remaining balance
            if payment_amount > student_fee.remaining_balance:
                return Response({
                    'error': f'Payment amount for {student_fee.fee_type.name} exceeds remaining balance'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            payment = Payment.objects.create(
                student=user,
                fee=student_fee,
                payment_provider=payment_provider,
                amount=payment_amount,
                transaction_reference=validated_data['transaction_reference'],
                payment_date=timezone.now().date(),
                sender_name=validated_data.get('sender_name', ''),
                sender_phone=validated_data.get('sender_phone', ''),
                transfer_notes=validated_data.get('transfer_notes', ''),
                status='pending'
            )
            created_payments.append(payment)
        
        # Serialize and return created payments
        payment_serializer = PaymentSerializer(created_payments, many=True)
        
        return Response({
            'message': 'Payment submitted successfully. Awaiting verification.',
            'payments': payment_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outstanding_fees(request):
    """
    Get all outstanding fees for payment
    """
    user = request.user
    
    outstanding_fees = StudentFee.objects.filter(
        student=user,
        status__in=['unpaid', 'partially_paid']
    ).select_related('fee_type').order_by('due_date')
    
    serializer = StudentFeeSerializer(outstanding_fees, many=True)
    
    return Response({
        'outstanding_fees': serializer.data,
        'total_outstanding': sum(fee.remaining_balance for fee in outstanding_fees)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_statistics(request):
    """
    Get payment statistics for the authenticated student
    """
    user = request.user
    
    # Total payments made
    total_payments = Payment.objects.filter(
        student=user,
        status='verified'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Payments by status
    payment_counts = Payment.objects.filter(student=user).values('status').annotate(
        count=Count('id')
    )
    
    # Monthly payment summary (last 12 months)
    twelve_months_ago = timezone.now() - timedelta(days=365)
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
    
    return Response({
        'total_payments': total_payments,
        'payment_counts': {item['status']: item['count'] for item in payment_counts},
        'monthly_summary': list(monthly_payments)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_receipt(request, payment_id):
    """
    View payment receipt as PDF
    """
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user,
        status='verified'
    )
    
    # Generate PDF receipt
    pdf_content = generate_receipt_pdf(payment)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{payment.id}.pdf"'
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_receipt(request, payment_id):
    """
    Download payment receipt as PDF
    """
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        student=request.user,
        status='verified'
    )
    
    # Generate PDF receipt
    pdf_content = generate_receipt_pdf(payment)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'
    
    return response