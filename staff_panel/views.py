from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib import messages


class StaffDashboardView(LoginRequiredMixin, TemplateView):
    """Staff dashboard view"""
    template_name = 'staff_panel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add dashboard statistics here
        context.update({
            'pending_requests': 0,
            'total_students': 0,
            'recent_activities': [],
        })
        
        return context


@login_required
def staff_dashboard(request):
    """Staff dashboard function-based view"""
    context = {
        'pending_requests': 0,
        'total_students': 0,
        'recent_activities': [],
    }
    return render(request, 'staff_panel/dashboard.html', context)
