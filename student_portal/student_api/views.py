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
    Enhanced list of all documents for authenticated student with advanced filtering and sorting
    """
    try:
        validate_student_access(request.user)
        
        # DEBUG: Log user information
        logger.info(f"[DEBUG] student_documents called for user: {request.user.id} ({request.user.username})")
        
        documents = StudentDocument.objects.filter(student=request.user)
        
        # DEBUG: Log initial document count
        initial_count = documents.count()
        logger.info(f"[DEBUG] Initial documents count for user {request.user.id}: {initial_count}")
        
        # DEBUG: Log all documents for this user
        if initial_count > 0:
            for doc in documents:
                logger.info(f"[DEBUG] Document: ID={doc.id}, Type={doc.document_type}, Title={doc.title}, Official={doc.is_official}")
        else:
            logger.warning(f"[DEBUG] No documents found for user {request.user.id}")
            # Check if any documents exist in the system
            total_docs = StudentDocument.objects.count()
            logger.info(f"[DEBUG] Total documents in system: {total_docs}")
        
        # Apply filters with validation
        document_type_filter = request.GET.get('document_type')
        logger.info(f"[DEBUG] document_type_filter: {document_type_filter}")
        
        if document_type_filter:
            valid_types = [choice[0] for choice in StudentDocument.DOCUMENT_TYPES]
            logger.info(f"[DEBUG] Valid document types: {valid_types}")
            if document_type_filter not in valid_types:
                logger.error(f"[DEBUG] Invalid document type filter: {document_type_filter}")
                raise DocumentException(f"Invalid document type filter: {document_type_filter}")
            documents = documents.filter(document_type=document_type_filter)
            filtered_count = documents.count()
            logger.info(f"[DEBUG] Documents after type filter '{document_type_filter}': {filtered_count}")
        
        is_official_filter = request.GET.get('is_official')
        logger.info(f"[DEBUG] is_official_filter: {is_official_filter}")
        if is_official_filter is not None:
            documents = documents.filter(is_official=is_official_filter.lower() == 'true')
            logger.info(f"[DEBUG] Documents after is_official filter: {documents.count()}")
        
        # Date range filtering
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        logger.info(f"[DEBUG] Date filters - from: {date_from}, to: {date_to}")
        
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                documents = documents.filter(issued_date__gte=date_from_obj)
                logger.info(f"[DEBUG] Documents after date_from filter: {documents.count()}")
            except ValueError:
                logger.error(f"[DEBUG] Invalid date_from format: {date_from}")
                raise DocumentException("Invalid date_from format. Use YYYY-MM-DD")
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                documents = documents.filter(issued_date__lte=date_to_obj)
                logger.info(f"[DEBUG] Documents after date_to filter: {documents.count()}")
            except ValueError:
                logger.error(f"[DEBUG] Invalid date_to format: {date_to}")
                raise DocumentException("Invalid date_to format. Use YYYY-MM-DD")
        
        # Search functionality
        search = request.GET.get('search')
        logger.info(f"[DEBUG] Search query: {search}")
        if search:
            if len(search.strip()) < 2:
                logger.error(f"[DEBUG] Search query too short: '{search}'")
                raise DocumentException("Search query must be at least 2 characters long")
            from django.db.models import Q
            documents = documents.filter(
                Q(title__icontains=search) | 
                Q(document_type__icontains=search)
            )
            logger.info(f"[DEBUG] Documents after search filter: {documents.count()}")
        
        # Sorting options
        sort_by = request.GET.get('sort_by', 'issued_date')
        sort_order = request.GET.get('sort_order', 'desc')
        logger.info(f"[DEBUG] Sorting - by: {sort_by}, order: {sort_order}")
        
        valid_sort_fields = ['issued_date', 'title', 'document_type', 'download_count']
        if sort_by not in valid_sort_fields:
            logger.error(f"[DEBUG] Invalid sort field: {sort_by}")
            raise DocumentException(f"Invalid sort field. Valid options: {', '.join(valid_sort_fields)}")
        
        if sort_order not in ['asc', 'desc']:
            logger.error(f"[DEBUG] Invalid sort order: {sort_order}")
            raise DocumentException("Invalid sort order. Use 'asc' or 'desc'")
        
        sort_field = sort_by if sort_order == 'asc' else f'-{sort_by}'
        documents = documents.order_by(sort_field)
        
        # DEBUG: Final document count before pagination
        final_count = documents.count()
        logger.info(f"[DEBUG] Final documents count after all filters and sorting: {final_count}")
        
        # Paginate results
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(documents, request)
        
        if page is not None:
            serializer = StudentDocumentSerializer(page, many=True, context={'request': request})
            response_data = {
                'success': True,
                'data': serializer.data,
                'filters': {
                    'document_type': document_type_filter,
                    'is_official': is_official_filter,
                    'date_from': date_from,
                    'date_to': date_to,
                    'search': search,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
            logger.info(f"[DEBUG] Returning paginated response with {len(serializer.data)} documents")
            return paginator.get_paginated_response(response_data)
        
        serializer = StudentDocumentSerializer(documents, many=True, context={'request': request})
        response_data = {
            'success': True,
            'data': serializer.data,
            'count': documents.count(),
            'filters': {
                'document_type': document_type_filter,
                'is_official': is_official_filter,
                'date_from': date_from,
                'date_to': date_to,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }
        logger.info(f"[DEBUG] Returning non-paginated response with {len(serializer.data)} documents")
        return Response(response_data)
    
    except DocumentException as e:
        logger.error(f"[DEBUG] DocumentException in student_documents: {e.message} (code: {e.code})")
        return Response({
            'success': False,
            'error': {
                'code': e.code,
                'message': e.message,
                'details': e.details
            }
        }, status=e.code)
    except Exception as e:
        logger.error(f"[DEBUG] Unexpected error in student_documents: {str(e)}")
        logger.error(f"[DEBUG] Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"[DEBUG] Traceback: {traceback.format_exc()}")
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
    Get detailed information about a specific document (preview mode)
    """
    try:
        validate_student_access(request.user)
        
        document = get_object_or_404(
            StudentDocument, 
            id=document_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, document)
        
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStudentUser])
def document_download(request, document_id):
    """
    Download a specific document and track download count
    """
    try:
        validate_student_access(request.user)
        
        document = get_object_or_404(
            StudentDocument, 
            id=document_id, 
            student=request.user
        )
        
        validate_object_ownership(request.user, document)
        
        if not document.document_file:
            return Response({
                'success': False,
                'error': {
                    'code': status.HTTP_404_NOT_FOUND,
                    'message': 'Document file not found',
                    'details': {}
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Increment download count
        document.download_count += 1
        document.save()
        
        from django.http import HttpResponse, Http404
        import os
        import mimetypes
        
        try:
            file_path = document.document_file.path
            if not os.path.exists(file_path):
                raise Http404("Document file not found on server")
            
            # Get file info
            file_size = os.path.getsize(file_path)
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create response with file
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{document.title}"'
                response['Content-Length'] = file_size
                return response
                
        except Exception as file_error:
            logger.error(f"File access error: {str(file_error)}")
            return Response({
                'success': False,
                'error': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': 'Error accessing document file',
                    'details': {}
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
        logger.error(f"Error in document_download: {str(e)}")
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
def document_types(request):
    """
    Get available document types for filtering
    """
    try:
        validate_student_access(request.user)
        
        logger.info(f"[DEBUG] document_types called for user: {request.user.id} ({request.user.username})")
        
        # Get document type choices from model
        types = [{
            'value': choice[0],
            'label': choice[1]
        } for choice in StudentDocument.DOCUMENT_TYPES]
        
        logger.info(f"[DEBUG] Returning {len(types)} document types: {[t['value'] for t in types]}")
        
        return Response({
            'success': True,
            'data': types
        })
    
    except Exception as e:
        logger.error(f"Error in document_types: {str(e)}")
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
def document_statistics(request):
    """
    Get document statistics for dashboard
    """
    try:
        validate_student_access(request.user)
        
        logger.info(f"[DEBUG] document_statistics called for user: {request.user.id} ({request.user.username})")
        
        from django.utils import timezone
        from datetime import timedelta
        
        documents = StudentDocument.objects.filter(student=request.user)
        
        # Calculate statistics
        total_documents = documents.count()
        official_documents = documents.filter(is_official=True).count()
        total_downloads = sum(doc.download_count for doc in documents)
        
        logger.info(f"[DEBUG] Statistics - Total: {total_documents}, Official: {official_documents}, Downloads: {total_downloads}")
        
        # Recent documents (last 30 days)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_documents = documents.filter(issued_date__gte=thirty_days_ago).count()
        
        logger.info(f"[DEBUG] Recent documents (last 30 days): {recent_documents}")
        
        # Documents by type
        documents_by_type = {}
        for doc_type, doc_type_display in StudentDocument.DOCUMENT_TYPES:
            count = documents.filter(document_type=doc_type).count()
            if count > 0:
                documents_by_type[doc_type] = {
                    'label': doc_type_display,
                    'count': count
                }
        
        # Most downloaded documents (top 5)
        most_downloaded = documents.order_by('-download_count')[:5]
        most_downloaded_data = [{
            'id': doc.id,
            'title': doc.title,
            'document_type': doc.get_document_type_display(),
            'download_count': doc.download_count
        } for doc in most_downloaded]
        
        logger.info(f"[DEBUG] Documents by type: {documents_by_type}")
        logger.info(f"[DEBUG] Most downloaded count: {len(most_downloaded_data)}")
        
        return Response({
            'success': True,
            'data': {
                'total_documents': total_documents,
                'official_documents': official_documents,
                'total_downloads': total_downloads,
                'recent_documents': recent_documents,
                'documents_by_type': documents_by_type,
                'most_downloaded': most_downloaded_data
            }
        })
    
    except Exception as e:
        logger.error(f"Error in document_statistics: {str(e)}")
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
def document_status_tracking(request):
    """
    Get document status and availability information
    """
    try:
        validate_student_access(request.user)
        
        documents = StudentDocument.objects.filter(student=request.user)
        
        # Calculate status information
        status_data = []
        for document in documents:
            file_exists = bool(document.document_file)
            try:
                file_accessible = file_exists and document.document_file.path
                import os
                file_accessible = file_accessible and os.path.exists(document.document_file.path)
            except:
                file_accessible = False
            
            status_info = {
                'id': document.id,
                'title': document.title,
                'document_type': document.get_document_type_display(),
                'issued_date': document.issued_date,
                'is_official': document.is_official,
                'download_count': document.download_count,
                'status': {
                    'is_available': file_accessible,
                    'is_downloadable': file_accessible,
                    'file_exists': file_exists,
                    'processing_status': 'completed' if file_accessible else 'processing',
                    'status_message': 'Document is ready for download' if file_accessible else 'Document is being processed'
                },
                'file_info': {
                    'has_file': file_exists,
                    'file_size': document.document_file.size if file_exists else 0,
                    'file_extension': None
                }
            }
            
            # Get file extension
            if file_exists and document.document_file.name:
                import os
                status_info['file_info']['file_extension'] = os.path.splitext(document.document_file.name)[1].lower()
            
            status_data.append(status_info)
        
        # Summary statistics
        total_documents = len(status_data)
        available_documents = sum(1 for doc in status_data if doc['status']['is_available'])
        processing_documents = total_documents - available_documents
        
        return Response({
            'success': True,
            'data': {
                'documents': status_data,
                'summary': {
                    'total_documents': total_documents,
                    'available_documents': available_documents,
                    'processing_documents': processing_documents,
                    'availability_rate': (available_documents / total_documents * 100) if total_documents > 0 else 0
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error in document_status_tracking: {str(e)}")
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
def document_advanced_search(request):
    """
    Advanced search API with multiple search criteria
    """
    try:
        validate_student_access(request.user)
        
        documents = StudentDocument.objects.filter(student=request.user)
        
        # Search parameters
        query = request.GET.get('q', '').strip()
        document_type = request.GET.get('document_type')
        is_official = request.GET.get('is_official')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        min_downloads = request.GET.get('min_downloads')
        max_downloads = request.GET.get('max_downloads')
        
        # Apply search filters
        if query:
            if len(query) < 2:
                raise DocumentException("Search query must be at least 2 characters long")
            from django.db.models import Q
            documents = documents.filter(
                Q(title__icontains=query) | 
                Q(document_type__icontains=query) |
                Q(issued_by__first_name__icontains=query) |
                Q(issued_by__last_name__icontains=query)
            )
        
        if document_type:
            valid_types = [choice[0] for choice in StudentDocument.DOCUMENT_TYPES]
            if document_type not in valid_types:
                raise DocumentException(f"Invalid document type: {document_type}")
            documents = documents.filter(document_type=document_type)
        
        if is_official is not None:
            documents = documents.filter(is_official=is_official.lower() == 'true')
        
        # Date range filtering
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                documents = documents.filter(issued_date__date__gte=date_from_obj)
            except ValueError:
                raise DocumentException("Invalid date_from format. Use YYYY-MM-DD")
        
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                documents = documents.filter(issued_date__date__lte=date_to_obj)
            except ValueError:
                raise DocumentException("Invalid date_to format. Use YYYY-MM-DD")
        
        # Download count filtering
        if min_downloads:
            try:
                min_downloads_int = int(min_downloads)
                documents = documents.filter(download_count__gte=min_downloads_int)
            except ValueError:
                raise DocumentException("Invalid min_downloads value")
        
        if max_downloads:
            try:
                max_downloads_int = int(max_downloads)
                documents = documents.filter(download_count__lte=max_downloads_int)
            except ValueError:
                raise DocumentException("Invalid max_downloads value")
        
        # Sorting
        sort_by = request.GET.get('sort_by', 'issued_date')
        sort_order = request.GET.get('sort_order', 'desc')
        
        valid_sort_fields = ['issued_date', 'title', 'document_type', 'download_count']
        if sort_by not in valid_sort_fields:
            raise DocumentException(f"Invalid sort field. Valid options: {', '.join(valid_sort_fields)}")
        
        if sort_order not in ['asc', 'desc']:
            raise DocumentException("Invalid sort order. Use 'asc' or 'desc'")
        
        sort_field = sort_by if sort_order == 'asc' else f'-{sort_by}'
        documents = documents.order_by(sort_field)
        
        # Paginate results
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(documents, request)
        
        search_params = {
            'query': query,
            'document_type': document_type,
            'is_official': is_official,
            'date_from': date_from,
            'date_to': date_to,
            'min_downloads': min_downloads,
            'max_downloads': max_downloads,
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        if page is not None:
            serializer = StudentDocumentSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data,
                'search_params': search_params,
                'total_matches': documents.count()
            })
        
        serializer = StudentDocumentSerializer(documents, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data,
            'search_params': search_params,
            'total_matches': documents.count()
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
        logger.error(f"Error in document_advanced_search: {str(e)}")
        return Response({
            'success': False,
            'error': {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'An unexpected error occurred',
                'details': {}
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsStudentUser])
def document_sharing(request):
    """
    Document sharing and access control API
    GET: List shared documents and sharing permissions
    POST: Create document sharing links or permissions
    """
    try:
        validate_student_access(request.user)
        
        if request.method == 'GET':
            # Get document sharing information
            document_id = request.GET.get('document_id')
            
            if document_id:
                # Get specific document sharing info
                try:
                    document = StudentDocument.objects.get(id=document_id, student=request.user)
                except StudentDocument.DoesNotExist:
                    raise DocumentException("Document not found", status.HTTP_404_NOT_FOUND)
                
                # Generate secure sharing information
                import hashlib
                import time
                
                # Create a secure token for sharing
                token_data = f"{document.id}_{request.user.id}_{int(time.time())}"
                sharing_token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
                
                sharing_info = {
                    'document_id': document.id,
                    'title': document.title,
                    'document_type': document.get_document_type_display(),
                    'is_official': document.is_official,
                    'sharing_enabled': True,  # Can be controlled by admin settings
                    'sharing_token': sharing_token,
                    'sharing_url': f"/api/student/documents/{document.id}/shared/{sharing_token}/",
                    'access_control': {
                        'can_download': document.document_file and bool(document.document_file),
                        'can_view': True,
                        'requires_authentication': True,
                        'expiry_date': None,  # Can be implemented for time-limited sharing
                        'access_count': 0  # Can be tracked in a separate model
                    },
                    'permissions': {
                        'owner_can_revoke': True,
                        'owner_can_set_expiry': True,
                        'owner_can_limit_downloads': True
                    }
                }
                
                return Response({
                    'success': True,
                    'data': sharing_info
                })
            
            else:
                # Get all documents with sharing capabilities
                documents = StudentDocument.objects.filter(student=request.user)
                sharing_data = []
                
                for document in documents:
                    has_file = bool(document.document_file)
                    sharing_data.append({
                        'document_id': document.id,
                        'title': document.title,
                        'document_type': document.get_document_type_display(),
                        'is_official': document.is_official,
                        'issued_date': document.issued_date,
                        'sharing_capabilities': {
                            'can_share': has_file,
                            'can_generate_link': has_file,
                            'supports_access_control': True,
                            'reason': 'Document ready for sharing' if has_file else 'No file available'
                        }
                    })
                
                return Response({
                    'success': True,
                    'data': {
                        'documents': sharing_data,
                        'total_shareable': sum(1 for doc in sharing_data if doc['sharing_capabilities']['can_share'])
                    }
                })
        
        elif request.method == 'POST':
            # Create or update sharing settings
            document_id = request.data.get('document_id')
            action = request.data.get('action', 'create_link')  # create_link, revoke_access, update_permissions
            
            if not document_id:
                raise DocumentException("Document ID is required")
            
            try:
                document = StudentDocument.objects.get(id=document_id, student=request.user)
            except StudentDocument.DoesNotExist:
                raise DocumentException("Document not found", status.HTTP_404_NOT_FOUND)
            
            if not document.document_file:
                raise DocumentException("Cannot share document without file")
            
            if action == 'create_link':
                # Generate new sharing link
                import hashlib
                import time
                from datetime import datetime, timedelta
                
                token_data = f"{document.id}_{request.user.id}_{int(time.time())}"
                sharing_token = hashlib.sha256(token_data.encode()).hexdigest()[:32]
                
                # Optional expiry (can be set by user)
                expiry_hours = request.data.get('expiry_hours', 24)  # Default 24 hours
                expiry_date = datetime.now() + timedelta(hours=int(expiry_hours)) if expiry_hours else None
                
                sharing_link = {
                    'document_id': document.id,
                    'sharing_token': sharing_token,
                    'sharing_url': f"/api/student/documents/{document.id}/shared/{sharing_token}/",
                    'created_at': datetime.now().isoformat(),
                    'expires_at': expiry_date.isoformat() if expiry_date else None,
                    'access_settings': {
                        'download_enabled': request.data.get('allow_download', True),
                        'view_enabled': True,
                        'max_downloads': request.data.get('max_downloads'),
                        'requires_auth': request.data.get('requires_auth', False)
                    }
                }
                
                return Response({
                    'success': True,
                    'message': 'Sharing link created successfully',
                    'data': sharing_link
                })
            
            elif action == 'revoke_access':
                # Revoke sharing access (in real implementation, this would update a sharing model)
                return Response({
                    'success': True,
                    'message': 'Document sharing access revoked successfully',
                    'data': {
                        'document_id': document.id,
                        'revoked_at': datetime.now().isoformat()
                    }
                })
            
            else:
                raise DocumentException(f"Invalid action: {action}")
    
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
        logger.error(f"Error in document_sharing: {str(e)}")
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