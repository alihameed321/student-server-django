from django.urls import path
from .views import (
    UserNotificationsListView, NotificationDetailView, AnnouncementListView,
    NotificationPreferencesView, user_notifications, mark_notification_read,
    mark_notification_unread, mark_all_notifications_read, notification_stats,
    delete_notification
)

app_name = 'notifications_api'

urlpatterns = [
    # Notification list and management
    path('', UserNotificationsListView.as_view(), name='notifications_list'),
    path('list/', user_notifications, name='user_notifications'),  # Legacy endpoint
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    
    # Notification actions
    path('<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
    path('<int:notification_id>/unread/', mark_notification_unread, name='mark_notification_unread'),
    path('<int:notification_id>/delete/', delete_notification, name='delete_notification'),
    path('mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Statistics and preferences
    path('stats/', notification_stats, name='notification_stats'),
    path('preferences/', NotificationPreferencesView.as_view(), name='notification_preferences'),
    
    # Announcements
    path('announcements/', AnnouncementListView.as_view(), name='announcements_list'),
]