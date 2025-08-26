from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Sum


class DashboardStats(models.Model):
    """Dashboard statistics for staff panel"""
    date = models.DateField(unique=True)
    
    # Student statistics
    total_students = models.IntegerField(default=0)
    new_students_today = models.IntegerField(default=0)
    active_students = models.IntegerField(default=0)
    
    # Request statistics
    total_requests = models.IntegerField(default=0)
    pending_requests = models.IntegerField(default=0)
    approved_requests_today = models.IntegerField(default=0)
    rejected_requests_today = models.IntegerField(default=0)
    
    # Financial statistics
    total_fees_collected_today = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    pending_payments = models.IntegerField(default=0)
    verified_payments_today = models.IntegerField(default=0)
    
    # Support statistics
    open_support_tickets = models.IntegerField(default=0)
    resolved_tickets_today = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Dashboard Statistics"
    
    def __str__(self):
        return f"Dashboard Stats - {self.date}"
    
    @classmethod
    def get_or_create_today(cls):
        """Get or create today's dashboard stats"""
        today = timezone.now().date()
        stats, created = cls.objects.get_or_create(date=today)
        if created:
            stats.calculate_stats()
        return stats
    
    def calculate_stats(self):
        """Calculate and update all statistics"""
        from accounts.models import User
        from student_portal.models import ServiceRequest, SupportTicket
        from financial.models import Payment, StudentFee
        
        # Student statistics
        self.total_students = User.objects.filter(user_type='student').count()
        self.new_students_today = User.objects.filter(
            user_type='student',
            date_joined__date=self.date
        ).count()
        self.active_students = User.objects.filter(
            user_type='student',
            last_login__date=self.date
        ).count()
        
        # Request statistics
        self.total_requests = ServiceRequest.objects.count()
        self.pending_requests = ServiceRequest.objects.filter(
            status__in=['pending', 'in_review']
        ).count()
        self.approved_requests_today = ServiceRequest.objects.filter(
            status='approved',
            updated_at__date=self.date
        ).count()
        self.rejected_requests_today = ServiceRequest.objects.filter(
            status='rejected',
            updated_at__date=self.date
        ).count()
        
        # Financial statistics
        verified_payments_today = Payment.objects.filter(
            status='verified',
            verified_at__date=self.date
        )
        self.total_fees_collected_today = verified_payments_today.aggregate(
            total=Sum('amount')
        )['total'] or 0
        self.pending_payments = Payment.objects.filter(status='pending').count()
        self.verified_payments_today = verified_payments_today.count()
        
        # Support statistics
        self.open_support_tickets = SupportTicket.objects.filter(
            status__in=['open', 'in_progress']
        ).count()
        self.resolved_tickets_today = SupportTicket.objects.filter(
            status='resolved',
            updated_at__date=self.date
        ).count()
        
        self.save()


class StaffActivity(models.Model):
    """Track staff activities for audit purposes"""
    
    ACTIVITY_TYPES = (
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('payment_verified', 'Payment Verified'),
        ('payment_rejected', 'Payment Rejected'),
        ('document_uploaded', 'Document Uploaded'),
        ('announcement_created', 'Announcement Created'),
        ('notification_created', 'Notification Created'),
        ('report_generated', 'Report Generated'),
        ('fee_created', 'Fee Created'),
        ('user_created', 'User Created'),
        ('user_modified', 'User Modified'),
        ('other', 'Other Activity'),
    )
    
    staff_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_activities')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Staff Activities"
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.get_activity_type_display()}"


class WorkflowTemplate(models.Model):
    """Templates for common staff workflows"""
    
    WORKFLOW_TYPES = (
        ('request_processing', 'Request Processing'),
        ('payment_verification', 'Payment Verification'),
        ('document_generation', 'Document Generation'),
        ('student_onboarding', 'Student Onboarding'),
        ('fee_management', 'Fee Management'),
    )
    
    name = models.CharField(max_length=100)
    workflow_type = models.CharField(max_length=25, choices=WORKFLOW_TYPES)
    description = models.TextField()
    steps = models.JSONField(default=list)  # List of workflow steps
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_workflow_type_display()})"


class QuickAction(models.Model):
    """Quick actions for staff dashboard"""
    
    ACTION_TYPES = (
        ('create_announcement', 'Create Announcement'),
        ('verify_payments', 'Verify Payments'),
        ('review_requests', 'Review Requests'),
        ('generate_report', 'Generate Report'),
        ('manage_fees', 'Manage Fees'),
        ('student_lookup', 'Student Lookup'),
    )
    
    name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=25, choices=ACTION_TYPES)
    description = models.CharField(max_length=200)
    url_pattern = models.CharField(max_length=200)
    icon_class = models.CharField(max_length=50, default='fas fa-cog')
    is_active = models.BooleanField(default=True)
    required_permissions = models.JSONField(default=list)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def is_accessible_by(self, user):
        """Check if user has required permissions for this action"""
        if not self.required_permissions:
            return True
        
        # Check if user has any of the required permissions
        for permission in self.required_permissions:
            if user.has_perm(permission):
                return True
        return False


class SystemConfiguration(models.Model):
    """System-wide configuration settings"""
    
    CONFIG_TYPES = (
        ('general', 'General Settings'),
        ('academic', 'Academic Settings'),
        ('financial', 'Financial Settings'),
        ('notification', 'Notification Settings'),
        ('security', 'Security Settings'),
    )
    
    category = models.CharField(max_length=15, choices=CONFIG_TYPES)
    key = models.CharField(max_length=100)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = ['category', 'key']
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category}.{self.key}"
    
    @classmethod
    def get_value(cls, category, key, default=None):
        """Get configuration value"""
        try:
            config = cls.objects.get(category=category, key=key, is_active=True)
            return config.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, category, key, value, user=None, description=""):
        """Set configuration value"""
        config, created = cls.objects.get_or_create(
            category=category,
            key=key,
            defaults={
                'value': value,
                'description': description,
                'updated_by': user
            }
        )
        if not created:
            config.value = value
            config.updated_by = user
            if description:
                config.description = description
            config.save()
        return config
