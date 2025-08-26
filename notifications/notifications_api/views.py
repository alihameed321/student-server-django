from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationUpdateSerializer,
    AnnouncementSerializer, NotificationPreferenceSerializer, NotificationStatsSerializer
)
from notifications.models import Notification, Announcement, NotificationPreference
import logging

logger = logging.getLogger(__name__)


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserNotificationsListView(generics.ListAPIView):
    """List user notifications with filtering and pagination"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user).order_by('-created_at')
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Filter by notification type
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        
        # Search in title and message
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        
        # Add unread count to response
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        
        response.data['unread_count'] = unread_count
        return response


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific notification"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id, recipient=request.user
        )
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'data': {
                'id': notification.id,
                'is_read': notification.is_read,
                'read_at': notification.read_at
            }
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_unread(request, notification_id):
    """Mark a specific notification as unread"""
    try:
        notification = Notification.objects.get(
            id=notification_id, recipient=request.user
        )
        notification.is_read = False
        notification.read_at = None
        notification.save()
        
        return Response({
            'success': True,
            'message': 'Notification marked as unread',
            'data': {
                'id': notification.id,
                'is_read': notification.is_read,
                'read_at': notification.read_at
            }
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read for the user"""
    filters = request.data if request.data else {}
    
    queryset = Notification.objects.filter(recipient=request.user, is_read=False)
    
    # Apply filters if provided
    if 'notification_type' in filters:
        queryset = queryset.filter(notification_type=filters['notification_type'])
    if 'priority' in filters:
        queryset = queryset.filter(priority=filters['priority'])
    
    updated_count = queryset.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'success': True,
        'message': f'{updated_count} notifications marked as read',
        'data': {
            'updated_count': updated_count
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """Get notification statistics for the user"""
    user = request.user
    today = timezone.now().date()
    
    # Basic counts
    total_notifications = Notification.objects.filter(recipient=user).count()
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False).count()
    high_priority_unread = Notification.objects.filter(
        recipient=user, is_read=False, priority='high'
    ).count()
    urgent_priority_unread = Notification.objects.filter(
        recipient=user, is_read=False, priority='urgent'
    ).count()
    notifications_today = Notification.objects.filter(
        recipient=user, created_at__date=today
    ).count()
    
    # Breakdown by type
    type_counts = Notification.objects.filter(recipient=user).values('notification_type').annotate(
        count=Count('id')
    )
    
    type_breakdown = {
        'info_count': 0,
        'warning_count': 0,
        'success_count': 0,
        'error_count': 0,
        'announcement_count': 0
    }
    
    for item in type_counts:
        type_breakdown[f"{item['notification_type']}_count"] = item['count']
    
    stats_data = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'high_priority_unread': high_priority_unread,
        'urgent_priority_unread': urgent_priority_unread,
        'notifications_today': notifications_today,
        **type_breakdown
    }
    
    serializer = NotificationStatsSerializer(data=stats_data)
    if serializer.is_valid():
        return Response({
            'success': True,
            'data': serializer.validated_data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Error generating statistics'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnnouncementListView(generics.ListAPIView):
    """List active announcements"""
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        now = timezone.now()
        return Announcement.objects.filter(
            publish_date__lte=now,
            expiry_date__gte=now
        ).order_by('-is_pinned', '-publish_date')


class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """Get and update user notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    try:
        notification = Notification.objects.get(
            id=notification_id, recipient=request.user
        )
        notification.delete()
        
        return Response({
            'success': True,
            'message': 'Notification deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)


# Legacy endpoint for backward compatibility
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    """Legacy API endpoint for user notifications - redirects to new endpoint"""
    view = UserNotificationsListView.as_view()
    return view(request)