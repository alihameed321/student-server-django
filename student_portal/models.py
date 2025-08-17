from django.db import models
from django.conf import settings
from django.utils import timezone


class ServiceRequest(models.Model):
    """Model for student service requests"""
    
    REQUEST_TYPES = (
        ('enrollment_certificate', 'Enrollment Certificate'),
        ('schedule_modification', 'Schedule Modification'),
        ('semester_postponement', 'Semester Postponement'),
        ('transcript', 'Official Transcript'),
        ('graduation_certificate', 'Graduation Certificate'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('more_info_needed', 'More Information Needed'),
    )
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests')
    rejection_reason = models.TextField(blank=True)
    additional_info_request = models.TextField(blank=True)
    priority = models.IntegerField(default=1)  # 1=Low, 2=Medium, 3=High
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.university_id} - {self.get_request_type_display()}"
    
    @property
    def status_icon(self):
        icons = {
            'pending': '⏳',
            'in_review': '👀',
            'approved': '✅',
            'rejected': '❌',
            'completed': '🎉',
            'more_info_needed': '❓',
        }
        return icons.get(self.status, '📄')


class RequestDocument(models.Model):
    """Supporting documents for service requests"""
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='request_documents/')
    document_name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.request} - {self.document_name}"


class StudentDocument(models.Model):
    """Official documents issued to students"""
    
    DOCUMENT_TYPES = (
        ('enrollment_certificate', 'Enrollment Certificate'),
        ('transcript', 'Official Transcript'),
        ('graduation_certificate', 'Graduation Certificate'),
        ('payment_receipt', 'Payment Receipt'),
        ('other', 'Other Document'),
    )
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='student_documents/')
    issued_date = models.DateTimeField(auto_now_add=True)
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='issued_documents')
    is_official = models.BooleanField(default=True)
    download_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-issued_date']
    
    def __str__(self):
        return f"{self.student.university_id} - {self.title}"
    
    def increment_download_count(self):
        self.download_count += 1
        self.save()


class SupportTicket(models.Model):
    """Support tickets for student inquiries"""
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.university_id} - {self.subject}"


class TicketResponse(models.Model):
    """Responses to support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False)  # Internal staff notes
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response to {self.ticket.subject} by {self.responder.get_full_name()}"
