from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notifications Center
    path('', views.NotificationCenterView.as_view(), name='notification_center'),
    path('preferences/', views.NotificationPreferencesView.as_view(), name='notification_preferences'),
    path('announcements/', views.AnnouncementsView.as_view(), name='announcements'),
    
    # AJAX endpoints
    path('ajax/unread-count/', views.ajax_unread_count, name='ajax_unread_count'),
]