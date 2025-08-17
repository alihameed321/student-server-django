from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import User, StudentProfile, StaffProfile
from .forms import CustomUserCreationForm, ProfileUpdateForm
import json
import qrcode
from io import BytesIO
import base64


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return '/staff/dashboard/'
        else:
            return '/student/dashboard/'
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    """Display user profile"""
    profile = None
    if request.user.is_student:
        try:
            profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            profile = None
    elif request.user.is_staff_member:
        try:
            profile = request.user.staff_profile
        except StaffProfile.DoesNotExist:
            profile = None
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)


@login_required
def digital_id_view(request):
    """Display digital ID"""
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/digital_id.html', context)


@login_required
def generate_qr_code(request):
    """Generate QR code for digital ID"""
    # Generate QR code data
    qr_data = {
        'university_id': request.user.university_id,
        'name': request.user.get_full_name(),
        'user_type': request.user.user_type,
        'username': request.user.username,
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return JsonResponse({
        'qr_code': f'data:image/png;base64,{img_str}',
        'data': qr_data
    })


@login_required
@require_http_methods(["POST"])
def regenerate_digital_id(request):
    """Regenerate digital ID"""
    try:
        # Regenerate QR code
        request.user.generate_qr_code()
        messages.success(request, 'Digital ID regenerated successfully!')
        return JsonResponse({'success': True, 'university_id': request.user.university_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def download_digital_id(request):
    """Download digital ID as PDF"""
    # This would generate a PDF version of the digital ID
    # For now, return a simple response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="digital_id_{request.user.username}.pdf"'
    
    # TODO: Implement PDF generation
    response.write(b'PDF generation not implemented yet')
    
    return response
