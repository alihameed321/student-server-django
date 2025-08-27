from django.urls import path
from . import views

app_name = 'staff_panel'

urlpatterns = [
    # Main Dashboard
    path('', views.StaffDashboardView.as_view(), name='dashboard'),
    
    # Request Management
    path('requests/', views.RequestManagementView.as_view(), name='request_management'),
    path('requests/<int:request_id>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    
    # Financial Management
    path('financial/', views.FinancialManagementView.as_view(), name='financial_management'),
    path('financial/payments/', views.PaymentVerificationView.as_view(), name='payment_verification'),
    path('financial/payments/pending/', views.PendingPaymentsView.as_view(), name='pending_payments'),
    path('financial/fees/', views.FeeManagementView.as_view(), name='fee_management'),
    path('financial/fees/create/', views.CreateFeeView.as_view(), name='create_fee'),
    path('fees/<int:fee_id>/edit/', views.EditFeeView.as_view(), name='edit_fee'),
    
    # Payment Provider Management
    path('financial/payment-providers/', views.PaymentProviderManagementView.as_view(), name='payment_provider_management'),
    path('financial/payment-providers/create/', views.CreatePaymentProviderView.as_view(), name='create_payment_provider'),
    path('financial/payment-providers/<int:provider_id>/edit/', views.EditPaymentProviderView.as_view(), name='edit_payment_provider'),
    path('api/payment-providers/<int:provider_id>/delete/', views.delete_payment_provider, name='delete_payment_provider'),
    
    # Student Management
    path('students/', views.StudentManagementView.as_view(), name='student_management'),
    path('students/<int:student_id>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:student_id>/edit/', views.EditStudentView.as_view(), name='edit_student'),
    path('students/<int:student_id>/delete/', views.DeleteStudentView.as_view(), name='delete_student'),
    path('students/add/', views.AddStudentView.as_view(), name='add_student'),
    path('students/search/', views.StudentSearchView.as_view(), name='student_search'),
    
    # Announcement Management
    path('announcements/', views.AnnouncementManagementView.as_view(), name='announcement_management'),
    path('announcements/create/', views.CreateAnnouncementView.as_view(), name='create_announcement'),
    
    # Notification Management
    path('notifications/create/', views.NotificationCreateView.as_view(), name='notification_create'),
    
    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('reports/generate/', views.GenerateReportView.as_view(), name='generate_report'),
    
    # Document Management
    path('documents/', views.DocumentManagementView.as_view(), name='document_management'),
    path('documents/upload/', views.UploadDocumentView.as_view(), name='upload_document'),
    
    # System Settings
    path('settings/', views.SystemSettingsView.as_view(), name='system_settings'),
    
    # API Endpoints for AJAX
    path('api/stats/', views.get_dashboard_stats, name='ajax_dashboard_stats'),
    path('api/activities/', views.get_recent_activities, name='api_activities'),
    path('api/payments/<int:payment_id>/verify/', views.verify_payment, name='verify_payment'),
    path('api/payments/<int:payment_id>/reject/', views.reject_payment, name='reject_payment'),
    path('api/payments/<int:payment_id>/details/', views.get_payment_details, name='payment_details'),
]