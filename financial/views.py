from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class FinancialDashboardView(LoginRequiredMixin, TemplateView):
    """Financial dashboard view"""
    template_name = 'financial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add financial statistics here
        context.update({
            'total_fees': 0,
            'pending_payments': 0,
            'recent_transactions': [],
        })
        
        return context
