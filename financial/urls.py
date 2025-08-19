from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    # Financial Dashboard
    path('', views.FinancialDashboardView.as_view(), name='dashboard'),
    path('pay-fees/', views.PayFeesView.as_view(), name='pay_fees'),
    path('payment-history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    
    # Receipt Management
    path('receipt/<int:payment_id>/', views.view_receipt, name='view_receipt'),
    path('receipt/<int:payment_id>/download/', views.download_receipt, name='download_receipt'),
]