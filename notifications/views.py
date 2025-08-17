from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse


class NotificationCenterView(LoginRequiredMixin, TemplateView):
    """Notification center view"""
    template_name = 'notifications/center.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add notification data here
        context.update({
            'notifications': [],
            'unread_count': 0,
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
        
        # Add announcements data here
        context.update({
            'announcements': [],
            'categories': ['General', 'Academic', 'Events', 'Emergency'],
        })
        
        return context


@login_required
def ajax_unread_count(request):
    """AJAX endpoint to get unread notification count"""
    # For now, return 0 as we don't have notification models implemented
    # This can be updated when notification functionality is fully implemented
    unread_count = 0
    
    return JsonResponse({
        'unread_count': unread_count
    })
