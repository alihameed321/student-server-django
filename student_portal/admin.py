from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ServiceRequest, StudentDocument, SupportTicket, RequestDocument


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    """Admin for Service Requests with university branding"""
    
    list_display = ('get_student_info', 'request_type', 'title', 'get_status_badge', 'priority', 'created_at')
    list_filter = ('request_type', 'status', 'priority', 'created_at', 'updated_at')
    search_fields = ('student__university_id', 'student__first_name', 'student__last_name', 'title', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_student_info(self, obj):
        return f"{obj.student.university_id} - {obj.student.get_full_name()}"
    get_student_info.short_description = 'الطالب'
    get_student_info.admin_order_field = 'student__university_id'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'in_review': 'info',
            'approved': 'success',
            'rejected': 'danger',
            'completed': 'primary',
            'more_info_needed': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'الحالة'
    get_status_badge.admin_order_field = 'status'
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('student', 'request_type', 'title', 'description'),
            'classes': ('wide',)
        }),
        ('الحالة والمعالجة', {
            'fields': ('status', 'priority', 'processed_by', 'rejection_reason', 'additional_info_request'),
            'classes': ('wide',)
        }),
        ('الطوابع الزمنية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_student_info(self, obj):
        return f"{obj.student.university_id} - {obj.student.get_full_name()}"
    get_student_info.short_description = 'Student'
    get_student_info.admin_order_field = 'student__university_id'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#F5C400',
            'in_review': '#102A71',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'completed': '#28a745',
            'more_info_needed': '#ffc107'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    """Admin for Student Documents"""
    
    list_display = ('get_student_info', 'document_type', 'title', 'get_official_badge', 'issued_date')
    list_filter = ('document_type', 'is_official', 'issued_date')
    search_fields = ('student__university_id', 'student__first_name', 'student__last_name', 'title')
    ordering = ('-issued_date',)
    date_hierarchy = 'issued_date'
    
    fieldsets = (
        ('معلومات الوثيقة', {
            'fields': ('student', 'document_type', 'title', 'document_file'),
            'classes': ('wide',)
        }),
        ('الحالة والتحقق', {
            'fields': ('is_official', 'issued_by'),
            'classes': ('wide',)
        }),
        ('الإحصائيات', {
            'fields': ('download_count',),
            'classes': ('collapse',)
        }),
        ('البيانات الوصفية', {
            'fields': ('issued_date',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('issued_date', 'download_count')
    
    def get_student_info(self, obj):
        return f"{obj.student.university_id} - {obj.student.get_full_name()}"
    get_student_info.short_description = 'Student'
    get_student_info.admin_order_field = 'student__university_id'
    
    def get_official_badge(self, obj):
        if obj.is_official:
            return format_html(
                '<span style="background-color: #102A71; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">OFFICIAL</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">UNOFFICIAL</span>'
        )
    get_official_badge.short_description = 'رسمي'
    get_official_badge.admin_order_field = 'is_official'


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    """Admin for Support Tickets"""
    
    list_display = ('get_student_info', 'subject', 'get_priority_badge', 'get_status_badge', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('student__university_id', 'student__first_name', 'student__last_name', 'subject', 'description')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات التذكرة', {
            'fields': ('student', 'subject', 'description', 'category'),
            'classes': ('wide',)
        }),
        ('الحالة والأولوية', {
            'fields': ('status', 'priority', 'assigned_to', 'resolution'),
            'classes': ('wide',)
        }),
        ('الطوابع الزمنية', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_student_info(self, obj):
        return f"{obj.student.university_id} - {obj.student.get_full_name()}"
    get_student_info.short_description = 'Student'
    get_student_info.admin_order_field = 'student__university_id'
    
    def get_status_badge(self, obj):
        colors = {
            'open': '#F5C400',
            'in_progress': '#102A71',
            'resolved': '#28a745',
            'closed': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'
    
    def get_priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#F5C400',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper()
        )
    get_priority_badge.short_description = 'الأولوية'
    get_priority_badge.admin_order_field = 'priority'


@admin.register(RequestDocument)
class RequestDocumentAdmin(admin.ModelAdmin):
    """Admin for Request Documents"""
    
    list_display = ('get_request_info', 'document_name', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('service_request__student__university_id', 'document_name')
    ordering = ('-uploaded_at',)
    
    def get_request_info(self, obj):
        return f"{obj.service_request.student.university_id} - {obj.service_request.title}"
    get_request_info.short_description = 'Service Request'
    get_request_info.admin_order_field = 'service_request__student__university_id'
