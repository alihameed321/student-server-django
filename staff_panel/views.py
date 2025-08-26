from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum
from django.db import models


class StaffDashboardView(LoginRequiredMixin, TemplateView):
    """Staff dashboard view"""
    template_name = 'staff_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create today's dashboard stats
        from .models import DashboardStats, StaffActivity
        from accounts.models import User
        from student_portal.models import ServiceRequest, SupportTicket
        from financial.models import Payment
        
        # Get today's stats
        stats = DashboardStats.get_or_create_today()
        
        # Get recent activities (last 10)
        recent_activities = StaffActivity.objects.select_related(
            'staff_member', 'target_user'
        ).order_by('-timestamp')[:10]
        
        # Calculate real-time stats
        pending_requests = ServiceRequest.objects.filter(
            status__in=['pending', 'in_review']
        ).count()
        
        open_support_tickets = SupportTicket.objects.filter(
            status__in=['open', 'in_progress']
        ).count()
        
        # Add comprehensive dashboard statistics
        context.update({
            # Student statistics
            'total_students': stats.total_students,
            'new_students_today': stats.new_students_today,
            'active_students': stats.active_students,
            
            # Request statistics
            'pending_requests': pending_requests,
            'approved_requests_today': stats.approved_requests_today,
            'rejected_requests_today': stats.rejected_requests_today,
            
            # Financial statistics
            'total_fees_collected_today': stats.total_fees_collected_today,
            'verified_payments_today': stats.verified_payments_today,
            'pending_payments': stats.pending_payments,
            
            # Support statistics
            'open_support_tickets': open_support_tickets,
            'resolved_tickets_today': stats.resolved_tickets_today,
            
            # Activity data
            'recent_activities': recent_activities,
        })
        
        return context


@login_required
def staff_dashboard(request):
    """Staff dashboard function-based view"""
    context = {
        'pending_requests': 0,
        'total_students': 0,
        'recent_activities': [],
    }
    return render(request, 'staff_panel/dashboard.html', context)


# Request Management Views
class RequestManagementView(LoginRequiredMixin, TemplateView):
    """Manage student service requests"""
    template_name = 'staff_panel/request_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from student_portal.models import ServiceRequest
        
        # Get all requests with filters
        status_filter = self.request.GET.get('status', 'all')
        requests = ServiceRequest.objects.select_related('student').order_by('-created_at')
        
        if status_filter != 'all':
            requests = requests.filter(status=status_filter)
            
        context.update({
            'requests': requests[:50],  # Limit to 50 for performance
            'status_filter': status_filter,
            'status_choices': ServiceRequest.STATUS_CHOICES,
        })
        return context


class RequestDetailView(LoginRequiredMixin, TemplateView):
    """View detailed information about a specific request"""
    template_name = 'staff_panel/request_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from student_portal.models import ServiceRequest
        
        request_id = kwargs.get('request_id')
        service_request = ServiceRequest.objects.select_related('student').get(id=request_id)
        
        context.update({
            'service_request': service_request,
        })
        return context


@login_required
def approve_request(request, request_id):
    """Approve a service request"""
    from student_portal.models import ServiceRequest
    from .models import StaffActivity
    
    try:
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check if request can be approved
        if service_request.status not in ['pending', 'in_review']:
            return JsonResponse({'status': 'error', 'message': 'Request cannot be approved in its current status'})
        
        service_request.status = 'approved'
        service_request.processed_by = request.user
        service_request.processed_at = timezone.now()
        service_request.save()
        
        # Log staff activity
        StaffActivity.objects.create(
            staff_member=request.user,
            activity_type='request_approved',
            description=f'Approved {service_request.get_request_type_display()} request for {service_request.student.get_full_name()}',
            target_user=service_request.student
        )
        
        messages.success(request, f'Request #{request_id} has been approved successfully.')
        return JsonResponse({'status': 'success', 'message': 'Request approved'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error approving request: {str(e)}'})


@login_required
def reject_request(request, request_id):
    """Reject a service request"""
    from student_portal.models import ServiceRequest
    from .models import StaffActivity
    
    try:
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check if request can be rejected
        if service_request.status not in ['pending', 'in_review']:
            return JsonResponse({'status': 'error', 'message': 'Request cannot be rejected in its current status'})
        
        service_request.status = 'rejected'
        service_request.processed_by = request.user
        service_request.processed_at = timezone.now()
        service_request.save()
        
        # Log staff activity
        StaffActivity.objects.create(
            staff_member=request.user,
            activity_type='request_rejected',
            description=f'Rejected {service_request.get_request_type_display()} request for {service_request.student.get_full_name()}',
            target_user=service_request.student
        )
        
        messages.success(request, f'Request #{request_id} has been rejected.')
        return JsonResponse({'status': 'success', 'message': 'Request rejected'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error rejecting request: {str(e)}'})


# Financial Management Views
class FinancialManagementView(LoginRequiredMixin, TemplateView):
    """Financial overview and management"""
    template_name = 'staff_panel/financial_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import Payment, StudentFee, FeeType
        from accounts.models import User
        from decimal import Decimal
        from datetime import datetime, timedelta
        from django.db.models import Sum
        from django.utils import timezone
        
        # Financial statistics
        total_revenue = Payment.objects.filter(status='verified').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        pending_payments_count = Payment.objects.filter(status='pending').count()
        pending_payments_amount = Payment.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        verified_today = Payment.objects.filter(
            status='verified',
            verified_at__date=timezone.now().date()
        ).count()
        
        revenue_today = Payment.objects.filter(
            status='verified',
            verified_at__date=timezone.now().date()
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Outstanding fees
        outstanding_fees = StudentFee.objects.exclude(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Recent transactions (last 10 verified payments)
        recent_transactions = Payment.objects.filter(
            status='verified'
        ).select_related('student', 'fee', 'fee__fee_type').order_by('-verified_at')[:10]
        
        # Payment trends (last 7 days)
        payment_trends = []
        daily_amounts = []
        
        # First pass: collect all amounts
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            daily_revenue = Payment.objects.filter(
                status='verified',
                verified_at__date=date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            daily_amounts.append(float(daily_revenue))
        
        # Calculate max for percentage calculation
        max_amount = max(daily_amounts) if daily_amounts and max(daily_amounts) > 0 else 1
        
        # Second pass: create trends with percentages
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            amount = daily_amounts[i]
            percentage = (amount / max_amount) * 100 if max_amount > 0 else 0
            
            payment_trends.append({
                'date': date.strftime('%m/%d'),
                'amount': amount,
                'percentage': round(percentage, 1)
            })
        payment_trends.reverse()
        
        # Fee type breakdown
        fee_breakdown = []
        fee_types = FeeType.objects.all()
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']  # Blue, Green, Yellow, Red, Purple, Cyan
        
        for i, fee_type in enumerate(fee_types):
            total_fees = StudentFee.objects.filter(fee_type=fee_type).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            paid_fees = Payment.objects.filter(
                fee__fee_type=fee_type,
                status='verified'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            fee_count = StudentFee.objects.filter(fee_type=fee_type).count()
            
            fee_breakdown.append({
                'type': fee_type.name,
                'name': fee_type.name,  # Keep for backward compatibility
                'total': total_fees,
                'paid': paid_fees,
                'outstanding': total_fees - paid_fees,
                'count': fee_count,
                'color': colors[i % len(colors)]
            })
        
        # Student payment status
        total_students = User.objects.filter(user_type='student').count()
        students_with_outstanding = StudentFee.objects.exclude(
            status='paid'
        ).values('student').distinct().count()
        
        context.update({
            'total_revenue': total_revenue,
            'pending_payments_count': pending_payments_count,
            'pending_payments_amount': pending_payments_amount,
            'verified_today': verified_today,
            'revenue_today': revenue_today,
            'outstanding_fees': outstanding_fees,
            'recent_transactions': recent_transactions,
            'payment_trends': payment_trends,
            'fee_breakdown': fee_breakdown,
            'total_students': total_students,
            'students_with_outstanding': students_with_outstanding,
        })
        return context


class PaymentVerificationView(LoginRequiredMixin, TemplateView):
    """Verify student payments"""
    template_name = 'staff_panel/payment_verification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import Payment
        from django.core.paginator import Paginator
        
        # Get search query
        search_query = self.request.GET.get('search', '')
        
        # Base queryset
        pending_payments = Payment.objects.filter(
            status='pending'
        ).select_related('student')
        
        # Apply search filter
        if search_query:
            pending_payments = pending_payments.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(student__university_id__icontains=search_query) |
                Q(fee__fee_type__name__icontains=search_query) |
                Q(payment_provider__name__icontains=search_query) |
                Q(sender_name__icontains=search_query) |
                Q(transaction_reference__icontains=search_query)
            )
        
        # Order by creation date
        pending_payments = pending_payments.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(pending_payments, 10)  # 10 payments per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'pending_payments': page_obj,
            'search_query': search_query,
            'total_payments': paginator.count,
        })
        return context


@login_required
def verify_payment(request, payment_id):
    """Verify a payment via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        from financial.models import Payment
        from .models import StaffActivity
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        if payment.status != 'pending':
            # Provide more specific error messages based on current status
            if payment.status == 'verified':
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Payment #{payment_id} has already been verified by {payment.verified_by.get_full_name() if payment.verified_by else "another staff member"}.'
                })
            elif payment.status == 'rejected':
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Payment #{payment_id} has already been rejected by {payment.verified_by.get_full_name() if payment.verified_by else "another staff member"}.'
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Payment #{payment_id} is not available for processing (current status: {payment.get_status_display()}).'
                })
        
        # Verify the payment
        payment.verify_payment(request.user, "Verified by staff")
        
        # Log staff activity
        StaffActivity.objects.create(
            staff_member=request.user,
            activity_type='payment_verified',
            description=f'Verified payment of ${payment.amount} for {payment.student.get_full_name()}',
            target_user=payment.student
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Payment #{payment_id} verified successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error verifying payment: {str(e)}'})


@login_required
def reject_payment(request, payment_id):
    """Reject a payment via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        from financial.models import Payment
        from .models import StaffActivity
        import json
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        if payment.status != 'pending':
            # Provide more specific error messages based on current status
            if payment.status == 'verified':
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Payment #{payment_id} has already been verified by {payment.verified_by.get_full_name() if payment.verified_by else "another staff member"}.'
                })
            elif payment.status == 'rejected':
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Payment #{payment_id} has already been rejected by {payment.verified_by.get_full_name() if payment.verified_by else "another staff member"}.'
                })
            else:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Payment #{payment_id} is not available for processing (current status: {payment.get_status_display()}).'
                })
        
        # Get rejection reason from request
        data = json.loads(request.body) if request.body else {}
        reason = data.get('reason', 'Rejected by staff')
        
        # Reject the payment
        payment.reject_payment(request.user, reason)
        
        # Log staff activity
        StaffActivity.objects.create(
            staff_member=request.user,
            activity_type='payment_rejected',
            description=f'Rejected payment of ${payment.amount} for {payment.student.get_full_name()}',
            target_user=payment.student
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Payment #{payment_id} rejected successfully'
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error rejecting payment: {str(e)}'})


@login_required
def get_payment_details(request, payment_id):
    """Get payment details via AJAX"""
    try:
        from financial.models import Payment
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        return JsonResponse({
            'status': 'success',
            'payment': {
                'id': payment.id,
                'student_name': payment.student.get_full_name(),
                'student_id': payment.student.university_id,
                'fee_name': payment.fee.fee_type.name if payment.fee else 'General Payment',
                'fee_type': payment.fee.fee_type.name if payment.fee else 'N/A',
                'amount': float(payment.amount),
                'payment_method': payment.payment_provider.name if payment.payment_provider else 'Bank Transfer',
                'transaction_reference': payment.transaction_reference,
                'payment_date': payment.payment_date.strftime('%B %d, %Y at %I:%M %p'),
                'status': payment.get_status_display(),
                'verification_notes': payment.verification_notes or '',
                'verified_by': payment.verified_by.get_full_name() if payment.verified_by else None,
                'verified_at': payment.verified_at.strftime('%B %d, %Y at %I:%M %p') if payment.verified_at else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error fetching payment details: {str(e)}'})


class PendingPaymentsView(LoginRequiredMixin, TemplateView):
    """View all pending payments"""
    template_name = 'staff_panel/pending_payments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import Payment, StudentFee
        from datetime import datetime, timedelta
        from decimal import Decimal
        from django.utils import timezone
        
        # Get all pending fees (not payments)
        pending_fees = StudentFee.objects.filter(
            status__in=['pending', 'overdue', 'partial']
        ).select_related('student', 'fee_type').order_by('-due_date')
        
        # Calculate statistics
        total_pending = pending_fees.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Count unique students with pending fees
        student_count = pending_fees.values('student').distinct().count()
        
        # Calculate overdue and due soon counts
        today = timezone.now().date()
        due_soon_threshold = today + timedelta(days=7)  # Due within 7 days
        
        overdue_count = pending_fees.filter(due_date__lt=today).count()
        due_soon_count = pending_fees.filter(
            due_date__gte=today,
            due_date__lte=due_soon_threshold
        ).count()
        
        # Get fee types for filter dropdown
        from financial.models import FeeType
        fee_types = FeeType.objects.filter(is_active=True).order_by('name')
        
        context.update({
            'pending_payments': pending_fees,
            'payments': pending_fees,  # Keep for backward compatibility
            'total_pending': total_pending,
            'student_count': student_count,
            'overdue_count': overdue_count,
            'due_soon_count': due_soon_count,
            'fee_types': fee_types,
        })
        return context


class FeeManagementView(LoginRequiredMixin, TemplateView):
    """Manage student fees"""
    template_name = 'staff_panel/fee_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import StudentFee, Payment, FeeType
        from accounts.models import User
        from django.db.models import Sum, Count, Q
        from django.core.paginator import Paginator
        from decimal import Decimal
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '')
        category_filter = self.request.GET.get('category', '')
        page_number = self.request.GET.get('page', 1)
        
        # Base queryset
        fees_queryset = StudentFee.objects.select_related('student', 'fee_type').order_by('-due_date')
        
        # Apply search filter
        if search_query:
            fees_queryset = fees_queryset.filter(
                Q(student__first_name__icontains=search_query) |
                Q(student__last_name__icontains=search_query) |
                Q(student__university_id__icontains=search_query) |
                Q(fee_type__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Apply category filter
        if category_filter:
            fees_queryset = fees_queryset.filter(fee_type__name__icontains=category_filter)
        
        # Pagination
        paginator = Paginator(fees_queryset, 10)  # 10 fees per page
        fees_page = paginator.get_page(page_number)
        
        # Calculate statistics
        total_fees = StudentFee.objects.count()
        active_fees = StudentFee.objects.filter(status__in=['pending', 'partial']).count()
        
        # Total revenue from verified payments
        total_revenue = Payment.objects.filter(status='verified').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Total enrolled students
        enrolled_students = User.objects.filter(user_type='student').count()
        
        # Calculate fee category statistics
        fee_categories = {
            'tuition': StudentFee.objects.filter(fee_type__name__icontains='tuition').count(),
            'library': StudentFee.objects.filter(fee_type__name__icontains='library').count(),
            'lab': StudentFee.objects.filter(fee_type__name__icontains='lab').count(),
            'sports': StudentFee.objects.filter(fee_type__name__icontains='sports').count(),
            'other': StudentFee.objects.exclude(
                Q(fee_type__name__icontains='tuition') |
                Q(fee_type__name__icontains='library') |
                Q(fee_type__name__icontains='lab') |
                Q(fee_type__name__icontains='sports')
            ).count(),
        }
        
        # Get all fee types for category filter
        fee_types = FeeType.objects.filter(is_active=True).order_by('name')
        
        context.update({
            'fees': fees_page,
            'total_fees': total_fees,
            'active_fees': active_fees,
            'total_revenue': total_revenue,
            'enrolled_students': enrolled_students,
            'tuition_count': fee_categories['tuition'],
            'library_count': fee_categories['library'],
            'lab_count': fee_categories['lab'],
            'sports_count': fee_categories['sports'],
            'other_count': fee_categories['other'],
            'fee_types': fee_types,
            'search_query': search_query,
            'category_filter': category_filter,
            'has_previous': fees_page.has_previous(),
            'has_next': fees_page.has_next(),
            'page_number': fees_page.number,
            'total_pages': paginator.num_pages,
        })
        return context


class CreateFeeView(LoginRequiredMixin, TemplateView):
    """Create new fee"""
    template_name = 'staff_panel/create_fee.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        
        # Get all students for the dropdown
        students = User.objects.filter(user_type='student').order_by('first_name', 'last_name')
        
        context.update({
            'students': students,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        from financial.models import StudentFee, FeeType
        from accounts.models import User
        from .models import StaffActivity
        from decimal import Decimal
        from datetime import datetime
        
        # Get form data
        fee_name = request.POST.get('fee_name')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '')
        apply_to = request.POST.get('apply_to')
        
        if fee_name and amount and due_date:
            try:
                # Get or create fee type
                fee_type, created = FeeType.objects.get_or_create(
                    name=fee_name,
                    defaults={'description': description}
                )
                
                # Convert amount to decimal
                amount_decimal = Decimal(amount)
                
                # Apply fee to students
                if apply_to == 'all':
                    students = User.objects.filter(user_type='student')
                    for student in students:
                        StudentFee.objects.create(
                            student=student,
                            fee_type=fee_type,
                            amount=amount_decimal,
                            due_date=due_date,
                            description=description,
                            created_by=request.user
                        )
                elif apply_to == 'specific':
                    selected_student_ids = request.POST.getlist('selected_students')
                    if selected_student_ids:
                        students = User.objects.filter(id__in=selected_student_ids, user_type='student')
                        for student in students:
                            StudentFee.objects.create(
                                student=student,
                                fee_type=fee_type,
                                amount=amount_decimal,
                                due_date=due_date,
                                description=description,
                                created_by=request.user
                            )
                    else:
                        messages.error(request, 'Please select at least one student when applying to specific students.')
                        return self.get(request, *args, **kwargs)
                
                # Log staff activity
                StaffActivity.objects.create(
                    staff_member=request.user,
                    activity_type='fee_created',
                    description=f'Created fee: {fee_name} - ${amount}'
                )
                
                messages.success(request, 'Fee created successfully!')
                return redirect('staff_panel:fee_management')
                
            except Exception as e:
                messages.error(request, f'Error creating fee: {str(e)}')
                return self.get(request, *args, **kwargs)
        else:
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request, *args, **kwargs)


class EditFeeView(LoginRequiredMixin, TemplateView):
    """Edit existing fee"""
    template_name = 'staff_panel/edit_fee.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import StudentFee
        
        fee_id = kwargs.get('fee_id')
        try:
            fee = StudentFee.objects.get(id=fee_id)
            context['fee'] = fee
        except StudentFee.DoesNotExist:
            messages.error(self.request, 'Fee not found.')
        
        return context
    
    def post(self, request, *args, **kwargs):
        from financial.models import StudentFee
        from .models import StaffActivity
        from decimal import Decimal
        
        fee_id = kwargs.get('fee_id')
        
        try:
            fee = StudentFee.objects.get(id=fee_id)
            
            # Update fee fields
            fee.amount = Decimal(request.POST.get('amount', fee.amount))
            fee.due_date = request.POST.get('due_date', fee.due_date)
            fee.description = request.POST.get('description', fee.description)
            fee.save()
            
            # Log staff activity
            StaffActivity.objects.create(
                staff_member=request.user,
                activity_type='other',
                description=f'Updated fee: {fee.fee_type.name} - ${fee.amount}',
                target_user=fee.student
            )
            
            messages.success(request, 'Fee updated successfully!')
            return redirect('staff_panel:fee_management')
            
        except StudentFee.DoesNotExist:
            messages.error(request, 'Fee not found.')
            return redirect('staff_panel:fee_management')
        except Exception as e:
            messages.error(request, f'Error updating fee: {str(e)}')
            return self.get(request, *args, **kwargs)


# Student Management Views
class StudentManagementView(LoginRequiredMixin, TemplateView):
    """Manage students"""
    template_name = 'staff_panel/student_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        
        students = User.objects.filter(
            user_type='student'
        ).select_related('student_profile').order_by('-date_joined')
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            students = students.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(university_id__icontains=search_query) |
                models.Q(email__icontains=search_query)
            )
        
        context.update({
            'students': students[:100],  # Limit for performance
            'search_query': search_query,
        })
        return context


class StudentDetailView(LoginRequiredMixin, TemplateView):
    """View detailed student information"""
    template_name = 'staff_panel/student_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        
        student_id = kwargs.get('student_id')
        student = User.objects.select_related('student_profile').get(
            id=student_id, user_type='student'
        )
        
        context.update({
            'student': student,
        })
        return context


class AddStudentView(LoginRequiredMixin, TemplateView):
    """Add new student"""
    template_name = 'staff_panel/add_student.html'
    
    def post(self, request, *args, **kwargs):
        from accounts.models import User, StudentProfile
        from .models import StaffActivity
        from django.contrib.auth.hashers import make_password
        import random
        import string
        
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        university_id = request.POST.get('university_id')
        phone_number = request.POST.get('phone_number', '')
        date_of_birth = request.POST.get('date_of_birth')
        program = request.POST.get('program', '')
        year_of_study = request.POST.get('year_of_study', '')
        is_active = request.POST.get('is_active') == 'on'
        
        if first_name and last_name and email and university_id:
            try:
                # Check if university ID or email already exists
                if User.objects.filter(university_id=university_id).exists():
                    messages.error(request, 'A student with this University ID already exists.')
                    return self.get(request, *args, **kwargs)
                    
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'A user with this email already exists.')
                    return self.get(request, *args, **kwargs)
                
                # Generate username and password
                username = f"student_{university_id.lower()}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                # Create user
                student = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    university_id=university_id,
                    user_type='student',
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    date_of_birth=date_of_birth if date_of_birth else None,
                    major=program,  # program maps to major
                    academic_level=year_of_study,  # year_of_study maps to academic_level
                    is_active=is_active
                )
                
                # Handle profile picture upload
                if 'profile_picture' in request.FILES:
                    student.profile_picture = request.FILES['profile_picture']
                    student.save()
                
                # Create student profile
                StudentProfile.objects.create(
                    user=student,
                    student_id_number=university_id
                )
                
                # Log staff activity
                StaffActivity.objects.create(
                    staff_member=request.user,
                    activity_type='user_created',
                    target_user=student,
                    description=f'Created new student: {student.get_full_name()} ({university_id})'
                )
                
                messages.success(request, f'Student {student.get_full_name()} created successfully! Temporary password: {password}')
                return redirect('staff_panel:student_detail', student_id=student.id)
                
            except Exception as e:
                messages.error(request, f'Error creating student: {str(e)}')
                return self.get(request, *args, **kwargs)
        else:
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request, *args, **kwargs)


class StudentSearchView(LoginRequiredMixin, TemplateView):
    """Search students"""
    template_name = 'staff_panel/student_search.html'


class DeleteStudentView(LoginRequiredMixin, View):
    """Delete student"""
    
    def post(self, request, student_id, *args, **kwargs):
        from accounts.models import User
        from .models import StaffActivity
        
        try:
            student = get_object_or_404(User, id=student_id, user_type='student')
            student_name = student.get_full_name()
            student_university_id = student.university_id
            
            # Log staff activity before deletion
            StaffActivity.objects.create(
                staff_member=request.user,
                activity_type='user_deleted',
                description=f'Deleted student: {student_name} ({student_university_id})'
            )
            
            # Delete the student (this will cascade to StudentProfile)
            student.delete()
            
            messages.success(request, f'Student {student_name} has been deleted successfully.')
            
        except Exception as e:
            messages.error(request, f'Error deleting student: {str(e)}')
            
        return redirect('staff_panel:student_management')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        
        search_query = self.request.GET.get('q', '')
        students = []
        
        if search_query:
            students = User.objects.filter(
                user_type='student'
            ).filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(university_id__icontains=search_query) |
                models.Q(email__icontains=search_query)
            ).select_related('student_profile')[:20]
        
        context.update({
            'students': students,
            'search_query': search_query,
        })
        return context


class EditStudentView(LoginRequiredMixin, TemplateView):
    """Edit student information"""
    template_name = 'staff_panel/edit_student.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        
        student_id = kwargs.get('student_id')
        student = User.objects.select_related('student_profile').get(
            id=student_id, user_type='student'
        )
        
        context.update({
            'student': student,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        from accounts.models import User, StudentProfile
        from .models import StaffActivity
        
        student_id = kwargs.get('student_id')
        student = User.objects.select_related('student_profile').get(
            id=student_id, user_type='student'
        )
        
        # Update user fields
        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        student.email = request.POST.get('email', student.email)
        student.phone_number = request.POST.get('phone_number', student.phone_number)
        student.date_of_birth = request.POST.get('date_of_birth') or student.date_of_birth
        student.major = request.POST.get('program', student.major)  # program maps to major
        student.academic_level = request.POST.get('year_of_study', student.academic_level)  # year_of_study maps to academic_level
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            student.profile_picture = request.FILES['profile_picture']
        
        student.save()
        
        # Update student profile fields
        if hasattr(student, 'student_profile'):
            profile = student.student_profile
            profile.emergency_contact_name = request.POST.get('emergency_contact_name', profile.emergency_contact_name)
            profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', profile.emergency_contact_phone)
            profile.save()
        
        # Log staff activity
        StaffActivity.objects.create(
            staff_member=request.user,
            activity_type='user_modified',
            target_user=student,
            description=f'Updated student information for {student.get_full_name()}'
        )
        
        messages.success(request, f'Student {student.get_full_name()} updated successfully.')
        return redirect('staff_panel:student_detail', student_id=student.id)


# Announcement Management Views
class AnnouncementManagementView(LoginRequiredMixin, TemplateView):
    """Manage announcements"""
    template_name = 'staff_panel/announcement_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from notifications.models import Announcement
        
        announcements = Announcement.objects.order_by('-created_at')
        
        context.update({
            'announcements': announcements,
        })
        return context


class CreateAnnouncementView(LoginRequiredMixin, TemplateView):
    """Create new announcement"""
    template_name = 'staff_panel/create_announcement.html'
    
    def post(self, request, *args, **kwargs):
        from notifications.models import Announcement
        from .models import StaffActivity
        from django.contrib import messages
        from django.shortcuts import redirect
        
        title = request.POST.get('title')
        content = request.POST.get('content')
        priority = request.POST.get('priority', 'medium')
        target_audience = request.POST.get('target_audience', 'all')
        
        if title and content:
            # Map priority to is_urgent field
            is_urgent = priority in ['high', 'urgent']
            
            announcement = Announcement.objects.create(
                title=title,
                content=content,
                target_audience=target_audience,
                is_urgent=is_urgent,
                created_by=request.user
            )
            
            # Send notifications to target users
            announcement.send_notifications()
            
            # Log staff activity
            StaffActivity.objects.create(
                staff_member=request.user,
                activity_type='announcement_created',
                description=f'Created announcement: {title}'
            )
            
            messages.success(request, 'Announcement created successfully!')
            return redirect('staff_panel:announcement_management')
        else:
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request, *args, **kwargs)


# Reports Views
class ReportsView(LoginRequiredMixin, TemplateView):
    """Generate and view reports"""
    template_name = 'staff_panel/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import DashboardStats
        
        # Get last 30 days of stats
        stats = DashboardStats.objects.order_by('-date')[:30]
        
        context.update({
            'stats': stats,
        })
        return context


class GenerateReportView(LoginRequiredMixin, TemplateView):
    """Generate specific reports"""
    template_name = 'staff_panel/generate_report.html'
    
    def post(self, request, *args, **kwargs):
        from django.http import HttpResponse
        from django.template.loader import render_to_string
        from .models import StaffActivity
        import csv
        from io import StringIO
        
        report_type = request.POST.get('report_type')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        if report_type and date_from and date_to:
            try:
                # Generate CSV report based on type
                output = StringIO()
                writer = csv.writer(output)
                
                if report_type == 'students':
                    from accounts.models import User
                    writer.writerow(['University ID', 'Name', 'Email', 'Program', 'Year', 'Status'])
                    students = User.objects.filter(user_type='student', date_joined__range=[date_from, date_to])
                    for student in students:
                        writer.writerow([
                            student.university_id,
                            student.get_full_name(),
                            student.email,
                            getattr(student.student_profile, 'program', 'N/A') if hasattr(student, 'student_profile') else 'N/A',
                            getattr(student.student_profile, 'year_of_study', 'N/A') if hasattr(student, 'student_profile') else 'N/A',
                            'Active' if student.is_active else 'Inactive'
                        ])
                
                elif report_type == 'fees':
                    from financial.models import StudentFee
                    writer.writerow(['Student ID', 'Student Name', 'Fee Type', 'Amount', 'Due Date', 'Status'])
                    fees = StudentFee.objects.filter(created_at__range=[date_from, date_to])
                    for fee in fees:
                        writer.writerow([
                            fee.student.university_id,
                            fee.student.get_full_name(),
                            fee.fee_type.name,
                            fee.amount,
                            fee.due_date,
                            fee.get_status_display()
                        ])
                
                elif report_type == 'requests':
                    from student_portal.models import ServiceRequest
                    writer.writerow(['Request ID', 'Student', 'Service Type', 'Status', 'Created Date', 'Updated Date'])
                    requests = ServiceRequest.objects.filter(created_at__range=[date_from, date_to])
                    for req in requests:
                        writer.writerow([
                            req.id,
                            req.student.get_full_name(),
                            req.service_type,
                            req.get_status_display(),
                            req.created_at.strftime('%Y-%m-%d'),
                            req.updated_at.strftime('%Y-%m-%d')
                        ])
                
                # Log staff activity
                StaffActivity.objects.create(
                    staff_member=request.user,
                    activity_type='report_generated',
                    description=f'Generated {report_type} report from {date_from} to {date_to}'
                )
                
                # Return CSV response
                response = HttpResponse(output.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{date_from}_to_{date_to}.csv"'
                return response
                
            except Exception as e:
                messages.error(request, f'Error generating report: {str(e)}')
                return self.get(request, *args, **kwargs)
        else:
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request, *args, **kwargs)


# Document Management Views
class DocumentManagementView(LoginRequiredMixin, TemplateView):
    """Manage student documents"""
    template_name = 'staff_panel/document_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from student_portal.models import StudentDocument
        from accounts.models import User
        
        # Get all documents with related student info
        documents = StudentDocument.objects.select_related(
            'student', 'issued_by'
        ).order_by('-issued_date')[:100]
        
        # Get all students for the upload form
        students = User.objects.filter(
            user_type='student'
        ).order_by('first_name', 'last_name')
        
        context.update({
            'documents': documents,
            'students': students,
        })
        return context


class UploadDocumentView(LoginRequiredMixin, TemplateView):
    """Upload document to student"""
    template_name = 'staff_panel/upload_document.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        from student_portal.models import StudentDocument
        
        # Get all students for selection
        students = User.objects.filter(
            user_type='student'
        ).order_by('first_name', 'last_name')
        
        context.update({
            'students': students,
            'document_types': StudentDocument.DOCUMENT_TYPES,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        from student_portal.models import StudentDocument
        from accounts.models import User
        from .models import StaffActivity
        
        try:
            # Get form data
            student_id = request.POST.get('student')
            document_type = request.POST.get('document_type')
            title = request.POST.get('title')
            document_file = request.FILES.get('document_file')
            
            # Validate required fields
            if not all([student_id, document_type, title, document_file]):
                messages.error(request, 'Please fill in all required fields and select a file.')
                return self.get(request, *args, **kwargs)
            
            # Get student
            student = User.objects.get(id=student_id, user_type='student')
            
            # Create document
            document = StudentDocument.objects.create(
                student=student,
                document_type=document_type,
                title=title,
                document_file=document_file,
                issued_by=request.user,
                is_official=True
            )
            
            # Log staff activity
            StaffActivity.objects.create(
                staff_member=request.user,
                activity_type='document_uploaded',
                target_user=student,
                description=f'Uploaded document: {title} for {student.get_full_name()}'
            )
            
            messages.success(request, f'Document "{title}" uploaded successfully for {student.get_full_name()}!')
            return redirect('staff_panel:document_management')
            
        except User.DoesNotExist:
            messages.error(request, 'Selected student not found.')
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')
        
        return self.get(request, *args, **kwargs)


# System Settings Views
class SystemSettingsView(LoginRequiredMixin, TemplateView):
    """System configuration and settings"""
    template_name = 'staff_panel/system_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import SystemConfiguration
        
        configurations = SystemConfiguration.objects.filter(
            is_active=True
        ).order_by('category', 'key')
        
        context.update({
            'configurations': configurations,
        })
        return context


# API Views for AJAX
@login_required
def get_dashboard_stats(request):
    """Get dashboard statistics via AJAX"""
    from .models import DashboardStats
    
    stats = DashboardStats.get_or_create_today()
    
    data = {
        'total_students': stats.total_students,
        'pending_requests': stats.pending_requests,
        'total_fees_collected_today': float(stats.total_fees_collected_today),
        'open_support_tickets': stats.open_support_tickets,
    }
    
    return JsonResponse(data)


@login_required
def get_recent_activities(request):
    """Get recent activities via AJAX"""
    from .models import StaffActivity
    
    activities = StaffActivity.objects.select_related(
        'staff_member', 'target_user'
    ).order_by('-timestamp')[:10]
    
    data = []
    for activity in activities:
        data.append({
            'description': activity.description,
            'activity_type': activity.get_activity_type_display(),
            'timestamp': activity.timestamp.isoformat(),
            'staff_member': activity.staff_member.get_full_name(),
        })
    
    return JsonResponse({'activities': data})


# Notification Management Views
class NotificationCreateView(LoginRequiredMixin, TemplateView):
    """Create notifications for users"""
    template_name = 'staff_panel/create_notification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from notifications.models import Notification
        from accounts.models import User
        
        # Get all users for recipient selection
        users = User.objects.filter(
            is_active=True
        ).order_by('user_type', 'first_name', 'last_name')
        
        context.update({
            'users': users,
            'notification_types': Notification.NOTIFICATION_TYPES,
            'priority_levels': Notification.PRIORITY_LEVELS,
        })
        return context
    
    def post(self, request, *args, **kwargs):
        from notifications.models import Notification
        from accounts.models import User
        from .models import StaffActivity
        from django.utils import timezone
        from datetime import datetime
        
        try:
            # Get form data
            recipient_ids = request.POST.getlist('recipients')
            title = request.POST.get('title', '').strip()
            message = request.POST.get('message', '').strip()
            notification_type = request.POST.get('notification_type', 'info')
            priority = request.POST.get('priority', 'medium')
            action_url = request.POST.get('action_url', '').strip()
            action_text = request.POST.get('action_text', '').strip()
            expires_at = request.POST.get('expires_at', '').strip()
            
            # Validate required fields
            if not all([recipient_ids, title, message]):
                messages.error(request, 'Please fill in all required fields.')
                return self.get(request, *args, **kwargs)
            
            # Parse expiry date if provided
            expiry_date = None
            if expires_at:
                try:
                    expiry_date = datetime.strptime(expires_at, '%Y-%m-%dT%H:%M')
                    expiry_date = timezone.make_aware(expiry_date)
                except ValueError:
                    messages.error(request, 'Invalid expiry date format.')
                    return self.get(request, *args, **kwargs)
            
            # Get recipients
            if 'all_users' in recipient_ids:
                recipients = User.objects.filter(is_active=True)
            elif 'all_students' in recipient_ids:
                recipients = User.objects.filter(user_type='student', is_active=True)
            elif 'all_staff' in recipient_ids:
                recipients = User.objects.filter(user_type__in=['staff', 'admin'], is_active=True)
            else:
                recipients = User.objects.filter(id__in=recipient_ids, is_active=True)
            
            if not recipients.exists():
                messages.error(request, 'No valid recipients selected.')
                return self.get(request, *args, **kwargs)
            
            # Create notifications
            notifications_created = 0
            for recipient in recipients:
                notification = Notification.objects.create(
                    recipient=recipient,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    action_url=action_url if action_url else '',
                    action_text=action_text if action_text else '',
                    expires_at=expiry_date
                )
                notifications_created += 1
            
            # Log staff activity
            StaffActivity.objects.create(
                staff_member=request.user,
                activity_type='notification_created',
                description=f'Created notification "{title}" for {notifications_created} recipients'
            )
            
            messages.success(
                request, 
                f'Notification "{title}" created successfully for {notifications_created} recipients!'
            )
            return redirect('staff_panel:notification_create')
            
        except Exception as e:
            messages.error(request, f'Error creating notification: {str(e)}')
            return self.get(request, *args, **kwargs)
