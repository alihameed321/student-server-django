from django.urls import path
from . import views

app_name = 'student_api'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    # Service Requests
    path('service-requests/', views.service_requests, name='service_requests'),
    path('service-requests/<int:request_id>/', views.service_request_detail, name='service_request_detail'),
    path('service-requests/<int:request_id>/cancel/', views.cancel_service_request, name='cancel_service_request'),
    path('service-request-types/', views.service_request_types, name='service_request_types'),
    
    # Student Documents
    path('documents/', views.student_documents, name='student_documents'),
    path('documents/<int:document_id>/', views.document_detail, name='document_detail'),
    
    # Support Tickets
    path('support-tickets/', views.support_tickets, name='support_tickets'),
    path('support-tickets/<int:ticket_id>/', views.support_ticket_detail, name='support_ticket_detail'),
    path('support-tickets/<int:ticket_id>/respond/', views.add_ticket_response, name='add_ticket_response'),
    path('ticket-categories/', views.ticket_categories, name='ticket_categories'),
]