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
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff_member:
            return '/staff/'
        else:
            return '/student/dashboard/'
    
    def form_invalid(self, form):
        messages.error(self.request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'تم تسجيل الخروج بنجاح.')
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
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
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
            messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)


@login_required
def digital_id_view(request):
    """Display digital ID page"""
    # Only allow students to access this view
    if request.user.user_type != 'student':
        messages.error(request, 'الوصول مرفوض. هذه الميزة متاحة للطلاب فقط.')
        return redirect('accounts:profile')
    
    # Generate QR code for the user
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
    
    # Convert to base64 for template
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'qr_code': f'data:image/png;base64,{qr_code_data}',
    }
    
    return render(request, 'accounts/digital_id.html', context)


@login_required
def student_id_card_view(request):
    """Display student ID card page"""
    # Only allow students to access this view
    if request.user.user_type != 'student':
        messages.error(request, 'الوصول مرفوض. هذه الميزة متاحة للطلاب فقط.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/student_id_card.html')


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
        messages.success(request, 'تم إعادة إنشاء الهوية الرقمية بنجاح!')
        return JsonResponse({'success': True, 'university_id': request.user.university_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def download_digital_id(request):
    """Download digital ID as PDF"""
    # Only allow students to download digital ID
    if request.user.user_type != 'student':
        messages.error(request, 'الوصول مرفوض. هذه الميزة متاحة للطلاب فقط.')
        return redirect('accounts:profile')
    
    try:
        # Create the HttpResponse object with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="digital_id_{request.user.username}.pdf"'
        
        # Create the PDF document
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#102A71')
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#102A71')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6
        )
        
        # Add title
        title = Paragraph("UNIVERSITY SERVICES<br/>Digital Student ID", title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Student Information Table
        student_data = [
            ['Student Information', ''],
            ['Full Name:', request.user.get_full_name() or request.user.username],
            ['University ID:', request.user.university_id],
            ['Email:', request.user.email],
            ['User Type:', request.user.user_type.title()],
            ['Program:', getattr(request.user, 'major', None) or 'Not Set'],
            ['Academic Level:', getattr(request.user, 'academic_level', None) or 'Not Set'],
            ['Enrollment Year:', getattr(request.user, 'enrollment_year', None) or 'Not Set'],
            ['Status:', 'Active'],
            ['Valid Until:', 'December 2025'],
            ['Generated:', datetime.now().strftime('%B %d, %Y at %I:%M %p')]
        ]
        
        # Create table
        table = Table(student_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#102A71')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 30))
        
        # Generate QR Code
        qr_data = {
            'university_id': request.user.university_id,
            'name': request.user.get_full_name(),
            'user_type': request.user.user_type,
            'username': request.user.username,
        }
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Add QR Code to PDF
        qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
        qr_table = Table([['QR Code for Verification', qr_image]], colWidths=[3*inch, 2.5*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 12),
        ]))
        
        elements.append(qr_table)
        elements.append(Spacer(1, 30))
        
        # Add security notice
        security_notice = Paragraph(
            "<b>Security Notice:</b> This digital ID is official university property. "
            "Do not share your QR code with unauthorized persons. Report any suspicious activity immediately. "
            "This document is valid only when accompanied by proper photo identification.",
            normal_style
        )
        elements.append(security_notice)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
         
    except Exception as e:
         # If PDF generation fails, return an error response
        response = HttpResponse(content_type='text/plain')
        response.write(f'Error generating PDF: {str(e)}')
        response.status_code = 500
        return response


@login_required
def download_id_card(request):
    """Download student ID card as a modern, stylish PDF"""
    # Only allow students to download ID card
    if request.user.user_type != 'student':
        messages.error(request, 'الوصول مرفوض. هذه الميزة متاحة للطلاب فقط.')
        return redirect('accounts:profile')
    
    try:
        # --- Basic Setup ---
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_id_card_{request.user.username}.pdf"'
        
        buffer = BytesIO()
        
        # Standard credit card size
        card_width = 3.375 * inch
        card_height = 2.125 * inch
        
        c = canvas.Canvas(buffer, pagesize=(card_width, card_height))

        # --- Color Palette ---
        color_primary = colors.HexColor('#003366') # Deep Blue
        color_secondary = colors.HexColor('#4A90E2') # Lighter Blue
        color_text = colors.white
        color_dark_text = colors.HexColor('#2c3e50') # Dark Slate

        # --- Draw Background Gradient & Border ---
        # This loop creates a vertical gradient
        for i in range(int(card_height)):
            ratio = i / card_height
            # Interpolate color from primary to secondary
            r = (1 - ratio) * color_primary.red + ratio * color_secondary.red
            g = (1 - ratio) * color_primary.green + ratio * color_secondary.green
            b = (1 - ratio) * color_primary.blue + ratio * color_secondary.blue
            c.setStrokeColorRGB(r, g, b)
            c.line(0, i, card_width, i)
        
        # Add a rounded border for a modern look
        c.setStrokeColor(colors.HexColor('#ffffff'))
        c.setLineWidth(2)
        c.roundRect(1, 1, card_width - 2, card_height - 2, radius=10, stroke=1, fill=0)

        # --- Header: University Logo & Title ---
        # Placeholder for a university logo
        c.setFillColor(colors.white)
        c.setStrokeColor(colors.white)
        c.circle(0.4 * inch, card_height - 0.4 * inch, 0.15 * inch, fill=1)
        c.setFillColor(color_primary)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(0.4 * inch, card_height - 0.425 * inch, "U")

        c.setFillColor(color_text)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.7 * inch, card_height - 0.35 * inch, "Global University")
        c.setFont("Helvetica", 7)
        c.drawString(0.7 * inch, card_height - 0.5 * inch, "Student Identification")

        # --- Profile Picture ---
        photo_size = 0.85 * inch
        photo_x = 0.3 * inch
        photo_y = card_height - 0.7 * inch - photo_size
        
        # Draw a white background for the photo
        c.setFillColor(colors.white)
        c.roundRect(photo_x - 2, photo_y - 2, photo_size + 4, photo_size + 4, radius=6, stroke=0, fill=1)

        if request.user.profile_picture:
            try:
                profile_image = ImageReader(request.user.profile_picture)
                c.drawImage(profile_image, photo_x, photo_y, width=photo_size, height=photo_size, mask='auto', preserveAspectRatio=True)
            except Exception:
                # Fallback if image fails to load
                c.setFillColor(colors.lightgrey)
                c.roundRect(photo_x, photo_y, photo_size, photo_size, radius=5, stroke=0, fill=1)
                c.setFillColor(color_dark_text)
                c.setFont("Helvetica", 8)
                c.drawCentredString(photo_x + photo_size / 2, photo_y + photo_size / 2, "NO IMG")
        else:
            # Placeholder if no image exists
            c.setFillColor(colors.lightgrey)
            c.roundRect(photo_x, photo_y, photo_size, photo_size, radius=5, stroke=0, fill=1)
            c.setFillColor(color_dark_text)
            c.setFont("Helvetica", 8)
            c.drawCentredString(photo_x + photo_size / 2, photo_y + photo_size / 2, "PHOTO")

        # --- Student Information ---
        info_x = photo_x + photo_size + 0.2 * inch
        info_y_start = card_height - 0.8 * inch
        line_height = 0.18 * inch

        c.setFillColor(color_text)
        
        # Full Name
        c.setFont("Helvetica-Bold", 12)
        c.drawString(info_x, info_y_start, request.user.get_full_name() or request.user.username)
        
        # University ID
        c.setFont("Helvetica", 8)
        c.drawString(info_x, info_y_start - line_height, f"ID: {request.user.university_id}")
        
        # Program
        program = getattr(request.user, 'major', None) or 'N/A'
        c.drawString(info_x, info_y_start - 2 * line_height, f"Program: {program}")
        
        # Valid Until
        c.setFont("Helvetica-Oblique", 7)
        c.drawString(info_x, 0.3 * inch, "Valid Until: December 2025")


        # --- QR Code ---
        qr_data = json.dumps({
            'university_id': request.user.university_id,
            'name': request.user.get_full_name(),
            'username': request.user.username,
        })
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        qr_image_reader = ImageReader(qr_buffer)
        qr_size = 0.75 * inch
        # Align QR code with photo position
        qr_x = card_width - qr_size - 0.2 * inch
        qr_y = photo_y  # Align with photo's Y position
        c.drawImage(qr_image_reader, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

        # --- Start Back Side of Card ---
        c.showPage()  # Start new page for back side
        
        # --- Back Side Background Gradient ---
        for i in range(int(card_height)):
            ratio = i / card_height
            # Lighter gradient for back side
            r = (1 - ratio) * color_secondary.red + ratio * 0.9
            g = (1 - ratio) * color_secondary.green + ratio * 0.9
            b = (1 - ratio) * color_secondary.blue + ratio * 0.9
            c.setStrokeColorRGB(r, g, b)
            c.line(0, i, card_width, i)
        
        # Add border
        c.setStrokeColor(colors.HexColor('#ffffff'))
        c.setLineWidth(2)
        c.roundRect(1, 1, card_width - 2, card_height - 2, radius=10, stroke=1, fill=0)

        # --- Back Side Header ---
        c.setFillColor(color_primary)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(card_width / 2, card_height - 0.3 * inch, "STUDENT IDENTIFICATION CARD")
        
        # --- Terms and Conditions ---
        c.setFillColor(color_dark_text)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(0.2 * inch, card_height - 0.6 * inch, "TERMS OF USE:")
        
        terms_text = [
            "• This card is property of Global University",
            "• Must be carried at all times on campus",
            "• Report lost or stolen cards immediately",
            "• Non-transferable - for authorized use only",
            "• Valid for current academic year only"
        ]
        
        c.setFont("Helvetica", 6)
        y_pos = card_height - 0.75 * inch
        for term in terms_text:
            c.drawString(0.25 * inch, y_pos, term)
            y_pos -= 0.12 * inch
        
        # --- Emergency Contact ---
        c.setFont("Helvetica-Bold", 8)
        c.drawString(0.2 * inch, y_pos - 0.1 * inch, "EMERGENCY CONTACT:")
        c.setFont("Helvetica", 7)
        c.drawString(0.2 * inch, y_pos - 0.25 * inch, "Campus Security: (555) 123-4567")
        c.drawString(0.2 * inch, y_pos - 0.37 * inch, "Student Services: (555) 123-4568")
        
        # --- Validity Information ---
        c.setFont("Helvetica-Bold", 7)
        c.drawString(0.2 * inch, 0.4 * inch, "VALID UNTIL: December 2025")
        
        # --- Card Number ---
        c.setFont("Helvetica", 6)
        card_number = f"CARD #{request.user.university_id}-{datetime.now().year}"
        c.drawRightString(card_width - 0.2 * inch, 0.2 * inch, card_number)
        
        # --- University Logo/Seal (placeholder) ---
        c.setFillColor(colors.lightgrey)
        c.setStrokeColor(color_primary)
        c.circle(card_width - 0.6 * inch, 0.6 * inch, 0.25 * inch, fill=1, stroke=1)
        c.setFillColor(color_primary)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(card_width - 0.6 * inch, 0.58 * inch, "GLOBAL")
        c.setFont("Helvetica", 6)
        c.drawCentredString(card_width - 0.6 * inch, 0.52 * inch, "UNIVERSITY")

        # --- Finalize PDF ---
        c.save()
        
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
        
    except Exception as e:
        # Error handling
        response = HttpResponse(content_type='text/plain')
        response.write(f'Error generating ID card PDF: {str(e)}')
        response.status_code = 500
        return response