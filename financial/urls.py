from django.urls import path, include
from . import views

app_name = 'financial'

urlpatterns = [
    # Financial Dashboard (Web Interface)
    path('', views.FinancialDashboardView.as_view(), name='dashboard'),
    path('pay-fees/', views.PayFeesView.as_view(), name='pay_fees'),
    path('payment-history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    
    # Receipt Management (Web Interface)
    path('receipt/<int:payment_id>/', views.view_receipt, name='view_receipt'),
    path('receipt/<int:payment_id>/download/', views.download_receipt, name='download_receipt'),
    
    # API Endpoints for Mobile App
    path('api/', include('financial.financial_api.urls')),
]