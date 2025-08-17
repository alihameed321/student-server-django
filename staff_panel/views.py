from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
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
    
    service_request = ServiceRequest.objects.get(id=request_id)
    service_request.status = 'approved'
    service_request.processed_by = request.user
    service_request.processed_at = timezone.now()
    service_request.save()
    
    # Log staff activity
    StaffActivity.objects.create(
        staff_member=request.user,
        activity_type='request_approved',
        description=f'Approved {service_request.service_type} request for {service_request.student.get_full_name()}',
        target_user=service_request.student
    )
    
    messages.success(request, f'Request #{request_id} has been approved successfully.')
    return JsonResponse({'status': 'success', 'message': 'Request approved'})


@login_required
def reject_request(request, request_id):
    """Reject a service request"""
    from student_portal.models import ServiceRequest
    from .models import StaffActivity
    
    service_request = ServiceRequest.objects.get(id=request_id)
    service_request.status = 'rejected'
    service_request.processed_by = request.user
    service_request.processed_at = timezone.now()
    service_request.save()
    
    # Log staff activity
    StaffActivity.objects.create(
        staff_member=request.user,
        activity_type='request_rejected',
        description=f'Rejected {service_request.service_type} request for {service_request.student.get_full_name()}',
        target_user=service_request.student
    )
    
    messages.success(request, f'Request #{request_id} has been rejected.')
    return JsonResponse({'status': 'success', 'message': 'Request rejected'})


# Financial Management Views
class FinancialManagementView(LoginRequiredMixin, TemplateView):
    """Financial overview and management"""
    template_name = 'staff_panel/financial_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import Payment, StudentFee
        
        # Financial statistics
        total_revenue = Payment.objects.filter(status='verified').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_payments = Payment.objects.filter(status='pending').count()
        verified_today = Payment.objects.filter(
            status='verified',
            verified_at__date=timezone.now().date()
        ).count()
        
        context.update({
            'total_revenue': total_revenue,
            'pending_payments': pending_payments,
            'verified_today': verified_today,
        })
        return context


class PaymentVerificationView(LoginRequiredMixin, TemplateView):
    """Verify student payments"""
    template_name = 'staff_panel/payment_verification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import Payment
        
        pending_payments = Payment.objects.filter(
            status='pending'
        ).select_related('student').order_by('-created_at')
        
        context.update({
            'pending_payments': pending_payments,
        })
        return context


class PendingPaymentsView(LoginRequiredMixin, TemplateView):
    """View all pending payments"""
    template_name = 'staff_panel/pending_payments.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import Payment
        
        payments = Payment.objects.filter(
            status='pending'
        ).select_related('student', 'fee').order_by('-created_at')
        
        context.update({
            'payments': payments,
        })
        return context


class FeeManagementView(LoginRequiredMixin, TemplateView):
    """Manage student fees"""
    template_name = 'staff_panel/fee_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from financial.models import StudentFee
        
        fees = StudentFee.objects.select_related('student').order_by('-due_date')
        
        context.update({
            'fees': fees,
        })
        return context


class CreateFeeView(LoginRequiredMixin, TemplateView):
    """Create new fee"""
    template_name = 'staff_panel/create_fee.html'


# Student Management Views
class StudentManagementView(LoginRequiredMixin, TemplateView):
    """Manage students"""
    template_name = 'staff_panel/student_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from accounts.models import User
        
        students = User.objects.filter(
            user_type='student'
        ).select_related('studentprofile').order_by('-date_joined')
        
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
        student = User.objects.select_related('studentprofile').get(
            id=student_id, user_type='student'
        )
        
        context.update({
            'student': student,
        })
        return context


class AddStudentView(LoginRequiredMixin, TemplateView):
    """Add new student"""
    template_name = 'staff_panel/add_student.html'


class StudentSearchView(LoginRequiredMixin, TemplateView):
    """Search for students"""
    template_name = 'staff_panel/student_search.html'
    
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
            ).select_related('studentprofile')[:20]
        
        context.update({
            'students': students,
            'search_query': search_query,
        })
        return context


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
