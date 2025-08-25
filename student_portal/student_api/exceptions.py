from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for student portal API
    Provides consistent error responses for mobile app integration
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception for debugging
    logger.error(f"API Exception: {exc}", exc_info=True)
    
    if response is not None:
        # Customize the error response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': get_error_message(exc, response),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        response.data = custom_response_data
    else:
        # Handle exceptions not handled by DRF
        if isinstance(exc, ValidationError):
            custom_response_data = {
                'success': False,
                'error': {
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Validation Error',
                    'details': {'validation_errors': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)}
                }
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, Http404):
            custom_response_data = {
                'success': False,
                'error': {
                    'code': status.HTTP_404_NOT_FOUND,
                    'message': 'Resource not found',
                    'details': {'detail': 'The requested resource was not found.'}
                }
            }
            response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
        
        elif isinstance(exc, IntegrityError):
            custom_response_data = {
                'success': False,
                'error': {
                    'code': status.HTTP_400_BAD_REQUEST,
                    'message': 'Data integrity error',
                    'details': {'detail': 'The operation could not be completed due to data constraints.'}
                }
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            # Generic server error
            custom_response_data = {
                'success': False,
                'error': {
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'message': 'Internal server error',
                    'details': {'detail': 'An unexpected error occurred. Please try again later.'}
                }
            }
            response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def get_error_message(exc, response):
    """
    Extract user-friendly error message from exception
    """
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            # Handle field-specific errors
            if 'non_field_errors' in exc.detail:
                return exc.detail['non_field_errors'][0] if exc.detail['non_field_errors'] else 'Validation error'
            else:
                # Return first field error
                for field, errors in exc.detail.items():
                    if isinstance(errors, list) and errors:
                        return f"{field.replace('_', ' ').title()}: {errors[0]}"
                    return str(errors)
        elif isinstance(exc.detail, list):
            return exc.detail[0] if exc.detail else 'An error occurred'
        else:
            return str(exc.detail)
    
    # Default messages based on status code
    status_messages = {
        400: 'Bad request - please check your input',
        401: 'Authentication required',
        403: 'Permission denied',
        404: 'Resource not found',
        405: 'Method not allowed',
        429: 'Too many requests - please try again later',
        500: 'Internal server error'
    }
    
    return status_messages.get(response.status_code, 'An error occurred')


class StudentPortalAPIException(Exception):
    """
    Custom exception for student portal API
    """
    def __init__(self, message, code=status.HTTP_400_BAD_REQUEST, details=None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ServiceRequestException(StudentPortalAPIException):
    """
    Exception for service request related errors
    """
    pass


class DocumentException(StudentPortalAPIException):
    """
    Exception for document related errors
    """
    pass


class SupportTicketException(StudentPortalAPIException):
    """
    Exception for support ticket related errors
    """
    pass