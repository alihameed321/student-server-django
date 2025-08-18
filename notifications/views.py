from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Notification, Announcement


class NotificationCenterView(LoginRequiredMixin, TemplateView):
    """Notification center view"""
    template_name = 'notifications/center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's notifications
        notifications = Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')[:20]  # Get latest 20 notifications
        
        unread_count = Notification.objects.filter(
            recipient=self.request.user,
            is_read=False
        ).count()
        
        read_count = Notification.objects.filter(
            recipient=self.request.user,
            is_read=True
        ).count()
        
        context.update({
            'notifications': notifications,
            'unread_count': unread_count,
            'read_count': read_count,
        })
        
        return context


class NotificationPreferencesView(LoginRequiredMixin, TemplateView):
    """Notification preferences view"""
    template_name = 'notifications/preferences.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add notification preferences data here
        context.update({
            'preferences': {},
        })
        
        return context


class AnnouncementsView(LoginRequiredMixin, TemplateView):
    """Announcements view"""
    template_name = 'notifications/announcements.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active announcements
        announcements = Announcement.objects.filter(
            is_active=True
        ).order_by('-created_at')
        
        context.update({
            'announcements': announcements,
            'categories': ['General', 'Academic', 'Events', 'Emergency'],
        })
        
        return context


@login_required
def ajax_unread_count(request):
    """AJAX endpoint to get unread notification count"""
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({
        'count': unread_count
    })


@login_required
def ajax_recent_notifications(request):
    """AJAX endpoint to get recent notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')[:5]  # Get latest 5 notifications
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read
        })
    
    return JsonResponse({
        'notifications': notifications_data
    })


@login_required
def ajax_mark_read(request, notification_id):
    """AJAX endpoint to mark a notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Notification marked as read'
            })
        except Notification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Notification not found'
            }, status=404)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)
