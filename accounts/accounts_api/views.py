from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserDetailSerializer
from ..models import User
from django.http import HttpResponse, JsonResponse
from io import BytesIO
import logging
import os
import json
import qrcode
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for mobile app login"""
    logger.info(f"Login attempt from IP: {request.META.get('REMOTE_ADDR')}")
    logger.info(f"Request data: {request.data}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Log successful login
        logger.info(f"Successful login for user: {user.username} ({user.university_id})")
        
        # Prepare user data
        user_serializer = UserDetailSerializer(user)
        
        response_data = {
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user': user_serializer.data
        }
        
        logger.info(f"Sending response: {response_data}")
        
        return Response(response_data, status=status.HTTP_200_OK)
    else:
        logger.warning(f"Failed login attempt from IP: {request.META.get('REMOTE_ADDR')}")
        logger.warning(f"Serializer errors: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'بيانات الاعتماد غير صحيحة',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API endpoint for mobile app logout"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logger.info(f"User logged out: {request.user.username}")
        return Response({
            'success': True,
            'message': 'تم تسجيل الخروج بنجاح'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Logout error for user {request.user.username}: {str(e)}")
        return Response({
            'success': False,
            'message': 'فشل في تسجيل الخروج'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    """API endpoint to get current user profile"""
    serializer = UserDetailSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_refresh_token(request):
    """API endpoint to refresh JWT token"""
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'رمز التحديث مطلوب'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        access_token = token.access_token
        
        return Response({
            'success': True,
            'access_token': str(access_token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'رمز التحديث غير صحيح'
        }, status=status.HTTP_401_UNAUTHORIZED)


def process_arabic_text(text):
    """Process Arabic text for PDF rendering"""
    try:
        from arabic_reshaper import reshape
        from bidi.algorithm import get_display
        reshaped_text = reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except ImportError:
        # Fallback if arabic_reshaper is not available
        return text


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes

@csrf_exempt
def api_download_id_card(request):
    """API endpoint for downloading student ID card PDF"""
    # Manual JWT authentication
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Get the authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({
            'success': False,
            'message': 'رمز التفويض مطلوب',
            'error_code': 'AUTHENTICATION_REQUIRED'
        }, status=401)
    
    # Extract and validate the token
    token = auth_header.split(' ')[1]
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model
        
        # Validate the token
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        
        # Get the user
        User = get_user_model()
        user = User.objects.get(id=user_id)
        request.user = user
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'رمز التفويض غير صحيح',
            'error_code': 'INVALID_TOKEN'
        }, status=401)
    
    # Only allow students to download ID card
    if request.user.user_type != 'student':
        return JsonResponse({
            'success': False,
            'message': 'الوصول مرفوض. هذه الميزة متاحة للطلاب فقط.',
            'error_code': 'ACCESS_DENIED'
        }, status=403)
    
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
        
        # --- Finalize PDF ---
        c.save()
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Create HTTP response with PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_id_card_{request.user.username}.pdf"'
        response['Content-Length'] = len(pdf_content)
        
        logger.info(f"Student ID card downloaded successfully for user: {request.user.username}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating ID card PDF for user {request.user.username}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'خطأ في إنشاء ملف PDF للهوية الطلابية: {str(e)}',
            'error_code': 'PDF_GENERATION_ERROR'
        }, status=500)