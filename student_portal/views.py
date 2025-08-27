from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views import View
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import ServiceRequest, StudentDocument, SupportTicket, RequestDocument
from .forms import ServiceRequestForm, SupportTicketForm
import json


class StudentDashboardView(LoginRequiredMixin, View):
    """Student dashboard view"""
    
    def get(self, request):
        if not request.user.is_student:
            messages.error(request, 'الوصول مرفوض. للطلاب فقط.')
            return redirect('accounts:login')
        
        # Get dashboard statistics
        pending_requests = ServiceRequest.objects.filter(
            student=request.user, 
            status='pending'
        ).count()
        
        new_documents = StudentDocument.objects.filter(
            student=request.user
        ).count()
        
        open_tickets = SupportTicket.objects.filter(
            student=request.user,
            status__in=['open', 'in_progress']
        ).count()
        
        # Get recent requests
        recent_requests = ServiceRequest.objects.filter(
            student=request.user
        ).order_by('-created_at')[:5]
        
        # Get recent documents
        recent_documents = StudentDocument.objects.filter(
            student=request.user
        ).order_by('-issued_date')[:5]
        
        context = {
            'pending_requests': pending_requests,
            'new_documents': new_documents,
            'open_tickets': open_tickets,
            'recent_requests': recent_requests,
            'recent_documents': recent_documents,
        }
        
        return render(request, 'student_portal/dashboard.html', context)


@login_required
def eservices_center(request):
    """E-services center view"""
    if not request.user.is_student:
        messages.error(request, 'الوصول مرفوض. للطلاب فقط.')
        return redirect('accounts:login')
    
    requests_list = ServiceRequest.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    requests = paginator.get_page(page_number)
    
    context = {
        'requests': requests,
    }
    
    return render(request, 'student_portal/eservices_center.html', context)


@login_required
def create_request(request):
    """Create new academic request"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.student = request.user
            service_request.save()
            
            messages.success(request, 'تم تقديم الطلب بنجاح!')
            return redirect('student_portal:eservices_center')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = ServiceRequestForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'student_portal/create_request.html', context)


@login_required
def request_detail(request, request_id):
    """View request details"""
    service_request = get_object_or_404(
        ServiceRequest, 
        id=request_id, 
        student=request.user
    )
    
    context = {
        'request': service_request,
    }
    
    return render(request, 'student_portal/request_detail.html', context)


@login_required
@require_http_methods(["POST"])
def cancel_request(request, request_id):
    """Cancel a request"""
    service_request = get_object_or_404(
        ServiceRequest, 
        id=request_id, 
        student=request.user
    )
    
    if service_request.status == 'pending':
        service_request.status = 'rejected'
        service_request.save()
        messages.success(request, 'تم إلغاء الطلب بنجاح.')
        return JsonResponse({'success': True})
    else:
        return JsonResponse({
            'success': False, 
            'error': 'لا يمكن إلغاء هذا الطلب.'
        })


@login_required
def document_inbox(request):
    """Document inbox view"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    documents_list = StudentDocument.objects.filter(
        student=request.user
    ).order_by('-issued_date')
    
    # Pagination
    paginator = Paginator(documents_list, 10)
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)
    
    context = {
        'documents': documents,
    }
    
    return render(request, 'student_portal/document_inbox.html', context)


@login_required
def download_document(request, document_id):
    """Download a document"""
    document = get_object_or_404(
        StudentDocument, 
        id=document_id, 
        student=request.user
    )
    
    # Increment download count
    document.increment_download_count()
    
    # Get the original filename with extension
    import os
    original_filename = os.path.basename(document.document_file.name)
    
    # Return file response
    response = HttpResponse(
        document.document_file.read(), 
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
    
    return response


@login_required
def support_center(request):
    """Support center view"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    tickets_list = SupportTicket.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tickets_list, 10)
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)
    
    context = {
        'tickets': tickets,
    }
    
    return render(request, 'student_portal/support_center.html', context)


@login_required
def create_ticket(request):
    """Create new support ticket"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.student = request.user
            ticket.save()
            messages.success(request, 'تم إنشاء تذكرة الدعم بنجاح!')
            return redirect('student_portal:support_center')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SupportTicketForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'student_portal/create_ticket.html', context)


@login_required
def ticket_detail(request, ticket_id):
    """View ticket details"""
    ticket = get_object_or_404(
        SupportTicket, 
        id=ticket_id, 
        student=request.user
    )
    
    context = {
        'ticket': ticket,
    }
    
    return render(request, 'student_portal/ticket_detail.html', context)


@login_required
@require_http_methods(["POST"])
def respond_to_ticket(request, ticket_id):
    """Respond to a support ticket"""
    ticket = get_object_or_404(
        SupportTicket, 
        id=ticket_id, 
        student=request.user
    )
    
    response_text = request.POST.get('response')
    if response_text:
        # Add response to ticket (this would need a separate model for responses)
        # For now, just update the ticket description
        ticket.description += f"\n\n--- Student Response ({timezone.now()}) ---\n{response_text}"
        ticket.save()
        
        messages.success(request, 'تم إضافة الرد بنجاح.')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'لم يتم تقديم رد.'})


# AJAX Views
@login_required
@require_http_methods(["GET"])
def get_notifications(request):
    """Get user notifications via AJAX"""
    # This would integrate with the notifications app
    notifications = []
    
    return JsonResponse({
        'notifications': notifications,
        'unread_count': 0
    })


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    # This would integrate with the notifications app
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["GET"])
def get_dashboard_stats(request):
    """Get dashboard statistics via AJAX"""
    if not request.user.is_student:
        return JsonResponse({'error': 'الوصول مرفوض'}, status=403)
    
    stats = {
        'pending_requests': ServiceRequest.objects.filter(
            student=request.user, 
            status='pending'
        ).count(),
        'new_documents': StudentDocument.objects.filter(
            student=request.user
        ).count(),
        'open_tickets': SupportTicket.objects.filter(
            student=request.user,
            status__in=['open', 'in_progress']
        ).count(),
    }
    
    return JsonResponse(stats)


@login_required
def my_requests(request):
    """View all user requests"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    requests_list = ServiceRequest.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    requests = paginator.get_page(page_number)
    
    context = {
        'requests': requests,
    }
    
    return render(request, 'student_portal/my_requests.html', context)


@login_required
@require_http_methods(["GET"])
def get_recent_requests(request):
    """AJAX endpoint to get recent requests"""
    if not request.user.is_student:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    recent_requests = ServiceRequest.objects.filter(
        student=request.user
    ).order_by('-created_at')[:5]
    
    requests_data = []
    for req in recent_requests:
        requests_data.append({
            'id': req.id,
            'title': req.title,
            'type': req.get_request_type_display(),
            'status': req.get_status_display(),
            'created_at': req.created_at.strftime('%b %d, %Y'),
            'url': f'/student/requests/{req.id}/'
        })
    
    return JsonResponse({'requests': requests_data})


@login_required
def documents(request):
    """View for student documents page"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    documents = StudentDocument.objects.filter(
        student=request.user
    ).order_by('-issued_date')
    
    context = {
        'documents': documents,
    }
    return render(request, 'student_portal/documents.html', context)


@login_required
def support(request):
    """View for support center page"""
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('accounts:login')
    
    tickets = SupportTicket.objects.filter(
        student=request.user
    ).order_by('-created_at')
    
    context = {
        'tickets': tickets,
    }
    return render(request, 'student_portal/support.html', context)
