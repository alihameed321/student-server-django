from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notifications with university branding"""
    
    list_display = ('get_recipient_info', 'title', 'get_type_badge', 'get_priority_badge', 'get_read_status', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at', 'expires_at')
    search_fields = ('recipient__university_id', 'recipient__first_name', 'recipient__last_name', 'title', 'message')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات الإشعار', {
            'fields': ('recipient', 'title', 'message'),
            'classes': ('wide',)
        }),
        ('التصنيف', {
            'fields': ('notification_type', 'priority'),
            'classes': ('wide',)
        }),
        ('الإجراء وانتهاء الصلاحية', {
            'fields': ('action_url', 'action_text', 'expires_at'),
            'classes': ('wide',)
        }),
        ('الحالة', {
            'fields': ('is_read', 'read_at'),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'read_at')
    
    def get_recipient_info(self, obj):
        return f"{obj.recipient.university_id} - {obj.recipient.get_full_name()}"
    get_recipient_info.short_description = 'المستلم'
    get_recipient_info.admin_order_field = 'recipient__university_id'
    
    def get_type_badge(self, obj):
        colors = {
            'info': '#102A71',
            'warning': '#F5C400',
            'success': '#28a745',
            'error': '#dc3545',
            'announcement': '#6f42c1'
        }
        color = colors.get(obj.notification_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_notification_type_display()
        )
    get_type_badge.short_description = 'النوع'
    get_type_badge.admin_order_field = 'notification_type'
    
    def get_priority_badge(self, obj):
        colors = {
            'low': '#28a745',
            'medium': '#F5C400',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display().upper()
        )
    get_priority_badge.short_description = 'الأولوية'
    get_priority_badge.admin_order_field = 'priority'
    
    def get_read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">READ</span>'
            )
        elif obj.expires_at and obj.expires_at < timezone.now():
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">EXPIRED</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #102A71; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">UNREAD</span>'
            )
    get_read_status.short_description = 'الحالة'
    get_read_status.admin_order_field = 'is_read'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read"""
        updated = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                updated += 1
        
        self.message_user(
            request,
            f'تم وضع علامة مقروء على {updated} إشعار.'
        )
    mark_as_read.short_description = 'وضع علامة مقروء على الإشعارات المحددة'
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread"""
        updated = queryset.filter(is_read=True).update(
            is_read=False,
            read_at=None
        )
        
        self.message_user(
            request,
            f'تم وضع علامة غير مقروء على {updated} إشعار.'
        )
    mark_as_unread.short_description = 'وضع علامة غير مقروء على الإشعارات المحددة'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


# Custom admin site styling
admin.site.site_header = 'إدارة الخدمات الجامعية'
admin.site.site_title = 'إدارة الجامعة'
admin.site.index_title = 'مرحباً بك في لوحة إدارة الخدمات الجامعية'
