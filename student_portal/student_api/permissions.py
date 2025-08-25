from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist


class IsStudentUser(permissions.BasePermission):
    """
    Permission to only allow students to access student portal APIs
    """
    message = "Only students can access this resource."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'student'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it
    """
    message = "You can only access your own resources."
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a 'student' field and it matches the current user
        if hasattr(obj, 'student'):
            return obj.student == request.user
        
        # Check if the object is the user themselves
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For other cases, check if the object is the user
        return obj == request.user


class CanModifyServiceRequest(permissions.BasePermission):
    """
    Permission to check if user can modify a service request
    """
    message = "You cannot modify this service request."
    
    def has_object_permission(self, request, view, obj):
        # Only the student who created the request can modify it
        if obj.student != request.user:
            return False
        
        # Check if the request can be modified based on its status
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            modifiable_statuses = ['pending', 'in_review']
            if obj.status not in modifiable_statuses:
                self.message = f"Cannot modify request with status '{obj.get_status_display()}'"
                return False
        
        return True


class CanCancelServiceRequest(permissions.BasePermission):
    """
    Permission to check if user can cancel a service request
    """
    message = "You cannot cancel this service request."
    
    def has_object_permission(self, request, view, obj):
        # Only the student who created the request can cancel it
        if obj.student != request.user:
            return False
        
        # Check if the request can be cancelled based on its status
        cancellable_statuses = ['pending', 'in_review']
        if obj.status not in cancellable_statuses:
            self.message = f"Cannot cancel request with status '{obj.get_status_display()}'"
            return False
        
        return True


class CanRespondToTicket(permissions.BasePermission):
    """
    Permission to check if user can respond to a support ticket
    """
    message = "You cannot respond to this ticket."
    
    def has_object_permission(self, request, view, obj):
        # Only the student who created the ticket can respond to it
        if obj.student != request.user:
            return False
        
        # Check if the ticket can receive responses based on its status
        respondable_statuses = ['open', 'in_progress']
        if obj.status not in respondable_statuses:
            self.message = f"Cannot respond to ticket with status '{obj.get_status_display()}'"
            return False
        
        return True


class CanAccessDocument(permissions.BasePermission):
    """
    Permission to check if user can access a document
    """
    message = "You cannot access this document."
    
    def has_object_permission(self, request, view, obj):
        # Only the student who owns the document can access it
        return obj.student == request.user


class StudentPortalPermissionMixin:
    """
    Mixin to add common permission checks for student portal views
    """
    
    def check_student_access(self, user):
        """
        Check if user is a student and has access to student portal
        """
        if not user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        
        if user.user_type != 'student':
            raise PermissionDenied("Only students can access this resource.")
        
        return True
    
    def check_object_ownership(self, user, obj, field_name='student'):
        """
        Check if user owns the object
        """
        if not hasattr(obj, field_name):
            raise PermissionDenied("Invalid object access.")
        
        if getattr(obj, field_name) != user:
            raise PermissionDenied("You can only access your own resources.")
        
        return True
    
    def check_request_modification_allowed(self, service_request):
        """
        Check if service request can be modified
        """
        modifiable_statuses = ['pending', 'in_review']
        if service_request.status not in modifiable_statuses:
            raise PermissionDenied(
                f"Cannot modify request with status '{service_request.get_status_display()}'"
            )
        return True
    
    def check_ticket_response_allowed(self, ticket):
        """
        Check if ticket can receive responses
        """
        respondable_statuses = ['open', 'in_progress']
        if ticket.status not in respondable_statuses:
            raise PermissionDenied(
                f"Cannot respond to ticket with status '{ticket.get_status_display()}'"
            )
        return True


def validate_student_access(user):
    """
    Utility function to validate student access
    """
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
    if user.user_type != 'student':
        raise PermissionDenied("Only students can access this resource.")
    
    return True


def validate_object_ownership(user, obj, field_name='student'):
    """
    Utility function to validate object ownership
    """
    if not hasattr(obj, field_name):
        raise PermissionDenied("Invalid object access.")
    
    if getattr(obj, field_name) != user:
        raise PermissionDenied("You can only access your own resources.")
    
    return True