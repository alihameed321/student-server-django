from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


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
