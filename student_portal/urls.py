from django.urls import path
from . import views

app_name = 'student_portal'

urlpatterns = [
    # Dashboard
    path('', views.StudentDashboardView.as_view(), name='dashboard'),
    
    # E-Services Center
    path('services/', views.eservices_center, name='eservices_center'),
    path('services/create/', views.create_request, name='create_request'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/cancel/', views.cancel_request, name='cancel_request'),
    
    # Document Inbox
    path('documents/', views.document_inbox, name='document_inbox'),
    path('documents/<int:document_id>/download/', views.download_document, name='download_document'),
    
    # Support Center
    path('support/', views.support_center, name='support_center'),
    path('support/create/', views.create_ticket, name='create_ticket'),
    path('support/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('support/<int:ticket_id>/respond/', views.respond_to_ticket, name='respond_to_ticket'),
    
    # AJAX endpoints
    path('ajax/notifications/', views.get_notifications, name='ajax_notifications'),
    path('ajax/dashboard-stats/', views.get_dashboard_stats, name='ajax_dashboard_stats'),
]