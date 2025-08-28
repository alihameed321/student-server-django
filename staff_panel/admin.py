from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from .models import DashboardStats, StaffActivity, WorkflowTemplate, QuickAction, SystemConfiguration


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    """Admin for Dashboard Statistics with university branding"""
    
    list_display = ('date', 'total_students', 'pending_requests', 'total_fees_collected_today', 'open_support_tickets')
    list_filter = ('date', 'created_at')
    search_fields = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('معلومات التاريخ', {
            'fields': ('date',),
            'classes': ('wide',)
        }),
        ('إحصائيات الطلاب', {
            'fields': ('total_students', 'new_students_today', 'active_students'),
            'classes': ('wide',)
        }),
        ('إحصائيات الطلبات', {
            'fields': ('total_requests', 'pending_requests', 'approved_requests_today', 'rejected_requests_today'),
            'classes': ('wide',)
        }),
        ('الإحصائيات المالية', {
            'fields': ('total_fees_collected_today', 'pending_payments', 'verified_payments_today'),
            'classes': ('wide',)
        }),
        ('إحصائيات الدعم', {
            'fields': ('open_support_tickets', 'resolved_tickets_today'),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['recalculate_stats']
    
    def recalculate_stats(self, request, queryset):
        """Recalculate statistics for selected dashboard stats"""
        updated = 0
        for stats in queryset:
            stats.calculate_stats()
            updated += 1
        
        self.message_user(
            request,
            f'تم إعادة حساب {updated} إحصائية لوحة التحكم.'
        )
    recalculate_stats.short_description = 'إعادة حساب الإحصائيات المحددة'


@admin.register(StaffActivity)
class StaffActivityAdmin(admin.ModelAdmin):
    """Admin for Staff Activities"""
    
    list_display = ('get_staff_info', 'get_activity_badge', 'get_target_user', 'timestamp')
    list_filter = ('activity_type', 'timestamp', 'staff_member__user_type')
    search_fields = ('staff_member__university_id', 'staff_member__first_name', 'staff_member__last_name', 'description')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('معلومات النشاط', {
            'fields': ('staff_member', 'activity_type', 'description'),
            'classes': ('wide',)
        }),
        ('الهدف والسياق', {
            'fields': ('target_user', 'metadata'),
            'classes': ('wide',)
        }),
        ('التفاصيل التقنية', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('البيانات الوصفية', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('timestamp',)
    
    def get_staff_info(self, obj):
        return f"{obj.staff_member.university_id} - {obj.staff_member.get_full_name()}"
    get_staff_info.short_description = 'عضو الموظفين'
    get_staff_info.admin_order_field = 'staff_member__university_id'
    
    def get_target_user(self, obj):
        if obj.target_user:
            return f"{obj.target_user.university_id} - {obj.target_user.get_full_name()}"
        return '-'
    get_target_user.short_description = 'المستخدم المستهدف'
    get_target_user.admin_order_field = 'target_user__university_id'
    
    def get_activity_badge(self, obj):
        colors = {
            'login': '#102A71',
            'logout': '#6c757d',
            'request_approved': '#102A71',
            'request_rejected': '#dc3545',
            'payment_verified': '#F5C400',
            'payment_rejected': '#dc3545',
            'document_uploaded': '#102A71',
            'announcement_created': '#F5C400',
            'fee_created': '#102A71',
            'user_created': '#102A71',
            'user_modified': '#F5C400',
            'other': '#6c757d'
        }
        color = colors.get(obj.activity_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_activity_type_display()
        )
    get_activity_badge.short_description = 'نوع النشاط'
    get_activity_badge.admin_order_field = 'activity_type'


@admin.register(WorkflowTemplate)
class WorkflowTemplateAdmin(admin.ModelAdmin):
    """Admin for Workflow Templates"""
    
    list_display = ('name', 'workflow_type', 'get_status_badge', 'created_by', 'created_at')
    list_filter = ('workflow_type', 'is_active', 'created_at', 'created_by')
    search_fields = ('name', 'description', 'created_by__university_id', 'created_by__first_name', 'created_by__last_name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات القالب', {
            'fields': ('name', 'description', 'workflow_type'),
            'classes': ('wide',)
        }),
        ('تكوين سير العمل', {
            'fields': ('steps',),
            'classes': ('wide',)
        }),
        ('الحالة والصلاحيات', {
            'fields': ('is_active',),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_category_badge(self, obj):
        colors = {
            'student_services': '#102A71',
            'financial': '#F5C400',
            'academic': '#102A71',
            'administrative': '#F5C400',
            'support': '#102A71',
            'other': '#6c757d'
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    get_category_badge.short_description = 'الفئة'
    get_category_badge.admin_order_field = 'category'
    
    def get_status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #102A71; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Inactive</span>'
            )
    get_status_badge.short_description = 'الحالة'
    get_status_badge.admin_order_field = 'is_active'


@admin.register(QuickAction)
class QuickActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'action_type', 'get_status_badge', 'order', 'is_active']
    list_filter = ['action_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['order']
    readonly_fields = []
    
    def get_category_badge(self, obj):
        colors = {
            'student_services': '#102A71',
            'financial': '#F5C400',
            'academic': '#102A71',
            'administrative': '#F5C400',
            'support': '#102A71',
            'system': '#dc3545',
            'other': '#6c757d'
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    get_category_badge.short_description = 'Category'
    get_category_badge.admin_order_field = 'category'
    
    def get_status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #102A71; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Inactive</span>'
            )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'is_active'


@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    """Admin for System Configuration"""
    
    list_display = ('key', 'get_category_badge', 'get_value_preview', 'get_status_badge', 'updated_at')
    list_filter = ('category', 'is_active', 'updated_at')
    search_fields = ('key', 'description', 'updated_by__university_id', 'updated_by__first_name', 'updated_by__last_name')
    ordering = ('category', 'key')
    date_hierarchy = 'updated_at'
    
    fieldsets = (
        ('Configuration Information', {
            'fields': ('key', 'description', 'category'),
            'classes': ('wide',)
        }),
        ('Value & Status', {
            'fields': ('value', 'is_active'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_category_badge(self, obj):
        colors = {
            'general': '#102A71',
            'security': '#dc3545',
            'email': '#F5C400',
            'payment': '#F5C400',
            'notification': '#102A71',
            'api': '#F5C400',
            'database': '#102A71',
            'other': '#6c757d'
        }
        color = colors.get(obj.category, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    get_category_badge.short_description = 'Category'
    get_category_badge.admin_order_field = 'category'
    
    def get_value_preview(self, obj):
        if obj.is_sensitive:
            return '***SENSITIVE***'
        value_str = str(obj.value)
        if len(value_str) > 50:
            return value_str[:47] + '...'
        return value_str
    get_value_preview.short_description = 'Value'
    
    def get_status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #102A71; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Inactive</span>'
            )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'is_active'


# Custom admin site styling
admin.site.site_header = 'University Services Administration'
admin.site.site_title = 'University Admin'
admin.site.index_title = 'Welcome to University Services Admin Panel'
