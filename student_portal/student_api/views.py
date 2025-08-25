from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import logging

from ..models import ServiceRequest, StudentDocument, SupportTicket, TicketResponse
from .serializers import (
    ServiceRequestListSerializer, ServiceRequestDetailSerializer, ServiceRequestCreateSerializer,
    StudentDocumentSerializer, SupportTicketListSerializer, SupportTicketDetailSerializer,
    SupportTicketCreateSerializer, TicketResponseCreateSerializer, DashboardStatsSerializer
)
from .permissions import (
    IsStudentUser, CanModifyServiceRequest, CanCancelServiceRequest, 
    CanRespondToTicket, CanAccessDocument, validate_student_access, validate_object_ownership
)
from .exceptions import ServiceRequestException, DocumentException, SupportTicketException

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# Service Request API Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsStudentUser])
def service_requests(request):
    """
    List all service requests for authenticated student or create a new one
    """
    try:
        validate_student_access(request.user)
        
        if request.method == 'GET':
            # Filter requests for current student
            requests = ServiceRequest.objects.filter(student=request.user).order_by('-created_at')
            
            # Apply filters with validation
            status_filter = request.GET.get('status')
            if status_filter:
                valid_statuses = [choice[0] for choice in ServiceRequest.STATUS_CHOICES]
                if status_filter not in valid_statuses:
                    raise ServiceRequestException(f"Invalid status filter: {status_filter}")
                requests = requests.filter(status=status_filter)
            
            request_type_filter = request.GET.get('request_type')
            if request_type_filter:
                valid_types = [choice[0] for choice in ServiceRequest.REQUEST_TYPE_CHOICES]
                if request_type_filter not in valid_types:
                    raise ServiceRequestException(f"Invalid request type filter: {request_type_filter}")
                requests = requests.filter(request_type=request_type_filter)
            
            search = request.GET.get('search')
            if search:
                if len(search.strip()) < 2:
                    raise ServiceRequestException("Search query must be at least 2 characters long")
                requests = requests.filter(
                    Q(title__icontains=search) | Q(description__icontains=search)
                )
            
            # Paginate results
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(requests, request)
            
            if page is not None:
                serializer = ServiceRequestListSerializer(page, many=True, context={'request': request})
                return paginator.get_paginated_response(serializer.data)
            
            serializer = ServiceRequestListSerializer(requests, many=True, context={'request': request})
            return Response({
                'success': True,
                'data': serializer.data,
                'count': requests.count()
            })
        
        elif request.method == 'POST':
            # Create new service request
            serializer = ServiceRequestCreateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    service_request = serializer.save()
                    detail_serializer = ServiceRequestDetailSerializer(service_request, context={'request': request})
                    logger.info(f"Service request created: {service_request.id} by user {request.user.id}")
                    return Response({
                        'success': True,
                        'message': 'Service request created successfully',
                        'data': detail_serializer.data
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"Error creating service request: {str(e)}")
                    raise ServiceRequestException("Failed to create service request")
            else:
                raise ServiceRequestException("Invalid request data", details=serializer.errors)
    
    except ServiceRequestException as e:
        return Response({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details
            }
        }, status=e.code)
    except Exception as e:
        logger.error(f"Unexpected error in service_requests: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def service_request_detail(request, request_id):
    """
    Get detailed information about a specific service request
    """
    try:
        validate_student_access(request.user)
        
        service_request = get_object_or_404(
            ServiceRequest, 
            id=request_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, service_request)
        
        serializer = ServiceRequestDetailSerializer(service_request, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except ServiceRequest.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Service request not found',
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in service_request_detail: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudentUser])
def cancel_service_request(request, request_id):
    """
    Cancel a service request (only if status allows)
    """
    try:
        validate_student_access(request.user)
        
        service_request = get_object_or_404(
            ServiceRequest, 
            id=request_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, service_request)
        
        if service_request.status not in ['pending', 'in_review']:
            raise ServiceRequestException(
                f"Cannot cancel request with status '{service_request.get_status_display()}'",
                code=status.HTTP_400_BAD_REQUEST
            )
        
        service_request.status = 'cancelled'
        service_request.save()
        
        logger.info(f"Service request {request_id} cancelled by user {request.user.id}")
        
        serializer = ServiceRequestDetailSerializer(service_request, context={'request': request})
        return Response({
            'success': True,
            'message': 'Service request cancelled successfully',
            'data': serializer.data
        })
    
    except ServiceRequest.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Service request not found',
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except ServiceRequestException as e:
        return Response({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details
            }
        }, status=e.code)
    except Exception as e:
        logger.error(f"Error in cancel_service_request: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def service_request_types(request):
    """
    Get available service request types
    """
    try:
        validate_student_access(request.user)
        
        types = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in ServiceRequest.REQUEST_TYPES
        ]
        return Response(types, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching service request types: {str(e)}")
        return Response(
            {'success': False, 'error': {'code': 500, 'message': 'Internal server error', 'details': {'detail': 'An unexpected error occurred. Please try again later.'}}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Student Documents API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def student_documents(request):
    """
    List all documents for authenticated student
    """
    try:
        validate_student_access(request.user)
        
        documents = StudentDocument.objects.filter(student=request.user).order_by('-issued_date')
        
        # Apply filters with validation
        document_type_filter = request.GET.get('document_type')
        if document_type_filter:
            valid_types = [choice[0] for choice in StudentDocument.DOCUMENT_TYPE_CHOICES]
            if document_type_filter not in valid_types:
                raise DocumentException(f"Invalid document type filter: {document_type_filter}")
            documents = documents.filter(document_type=document_type_filter)
        
        is_official_filter = request.GET.get('is_official')
        if is_official_filter is not None:
            documents = documents.filter(is_official=is_official_filter.lower() == 'true')
        
        search = request.GET.get('search')
        if search:
            if len(search.strip()) < 2:
                raise DocumentException("Search query must be at least 2 characters long")
            documents = documents.filter(title__icontains=search)
        
        # Paginate results
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(documents, request)
        
        if page is not None:
            serializer = StudentDocumentSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = StudentDocumentSerializer(documents, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data,
            'count': documents.count()
        })
    
    except DocumentException as e:
        return Response({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details
            }
        }, status=e.code)
    except Exception as e:
        logger.error(f"Unexpected error in student_documents: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def document_detail(request, document_id):
    """
    Get detailed information about a specific document
    """
    try:
        validate_student_access(request.user)
        
        document = get_object_or_404(
            StudentDocument, 
            id=document_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, document)
        
        # Increment download count
        document.download_count += 1
        document.save()
        
        serializer = StudentDocumentSerializer(document, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except StudentDocument.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Document not found',
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in document_detail: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Support Tickets API Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsStudentUser])
def support_tickets(request):
    """
    List all support tickets for authenticated student or create a new one
    """
    try:
        validate_student_access(request.user)
        
        if request.method == 'GET':
            tickets = SupportTicket.objects.filter(student=request.user).order_by('-created_at')
            
            # Apply filters with validation
            status_filter = request.GET.get('status')
            if status_filter:
                valid_statuses = [choice[0] for choice in SupportTicket.STATUS_CHOICES]
                if status_filter not in valid_statuses:
                    raise SupportTicketException(f"Invalid status filter: {status_filter}")
                tickets = tickets.filter(status=status_filter)
            
            category_filter = request.GET.get('category')
            if category_filter:
                valid_categories = [choice[0] for choice in SupportTicket.CATEGORY_CHOICES]
                if category_filter not in valid_categories:
                    raise SupportTicketException(f"Invalid category filter: {category_filter}")
                tickets = tickets.filter(category=category_filter)
            
            search = request.GET.get('search')
            if search:
                if len(search.strip()) < 2:
                    raise SupportTicketException("Search query must be at least 2 characters long")
                tickets = tickets.filter(
                    Q(subject__icontains=search) | Q(description__icontains=search)
                )
            
            # Paginate results
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(tickets, request)
            
            if page is not None:
                serializer = SupportTicketListSerializer(page, many=True, context={'request': request})
                return paginator.get_paginated_response({
                    'success': True,
                    'data': serializer.data
                })
            
            serializer = SupportTicketListSerializer(tickets, many=True, context={'request': request})
            return Response({
                'success': True,
                'data': serializer.data,
                'count': tickets.count()
            })
        
        elif request.method == 'POST':
            # Create new support ticket
            serializer = SupportTicketCreateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                try:
                    ticket = serializer.save()
                    detail_serializer = SupportTicketDetailSerializer(ticket, context={'request': request})
                    logger.info(f"Support ticket created: {ticket.id} by user {request.user.id}")
                    return Response({
                        'success': True,
                        'message': 'Support ticket created successfully',
                        'data': detail_serializer.data
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"Error creating support ticket: {str(e)}")
                    raise SupportTicketException("Failed to create support ticket")
            else:
                raise SupportTicketException("Invalid request data", details=serializer.errors)
    
    except SupportTicketException as e:
        return Response({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details
            }
        }, status=e.code)
    except Exception as e:
        logger.error(f"Unexpected error in support_tickets: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def support_ticket_detail(request, ticket_id):
    """
    Get detailed information about a specific support ticket
    """
    try:
        validate_student_access(request.user)
        
        ticket = get_object_or_404(
            SupportTicket, 
            id=ticket_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, ticket)
        
        serializer = SupportTicketDetailSerializer(ticket, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    except SupportTicket.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Support ticket not found',
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in support_ticket_detail: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudentUser])
def add_ticket_response(request, ticket_id):
    """
    Add a response to a support ticket
    """
    try:
        validate_student_access(request.user)
        
        ticket = get_object_or_404(
            SupportTicket, 
            id=ticket_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, ticket)
        
        if ticket.status not in ['open', 'in_progress']:
            raise SupportTicketException(
                'Cannot respond to ticket with current status',
                code=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TicketResponseCreateSerializer(
            data=request.data, 
            context={'request': request, 'ticket': ticket}
        )
        
        if serializer.is_valid():
            response = serializer.save()
            
            # Update ticket status and timestamp
            ticket.status = 'in_progress'
            ticket.updated_at = timezone.now()
            ticket.save()
            
            logger.info(f"Response added to ticket {ticket_id} by user {request.user.id}")
            
            # Return updated ticket detail
            ticket_serializer = SupportTicketDetailSerializer(ticket, context={'request': request})
            return Response({
                'success': True,
                'message': 'Response added successfully',
                'data': ticket_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        raise SupportTicketException("Invalid request data", details=serializer.errors)
    
    except SupportTicket.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_404_NOT_FOUND,
                'message': 'Support ticket not found',
                'details': {}
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except SupportTicketException as e:
        return Response({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details
            }
        }, status=e.code)
    except Exception as e:
        logger.error(f"Error in add_ticket_response: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_categories(request):
    """
    Get available support ticket categories
    """
    categories = [
        {'value': choice[0], 'label': choice[1]} 
        for choice in SupportTicket.CATEGORY_CHOICES
    ]
    return Response({'categories': categories})


# Dashboard API View
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def student_dashboard(request):
    """
    Get comprehensive dashboard data for the authenticated student
    """
    try:
        validate_student_access(request.user)
        user = request.user
        
        # Get statistics with error handling
        try:
            pending_requests = ServiceRequest.objects.filter(
                student=user, 
                status__in=['pending', 'in_review']
            ).count()
            
            total_requests = ServiceRequest.objects.filter(student=user).count()
            
            open_tickets = SupportTicket.objects.filter(
                student=user, 
                status__in=['open', 'in_progress']
            ).count()
            
            new_documents = StudentDocument.objects.filter(
                student=user,
                issued_date__gte=timezone.now() - timedelta(days=7)
            ).count()
            
        except Exception as e:
            logger.error(f"Error fetching dashboard statistics: {str(e)}")
            # Provide default values if statistics fail
            pending_requests = total_requests = open_tickets = new_documents = 0
        
        # Get recent activities with error handling
        try:
            recent_requests = ServiceRequest.objects.filter(
                student=user
            ).select_related('student').order_by('-created_at')[:5]
            
            recent_tickets = SupportTicket.objects.filter(
                student=user
            ).select_related('student').order_by('-created_at')[:5]
            
            recent_documents = StudentDocument.objects.filter(
                student=user
            ).select_related('student').order_by('-issued_date')[:5]
            
        except Exception as e:
            logger.error(f"Error fetching recent activities: {str(e)}")
            # Provide empty querysets if activities fail
            recent_requests = ServiceRequest.objects.none()
            recent_tickets = SupportTicket.objects.none()
            recent_documents = StudentDocument.objects.none()
        
        # Prepare dashboard data
        dashboard_data = {
            'success': True,
            'data': {
                'statistics': {
                    'pending_requests': pending_requests,
                    'total_requests': total_requests,
                    'open_tickets': open_tickets,
                    'new_documents': new_documents,
                },
                'recent_activities': {
                    'service_requests': ServiceRequestListSerializer(
                        recent_requests, many=True, context={'request': request}
                    ).data,
                    'support_tickets': SupportTicketListSerializer(
                        recent_tickets, many=True, context={'request': request}
                    ).data,
                    'documents': StudentDocumentSerializer(
                        recent_documents, many=True, context={'request': request}
                    ).data,
                },
                'quick_actions': [
                    {
                        'title': 'New Service Request',
                        'description': 'Submit a new service request',
                        'action': 'create_service_request',
                        'icon': 'plus-circle',
                        'endpoint': '/api/student/service-requests/'
                    },
                    {
                        'title': 'Support Ticket',
                        'description': 'Get help with technical issues',
                        'action': 'create_support_ticket',
                        'icon': 'help-circle',
                        'endpoint': '/api/student/support-tickets/'
                    },
                    {
                        'title': 'My Documents',
                        'description': 'View and download your documents',
                        'action': 'view_documents',
                        'icon': 'file-text',
                        'endpoint': '/api/student/documents/'
                    },
                ],
                'user_info': {
                    'full_name': user.get_full_name(),
                    'email': user.email,
                    'student_id': getattr(user, 'student_id', None),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            }
        }
        
        return Response(dashboard_data)
    
    except Exception as e:
        logger.error(f"Error in student_dashboard: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred while loading dashboard',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)