from rest_framework import serializers
from notifications.models import Notification, Announcement, NotificationTemplate, NotificationPreference
from accounts.models import User


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'is_read', 'created_at', 'read_at', 'expires_at', 'action_url',
            'action_text', 'recipient_name', 'time_since_created'
        ]
        read_only_fields = ['id', 'created_at', 'recipient_name', 'time_since_created']
    
    def get_time_since_created(self, obj):
        """Get human-readable time since notification was created"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"منذ {diff.days} {'أيام' if diff.days > 1 else 'يوم'}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"منذ {hours} {'ساعات' if hours > 1 else 'ساعة'}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"منذ {minutes} {'دقائق' if minutes > 1 else 'دقيقة'}"
        else:
            return "الآن"


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'recipient', 'title', 'message', 'notification_type', 'priority',
            'expires_at', 'action_url', 'action_text'
        ]


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notification status"""
    
    class Meta:
        model = Notification
        fields = ['is_read']


class AnnouncementSerializer(serializers.ModelSerializer):
    """Serializer for Announcement model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'target_audience', 'publish_date',
            'expiry_date', 'is_urgent', 'is_pinned', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by_name']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_announcements', 'email_request_updates', 'email_payment_updates',
            'email_fee_reminders', 'app_announcements', 'app_request_updates',
            'app_payment_updates', 'app_fee_reminders', 'digest_frequency'
        ]


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()
    high_priority_unread = serializers.IntegerField()
    urgent_priority_unread = serializers.IntegerField()
    notifications_today = serializers.IntegerField()
    
    # Breakdown by type
    info_count = serializers.IntegerField()
    warning_count = serializers.IntegerField()
    success_count = serializers.IntegerField()
    error_count = serializers.IntegerField()
    announcement_count = serializers.IntegerField()