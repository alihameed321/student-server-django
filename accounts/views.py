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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Try to import Arabic text processing libraries
try:
    from bidi.algorithm import get_display
    from arabic_reshaper import reshape
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    
def process_arabic_text(text):
    """Process Arabic text for proper display in PDF"""
    if not ARABIC_SUPPORT:
        return text
    try:
        # Reshape Arabic text to connect letters properly
        reshaped_text = reshape(text)
        # Apply bidirectional algorithm for proper RTL display
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except:
        return text


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
        # Register Arabic font if available
        try:
            # Try to find proper Arabic fonts that support text shaping
            font_paths = [
                'C:/Windows/Fonts/tahoma.ttf',  # Windows - better Arabic support
                'C:/Windows/Fonts/calibri.ttf',  # Windows - good Arabic support
                'C:/Windows/Fonts/arial.ttf',  # Windows fallback
                '/System/Library/Fonts/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Linux
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Arabic', font_path))
                    break
            else:
                # Fallback to default font
                pass
        except:
            # If font registration fails, continue with default
            pass
        
        # Create the HttpResponse object with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="digital_id_{request.user.username}.pdf"'
        
        # Create the PDF document
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles with Arabic support
        styles = getSampleStyleSheet()
        
        # Try to use Arabic font, fallback to Helvetica
        font_name = 'Arabic' if 'Arabic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#102A71'),
            fontName=font_name
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#102A71'),
            fontName=font_name
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            fontName=font_name,
            alignment=TA_RIGHT
        )
        
        # Add university logo
        try:
            # Use the specific logo path provided by user
            logo_path = 'd:/student/student-server-django/static/images/logo.png'
            if os.path.exists(logo_path):
                logo_image = Image(logo_path, width=1*inch, height=1*inch)
                logo_table = Table([[logo_image]], colWidths=[6*inch])
                logo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ]))
                elements.append(logo_table)
                elements.append(Spacer(1, 10))
        except Exception:
            # Continue without logo if there's an error
            pass
        
        # Add title in Arabic
        title = Paragraph(process_arabic_text("الجامعة اليمنية<br/>بطاقة الهوية الطلابية الرقمية"), title_style)
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Student Information Table in Arabic
        student_data = [
            [process_arabic_text('معلومات الطالب'), ''],
            [process_arabic_text('الاسم الكامل:'), process_arabic_text(request.user.get_full_name() or request.user.username)],
            [process_arabic_text('الرقم الجامعي:'), request.user.university_id],
            [process_arabic_text('البريد الإلكتروني:'), request.user.email],
            [process_arabic_text('نوع المستخدم:'), process_arabic_text('طالب' if request.user.user_type == 'student' else request.user.user_type)],
            [process_arabic_text('البرنامج:'), process_arabic_text(getattr(request.user, 'major', None) or 'غير محدد')],
            [process_arabic_text('المستوى الأكاديمي:'), process_arabic_text(getattr(request.user, 'academic_level', None) or 'غير محدد')],
            [process_arabic_text('سنة التسجيل:'), process_arabic_text(getattr(request.user, 'enrollment_year', None) or 'غير محدد')],
            [process_arabic_text('الحالة:'), process_arabic_text('نشط')],
            [process_arabic_text('صالحة حتى:'), process_arabic_text('ديسمبر 2025')],
            [process_arabic_text('تاريخ الإنشاء:'), process_arabic_text(datetime.now().strftime('%d/%m/%Y الساعة %H:%M'))]
        ]
        
        # Create table with Arabic support
        table = Table(student_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#102A71')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),  # RTL alignment
            ('FONTNAME', (0, 0), (1, 0), font_name + '-Bold' if font_name == 'Helvetica' else font_name),
            ('FONTSIZE', (0, 0), (1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), font_name + '-Bold' if font_name == 'Helvetica' else font_name),
            ('FONTNAME', (1, 1), (1, -1), font_name),  # Data column uses regular font
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
        
        # Add QR Code to PDF with Arabic label
        qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
        qr_table = Table([[process_arabic_text('رمز الاستجابة السريعة للتحقق'), qr_image]], colWidths=[3*inch, 2.5*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),  # RTL alignment
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, 0), font_name + '-Bold' if font_name == 'Helvetica' else font_name),
            ('FONTSIZE', (0, 0), (0, 0), 12),
        ]))
        
        elements.append(qr_table)
        elements.append(Spacer(1, 30))
        
        # Add security notice in Arabic
        security_notice = Paragraph(
            process_arabic_text("<b>تنبيه أمني:</b> هذه البطاقة الرقمية ملكية رسمية للجامعة. "
            "لا تشارك رمز الاستجابة السريعة مع أشخاص غير مخولين. أبلغ عن أي نشاط مشبوه فوراً. "
            "هذه الوثيقة صالحة فقط عند مرافقتها بهوية شخصية صحيحة مع صورة."),
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
        # Register Arabic font if available
        try:
            # Try to find proper Arabic fonts that support text shaping
            font_paths = [
                'C:/Windows/Fonts/tahoma.ttf',  # Windows - better Arabic support
                'C:/Windows/Fonts/calibri.ttf',  # Windows - good Arabic support
                'C:/Windows/Fonts/arial.ttf',  # Windows fallback
                '/System/Library/Fonts/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Linux
            ]
            
            bold_font_paths = [
                'C:/Windows/Fonts/tahomabd.ttf',  # Windows Tahoma Bold
                'C:/Windows/Fonts/calibrib.ttf',  # Windows Calibri Bold
                'C:/Windows/Fonts/arialbd.ttf',  # Windows Arial Bold
                '/System/Library/Fonts/Arial Bold.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',  # Linux
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',  # Linux
            ]
            
            # Register regular font
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Arabic', font_path))
                    break
            
            # Register bold font
            for font_path in bold_font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
                    break
            else:
                # If no bold font found, use regular font for bold
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
                        break
        except:
            pass
        
        # --- Basic Setup ---
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_id_card_{request.user.username}.pdf"'
        
        buffer = BytesIO()
        
        # Standard credit card size
        card_width = 3.375 * inch
        card_height = 2.125 * inch
        
        c = canvas.Canvas(buffer, pagesize=(card_width, card_height))
        
        # Determine font to use
        font_name = 'Arabic' if 'Arabic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'Arabic-Bold' if 'Arabic-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

        # --- Color Palette ---
        color_primary = colors.HexColor('#003366') # Deep Blue
        color_secondary = colors.HexColor('#4A90E2') # Lighter Blue
        color_text = colors.white
        color_dark_text = colors.HexColor('#2c3e50') # Dark Slate

        # --- Draw Professional Blue Gradient Background ---
        # Create smooth vertical gradient from deep blue to lighter blue
        gradient_steps = 100
        step_height = card_height / gradient_steps
        
        for i in range(gradient_steps):
            ratio = i / gradient_steps
            # Smooth interpolation between primary and secondary colors
            r = (1 - ratio) * color_primary.red + ratio * color_secondary.red
            g = (1 - ratio) * color_primary.green + ratio * color_secondary.green
            b = (1 - ratio) * color_primary.blue + ratio * color_secondary.blue
            c.setFillColorRGB(r, g, b)
            c.rect(0, i * step_height, card_width, step_height, fill=1, stroke=0)
        
        # Add a rounded border for a modern look
        c.setStrokeColor(colors.HexColor('#ffffff'))
        c.setLineWidth(2)
        c.roundRect(1, 1, card_width - 2, card_height - 2, radius=10, stroke=1, fill=0)

        # --- Header: University Title and Logo (logo to the right of title) ---
        c.setFillColor(color_text)
        c.setFont(font_bold, 10)
        # RTL text positioning for Arabic - position text more to the left to make room for logo
        c.drawRightString(card_width - 0.6 * inch, card_height - 0.35 * inch, process_arabic_text("الجامعة اليمنية"))
        c.setFont(font_name, 7)
        c.drawRightString(card_width - 0.6 * inch, card_height - 0.5 * inch, process_arabic_text("بطاقة الهوية الطلابية"))
        
        # Try to load university logo (positioned to the right of the text)
        try:
            # Use the specific logo path provided by user
            logo_path = 'd:/student/student-server-django/static/images/logo.png'
            if os.path.exists(logo_path):
                c.drawImage(logo_path, card_width - 0.45 * inch, card_height - 0.55 * inch, width=0.3 * inch, height=0.3 * inch, preserveAspectRatio=True)
            else:
                # Fallback circle if logo not found
                c.setFillColor(colors.white)
                c.setStrokeColor(colors.white)
                c.circle(card_width - 0.3 * inch, card_height - 0.4 * inch, 0.15 * inch, fill=1)
                c.setFillColor(color_primary)
                c.setFont(font_bold, 10)
                c.drawCentredString(card_width - 0.3 * inch, card_height - 0.425 * inch, process_arabic_text("ج"))
        except Exception:
            # Fallback circle if any error
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.white)
            c.circle(card_width - 0.3 * inch, card_height - 0.4 * inch, 0.15 * inch, fill=1)
            c.setFillColor(color_primary)
            c.setFont(font_bold, 10)
            c.drawCentredString(card_width - 0.3 * inch, card_height - 0.425 * inch, process_arabic_text("ج"))

        # --- Profile Picture ---
        photo_size = 0.85 * inch
        photo_x = 0.3 * inch
        photo_y = card_height - 0.6 * inch - photo_size
        
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
                c.setFont(font_name, 8)
                c.drawCentredString(photo_x + photo_size / 2, photo_y + photo_size / 2, process_arabic_text("لا توجد صورة"))
        else:
            # Placeholder if no image exists
            c.setFillColor(colors.lightgrey)
            c.roundRect(photo_x, photo_y, photo_size, photo_size, radius=5, stroke=0, fill=1)
            c.setFillColor(color_dark_text)
            c.setFont(font_name, 8)
            c.drawCentredString(photo_x + photo_size / 2, photo_y + photo_size / 2, process_arabic_text("صورة"))

        # --- Student Information ---
        info_x_right = card_width - 0.2 * inch  # Right edge for RTL text
        info_y_start = card_height - 0.8 * inch
        line_height = 0.18 * inch

        c.setFillColor(color_text)
        
        # Full Name (RTL positioning)
        c.setFont(font_bold, 12)
        full_name = process_arabic_text(request.user.get_full_name() or request.user.username)
        c.drawRightString(info_x_right, info_y_start, full_name)
        
        # University ID
        c.setFont(font_name, 8)
        c.drawRightString(info_x_right, info_y_start - line_height, process_arabic_text(f"الرقم الجامعي: {request.user.university_id}"))
        
        # Program
        program = getattr(request.user, 'major', None) or 'غير محدد'
        c.drawRightString(info_x_right, info_y_start - 2 * line_height, process_arabic_text(f"التخصص: {program}"))
        
        # Valid Until
        c.setFont(font_name, 7)
        c.drawRightString(info_x_right, 0.3 * inch, process_arabic_text("صالحة حتى: نهاية الفصل الدراسي"))


        # --- QR Code (positioned under student photo) ---
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
        qr_size = 0.5 * inch  # Smaller QR code to fit better
        # Position QR code under the photo, centered
        qr_x = photo_x + (photo_size - qr_size) / 2  # Center under photo
        qr_y = photo_y - qr_size - 0.05 * inch  # Below photo with smaller gap
        c.drawImage(qr_image_reader, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

        # --- Start Back Side of Card ---
        c.showPage()  # Start new page for back side
        
        # --- Back Side Professional Blue Gradient ---
        # Create smooth vertical gradient with lighter tones
        gradient_steps = 100
        step_height = card_height / gradient_steps
        
        for i in range(gradient_steps):
            ratio = i / gradient_steps
            # Lighter gradient for back side - from secondary to light blue
            light_blue = colors.HexColor('#87CEEB')  # Sky blue
            r = (1 - ratio) * color_secondary.red + ratio * light_blue.red
            g = (1 - ratio) * color_secondary.green + ratio * light_blue.green
            b = (1 - ratio) * color_secondary.blue + ratio * light_blue.blue
            c.setFillColorRGB(r, g, b)
            c.rect(0, i * step_height, card_width, step_height, fill=1, stroke=0)
        
        # Add border
        c.setStrokeColor(colors.HexColor('#ffffff'))
        c.setLineWidth(2)
        c.roundRect(1, 1, card_width - 2, card_height - 2, radius=10, stroke=1, fill=0)

        # --- Back Side Header with Logo Above Text ---
        # Try to load university logo (positioned above the text)
        try:
            # Use the specific logo path provided by user
            logo_path = 'd:/student/student-server-django/static/images/logo.png'
            if os.path.exists(logo_path):
                c.drawImage(logo_path, card_width / 2 - 0.15 * inch, card_height - 0.4 * inch, width=0.3 * inch, height=0.3 * inch, preserveAspectRatio=True)
            else:
                # Fallback circle if logo not found
                c.setFillColor(colors.white)
                c.setStrokeColor(color_primary)
                c.circle(card_width / 2, card_height - 0.25 * inch, 0.15 * inch, fill=1, stroke=1)
                c.setFillColor(color_primary)
                c.setFont(font_bold, 8)
                c.drawCentredString(card_width / 2, card_height - 0.27 * inch, process_arabic_text("ج"))
        except Exception:
            # Fallback circle if any error
            c.setFillColor(colors.white)
            c.setStrokeColor(color_primary)
            c.circle(card_width / 2, card_height - 0.25 * inch, 0.15 * inch, fill=1, stroke=1)
            c.setFillColor(color_primary)
            c.setFont(font_bold, 8)
            c.drawCentredString(card_width / 2, card_height - 0.27 * inch, process_arabic_text("ج"))
        
        # Header text below logo
        c.setFillColor(color_primary)
        c.setFont(font_bold, 10)
        c.drawCentredString(card_width / 2, card_height - 0.55 * inch, process_arabic_text("الجامعة اليمنية - بطاقة الهوية الطلابية"))
        
        # --- Terms and Conditions ---
        c.setFillColor(color_dark_text)
        c.setFont(font_bold, 8)
        c.drawRightString(card_width - 0.2 * inch, card_height - 0.75 * inch, process_arabic_text("شروط الاستخدام:"))
        
        terms_text = [
            process_arabic_text("• هذه البطاقة ملك للخدمات الجامعية"),
            process_arabic_text("• يجب حملها في جميع الأوقات داخل الحرم الجامعي"),
            process_arabic_text("• أبلغ عن البطاقات المفقودة أو المسروقة فوراً"),
            process_arabic_text("• غير قابلة للتحويل - للاستخدام المخول فقط"),
            process_arabic_text("• صالحة للسنة الأكاديمية الحالية فقط")
        ]
        
        c.setFont(font_name, 6)
        y_pos = card_height - 0.9 * inch
        for term in terms_text:
            c.drawRightString(card_width - 0.25 * inch, y_pos, term)
            y_pos -= 0.12 * inch
        
        # --- Emergency Contact ---
        c.setFont(font_bold, 8)
        c.drawRightString(card_width - 0.2 * inch, y_pos - 0.1 * inch, process_arabic_text("جهات الاتصال الطارئة:"))
        c.setFont(font_name, 7)
        c.drawRightString(card_width - 0.2 * inch, y_pos - 0.25 * inch, process_arabic_text("أمن الحرم الجامعي: (555) 123-4567"))
        c.drawRightString(card_width - 0.2 * inch, y_pos - 0.37 * inch, process_arabic_text("خدمات الطلاب: (555) 123-4568"))
        
        # --- Validity Information ---
        c.setFont(font_bold, 7)
        c.setFillColor(colors.red)
        validity_text = process_arabic_text("صالحة حتى: نهاية الفصل الدراسي")
        text_width = c.stringWidth(validity_text, font_bold, 7)
        c.drawString(card_width - text_width - 0.2 * inch, y_pos - 0.5 * inch, validity_text)
        c.setFillColor(colors.black)  # Reset color to black
        
        # --- Card Number ID on next line ---
        # c.setFont(font_name, 6)
        # card_number = process_arabic_text(f"رقم البطاقة #{request.user.university_id}-{datetime.now().year}")
        # c.drawString(0.2 * inch, 0.25 * inch, card_number)
        
        # Logo is now at the top of the back side, no need for duplicate

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