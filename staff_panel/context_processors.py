from student_portal.models import ServiceRequest
from financial.models import StudentFee

def staff_context(request):
    """
    Context processor to provide staff-specific data to all templates
    """
    context = {}
    
    # Only add context for staff users
    if request.user.is_authenticated and hasattr(request.user, 'user_type') and request.user.user_type == 'staff':
        # Get pending requests count
        pending_requests = ServiceRequest.objects.filter(
            status__in=['pending', 'in_review']
        ).count()
        
        # Get pending payments count
        pending_payments_count = StudentFee.objects.filter(
            status__in=['pending', 'overdue', 'partial']
        ).count()
        
        context.update({
            'pending_requests': pending_requests,
            'pending_payments_count': pending_payments_count,
        })
    
    return context