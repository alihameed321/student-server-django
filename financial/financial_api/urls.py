from django.urls import path
from . import views

app_name = 'financial_api'

urlpatterns = [
    # Financial Summary
    path('summary/', views.financial_summary, name='financial_summary'),
    
    # Student Fees
    path('fees/', views.StudentFeeListView.as_view(), name='student_fees'),
    path('fees/<int:pk>/', views.StudentFeeDetailView.as_view(), name='student_fee_detail'),
    path('fees/outstanding/', views.outstanding_fees, name='outstanding_fees'),
    
    # Payment Providers
    path('payment-providers/', views.PaymentProviderListView.as_view(), name='payment_providers'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payments'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/create/', views.create_payment, name='create_payment'),
    path('payments/statistics/', views.payment_statistics, name='payment_statistics'),
    
    # Receipts
    path('receipts/<int:payment_id>/view/', views.view_receipt, name='view_receipt'),
    path('receipts/<int:payment_id>/download/', views.download_receipt, name='download_receipt'),
]