from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """System notifications for users"""
    
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Optional link for action
    action_url = models.URLField(blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.university_id} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class Announcement(models.Model):
    """University-wide announcements"""
    
    TARGET_AUDIENCES = (
        ('all', 'All Users'),
        ('students', 'All Students'),
        ('staff', 'All Staff'),
        ('specific_major', 'Specific Major'),
        ('specific_year', 'Specific Academic Year'),
        ('specific_department', 'Specific Department'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCES, default='all')
    
    # Specific targeting fields
    target_major = models.CharField(max_length=100, blank=True)
    target_year = models.IntegerField(null=True, blank=True)
    target_department = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    publish_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking
    view_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-publish_date']
    
    def __str__(self):
        return self.title
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    @property
    def is_published(self):
        """Check if announcement is published"""
        now = timezone.now()
        return self.is_active and self.publish_date <= now
    
    @property
    def is_expired(self):
        """Check if announcement has expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def get_target_users(self):
        """Get users who should receive this announcement"""
        from accounts.models import User
        
        if self.target_audience == 'all':
            return User.objects.all()
        elif self.target_audience == 'students':
            return User.objects.filter(user_type='student')
        elif self.target_audience == 'staff':
            return User.objects.filter(user_type__in=['staff', 'admin'])
        elif self.target_audience == 'specific_major' and self.target_major:
            return User.objects.filter(user_type='student', major=self.target_major)
        elif self.target_audience == 'specific_year' and self.target_year:
            return User.objects.filter(user_type='student', enrollment_year=self.target_year)
        elif self.target_audience == 'specific_department' and self.target_department:
            return User.objects.filter(user_type__in=['staff', 'admin'], department=self.target_department)
        
        return User.objects.none()
    
    def send_notifications(self):
        """Send notifications to target users"""
        target_users = self.get_target_users()
        notifications = []
        
        for user in target_users:
            notification = Notification(
                recipient=user,
                title=f"📢 {self.title}",
                message=self.content,
                notification_type='announcement',
                priority='high' if self.is_urgent else 'medium',
                expires_at=self.expiry_date
            )
            notifications.append(notification)
        
        Notification.objects.bulk_create(notifications)


class NotificationTemplate(models.Model):
    """Templates for common notifications"""
    
    TEMPLATE_TYPES = (
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('payment_verified', 'Payment Verified'),
        ('payment_rejected', 'Payment Rejected'),
        ('fee_due', 'Fee Due Reminder'),
        ('document_ready', 'Document Ready'),
        ('general', 'General Template'),
    )
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def render(self, context):
        """Render template with context variables"""
        subject = self.subject_template.format(**context)
        message = self.message_template.format(**context)
        return subject, message


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_announcements = models.BooleanField(default=True)
    email_request_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_fee_reminders = models.BooleanField(default=True)
    
    # In-app notifications
    app_announcements = models.BooleanField(default=True)
    app_request_updates = models.BooleanField(default=True)
    app_payment_updates = models.BooleanField(default=True)
    app_fee_reminders = models.BooleanField(default=True)
    
    # Notification frequency
    digest_frequency = models.CharField(
        max_length=10,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
        ],
        default='immediate'
    )
    
    def __str__(self):
        return f"Notification Preferences - {self.user.get_full_name()}"
