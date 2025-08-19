from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.http import HttpResponse, Http404
from decimal import Decimal
from .models import StudentFee, Payment, PaymentProvider, PaymentReceipt
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO


class FinancialDashboardView(LoginRequiredMixin, TemplateView):
    """Financial dashboard view"""
    template_name = 'financial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get student fees
        student_fees = StudentFee.objects.filter(student=user)
        
        # Calculate total fees
        total_fees = student_fees.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate pending payments (fees that are not fully paid)
        pending_fees = student_fees.exclude(status='paid')
        pending_payments = sum(fee.remaining_balance for fee in pending_fees)
        
        # Calculate paid this semester (current year)
        current_year = timezone.now().year
        paid_this_semester = Payment.objects.filter(
            student=user,
            status='verified',
            payment_date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Get recent transactions (last 5 verified payments)
        recent_transactions = Payment.objects.filter(
            student=user,
            status='verified'
        ).order_by('-payment_date')[:5]
        
        # Format transactions for display
        formatted_transactions = []
        for payment in recent_transactions:
            formatted_transactions.append({
                'description': f"{payment.fee.fee_type.name} Payment",
                'amount': payment.amount,
                'date': payment.payment_date.strftime('%B %d, %Y'),
                'reference': payment.transaction_reference,
                'payment_id': payment.id
            })
        
        # Get fee breakdown for current academic year
        fee_breakdown = []
        for fee in student_fees.filter(created_at__year=current_year):
            fee_breakdown.append({
                'name': fee.fee_type.name,
                'amount': fee.amount,
                'paid': fee.amount_paid,
                'remaining': fee.remaining_balance,
                'status': fee.status,
                'due_date': fee.due_date
            })
        
        context.update({
            'total_fees': total_fees,
            'pending_payments': pending_payments,
            'paid_this_semester': paid_this_semester,
            'recent_transactions': formatted_transactions,
            'fee_breakdown': fee_breakdown,
            'overdue_count': pending_fees.filter(due_date__lt=timezone.now().date()).count(),
        })
        
        return context


class PayFeesView(LoginRequiredMixin, TemplateView):
    """Pay fees view"""
    template_name = 'financial/pay_fees.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get outstanding fees
        outstanding_fees_qs = StudentFee.objects.filter(
            student=user
        ).exclude(status='paid')
        
        # Calculate total outstanding amount
        outstanding_amount = sum(fee.remaining_balance for fee in outstanding_fees_qs)
        
        # Get fee breakdown
        fee_breakdown = []
        for fee in outstanding_fees_qs:
            fee_breakdown.append({
                'id': fee.id,
                'name': fee.fee_type.name,
                'amount': fee.amount,
                'paid': fee.amount_paid,
                'remaining': fee.remaining_balance,
                'due_date': fee.due_date,
                'status': fee.status,
                'is_overdue': fee.is_overdue
            })
        
        # Get available payment providers
        payment_providers = PaymentProvider.objects.filter(is_active=True)
        
        context.update({
            'outstanding_fees': outstanding_amount,
            'fee_breakdown': fee_breakdown,
            'payment_providers': payment_providers,
            'has_outstanding_fees': outstanding_amount > 0,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Process payment submission"""
        user = request.user
        
        try:
            # Get form data
            amount = Decimal(request.POST.get('amount', '0'))
            payment_provider_id = request.POST.get('payment_method')  # This should be payment_provider_id
            transaction_reference = request.POST.get('transaction_reference', '')
            selected_fees = request.POST.getlist('selected_fees')
            
            # Get transfer details
            sender_name = request.POST.get('sender_name', '')
            sender_phone = request.POST.get('sender_phone', '')
            transfer_notes = request.POST.get('transfer_notes', '')
            
            # Validate amount
            if amount <= 0:
                messages.error(request, 'Please enter a valid payment amount.')
                return redirect('financial:pay_fees')
            
            # Validate payment provider
            if not payment_provider_id:
                messages.error(request, 'Please select a payment method.')
                return redirect('financial:pay_fees')
            
            # Get payment provider
            try:
                payment_provider = PaymentProvider.objects.get(id=payment_provider_id)
            except PaymentProvider.DoesNotExist:
                messages.error(request, 'Invalid payment method selected.')
                return redirect('financial:pay_fees')
            
            # Validate transfer details (optional but recommended)
            # Note: These fields are now optional to allow for different payment types
            
            # Validate selected fees (only if there are outstanding fees)
            outstanding_fees_qs = StudentFee.objects.filter(
                student=user
            ).exclude(status='paid')
            
            if outstanding_fees_qs.exists() and not selected_fees:
                messages.error(request, 'Please select at least one fee to pay.')
                return redirect('financial:pay_fees')
            
            # If no outstanding fees exist, redirect with appropriate message
            if not outstanding_fees_qs.exists():
                messages.info(request, 'You have no outstanding fees to pay.')
                return redirect('financial:dashboard')
            
            # Calculate total amount for selected fees
            selected_fee_objects = StudentFee.objects.filter(id__in=selected_fees, student=user)
            total_selected_amount = sum(fee.remaining_balance for fee in selected_fee_objects)
            
            # Validate that payment amount doesn't exceed selected fees total
            if amount > total_selected_amount:
                messages.error(request, f'Payment amount (${amount}) cannot exceed the total of selected fees (${total_selected_amount}).')
                return redirect('financial:pay_fees')
            
            # Create payment records for selected fees
            payment_ids = []
            remaining_payment = amount
            
            for fee_id in selected_fees:
                try:
                    fee = StudentFee.objects.get(id=fee_id, student=user)
                    
                    # Calculate how much to allocate to this fee
                    fee_remaining = fee.remaining_balance
                    payment_for_this_fee = min(remaining_payment, fee_remaining)
                    
                    if payment_for_this_fee > 0:
                        # Create payment record with the allocated amount
                        payment = Payment.objects.create(
                            student=user,
                            fee=fee,
                            payment_provider=payment_provider,
                            amount=payment_for_this_fee,  # Use the allocated amount
                            transaction_reference=transaction_reference,
                            payment_date=timezone.now(),
                            status='pending',
                            sender_name=sender_name,
                            sender_phone=sender_phone,
                            transfer_notes=transfer_notes
                        )
                        payment_ids.append(payment.id)
                        remaining_payment -= payment_for_this_fee
                        
                        # Stop if we've allocated all the payment amount
                        if remaining_payment <= 0:
                            break
                            
                except StudentFee.DoesNotExist:
                    continue
            
            if payment_ids:
                messages.success(request, f'Payment(s) submitted successfully. Payment IDs: {", ".join(map(str, payment_ids))}')
            else:
                messages.error(request, 'No valid fees were selected for payment.')
            
            return redirect('financial:dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred while processing your payment: {str(e)}')
            return redirect('financial:pay_fees')


class PaymentHistoryView(LoginRequiredMixin, TemplateView):
    """View all payment history including rejected payments"""
    template_name = 'financial/payment_history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all payments for the student
        all_payments = Payment.objects.filter(
            student=user
        ).select_related('fee__fee_type', 'payment_provider', 'verified_by').order_by('-created_at')
        
        # Format payments for display
        formatted_payments = []
        for payment in all_payments:
            formatted_payments.append({
                'id': payment.id,
                'description': f"{payment.fee.fee_type.name} Payment" if payment.fee else "General Payment",
                'amount': payment.amount,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'payment_date': payment.payment_date,
                'created_at': payment.created_at,
                'transaction_reference': payment.transaction_reference,
                'payment_method': payment.payment_provider.name if payment.payment_provider else 'Bank Transfer',
                'verification_notes': payment.verification_notes,
                'verified_by': payment.verified_by.get_full_name() if payment.verified_by else None,
                'verified_at': payment.verified_at,
                'can_view_receipt': payment.status == 'verified'
            })
        
        # Get payment statistics
        total_payments = all_payments.count()
        verified_payments = all_payments.filter(status='verified').count()
        pending_payments = all_payments.filter(status='pending').count()
        rejected_payments = all_payments.filter(status='rejected').count()
        
        # Convert datetime objects to strings for JSON serialization
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        
        payments_json = json.dumps(formatted_payments, cls=DjangoJSONEncoder)
        
        context.update({
            'payments': formatted_payments,
            'payments_json': payments_json,
            'total_payments': total_payments,
            'verified_payments': verified_payments,
            'pending_payments': pending_payments,
            'rejected_payments': rejected_payments,
        })
        
        return context


@login_required
def view_receipt(request, payment_id):
    """View payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user, status='verified')
    
    # Get or create receipt
    receipt, created = PaymentReceipt.objects.get_or_create(
        payment=payment,
        defaults={
            'generated_by': request.user
        }
    )
    
    context = {
        'payment': payment,
        'receipt': receipt,
    }
    
    return render(request, 'financial/receipt.html', context)


@login_required
def download_receipt(request, payment_id):
    """Download payment receipt as PDF"""
    payment = get_object_or_404(Payment, id=payment_id, student=request.user, status='verified')
    
    # Get or create receipt
    receipt, created = PaymentReceipt.objects.get_or_create(
        payment=payment,
        defaults={
            'generated_by': request.user
        }
    )
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    title = Paragraph("PAYMENT RECEIPT", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # University Info
    university_info = Paragraph(
        "<b>University Services Portal</b><br/>"
        "Financial Services Department<br/>"
        "123 University Avenue<br/>"
        "University City, UC 12345",
        styles['Normal']
    )
    story.append(university_info)
    story.append(Spacer(1, 20))
    
    # Receipt Details
    receipt_data = [
        ['Receipt Number:', receipt.receipt_number],
        ['Date:', payment.payment_date.strftime('%B %d, %Y')],
        ['Student ID:', payment.student.university_id],
        ['Student Name:', payment.student.get_full_name()],
        ['Fee Type:', payment.fee.fee_type.name],
        ['Amount Paid:', f'${payment.amount}'],
        ['Payment Method:', payment.payment_provider.name],
        ['Transaction Reference:', payment.transaction_reference or 'N/A'],
        ['Status:', 'Verified'],
    ]
    
    receipt_table = Table(receipt_data, colWidths=[2*72, 3*72])
    receipt_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    
    story.append(receipt_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer = Paragraph(
        "<i>This is an official receipt for payment made to the University Services Portal. "
        "Please keep this receipt for your records.</i>",
        styles['Normal']
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Return PDF response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
    
    return response
