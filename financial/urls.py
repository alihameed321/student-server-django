from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    # Financial Dashboard
    path('', views.FinancialDashboardView.as_view(), name='dashboard'),
]