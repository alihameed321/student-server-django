from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
import qrcode
from io import BytesIO
from django.core.files import File


class User(AbstractUser):
    """نموذج المستخدم المخصص لطلاب وموظفي الجامعة"""
    
    USER_TYPES = (
        ('student', _('طالب')),
        ('staff', _('موظف')),
        ('admin', _('مدير')),
    )
    
    university_id = models.CharField(
        max_length=20, 
        unique=True, 
        default='MY-UNIV-001',
        verbose_name=_('الرقم الجامعي'),
        help_text=_('الرقم الجامعي الفريد للمستخدم')
    )
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPES, 
        default='student',
        verbose_name=_('نوع المستخدم'),
        help_text=_('نوع المستخدم في النظام')
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True,
        verbose_name=_('رقم الهاتف'),
        help_text=_('رقم الهاتف المحمول')
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('تاريخ الميلاد'),
        help_text=_('تاريخ ميلاد المستخدم')
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True,
        verbose_name=_('صورة الملف الشخصي'),
        help_text=_('صورة شخصية للمستخدم')
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/', 
        null=True, 
        blank=True,
        verbose_name=_('رمز الاستجابة السريعة'),
        help_text=_('رمز QR للهوية الرقمية')
    )
    
    # حقول خاصة بالطلاب
    major = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('التخصص'),
        help_text=_('تخصص الطالب الأكاديمي')
    )
    academic_level = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('المستوى الأكاديمي'),
        help_text=_('المستوى الدراسي الحالي')
    )
    enrollment_year = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name=_('سنة التسجيل'),
        help_text=_('السنة التي تم فيها تسجيل الطالب')
    )
    
    # حقول خاصة بالموظفين
    department = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('القسم'),
        help_text=_('القسم الذي يعمل به الموظف')
    )
    position = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('المنصب'),
        help_text=_('منصب الموظف في الجامعة')
    )
    
    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        ordering = ['university_id']
    
    def __str__(self):
        return f"{self.university_id} - {self.get_full_name()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Temporarily disabled QR code generation to avoid recursion error
        # self.generate_qr_code()
    
    def generate_qr_code(self):
        """Generate QR code for the user's digital ID"""
        qr_data = f"University ID: {self.university_id}\nName: {self.get_full_name()}\nType: {self.user_type}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.university_id}.png'
        filebuffer = File(buffer, name=filename)
        self.qr_code.save(filename, filebuffer)
        buffer.close()
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_staff_member(self):
        return self.user_type in ['staff', 'admin']


class StudentProfile(models.Model):
    """الملف الشخصي الموسع للطلاب"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        verbose_name=_('المستخدم'),
        help_text=_('المستخدم المرتبط بهذا الملف الشخصي')
    )
    student_id_number = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_('رقم الطالب'),
        help_text=_('رقم الطالب الفريد')
    )
    gpa = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_('المعدل التراكمي'),
        help_text=_('المعدل التراكمي للطالب')
    )
    total_credits = models.IntegerField(
        default=0,
        verbose_name=_('إجمالي الساعات المعتمدة'),
        help_text=_('العدد الإجمالي للساعات المعتمدة المكتسبة')
    )
    graduation_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('تاريخ التخرج'),
        help_text=_('تاريخ التخرج المتوقع أو الفعلي')
    )
    emergency_contact_name = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('اسم جهة الاتصال في حالات الطوارئ'),
        help_text=_('اسم الشخص المراد الاتصال به في حالات الطوارئ')
    )
    emergency_contact_phone = models.CharField(
        max_length=15, 
        blank=True,
        verbose_name=_('هاتف جهة الاتصال في حالات الطوارئ'),
        help_text=_('رقم هاتف جهة الاتصال في حالات الطوارئ')
    )
    
    class Meta:
        verbose_name = _('الملف الشخصي للطالب')
        verbose_name_plural = _('الملفات الشخصية للطلاب')
        ordering = ['student_id_number']
    
    def __str__(self):
        return f"الملف الشخصي للطالب - {self.user.get_full_name()}"


class StaffProfile(models.Model):
    """الملف الشخصي الموسع لأعضاء الهيئة الإدارية"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='staff_profile',
        verbose_name=_('المستخدم'),
        help_text=_('المستخدم المرتبط بهذا الملف الشخصي')
    )
    employee_id = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name=_('رقم الموظف'),
        help_text=_('رقم الموظف الفريد')
    )
    hire_date = models.DateField(
        verbose_name=_('تاريخ التوظيف'),
        help_text=_('تاريخ بداية العمل في الجامعة')
    )
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_('الراتب'),
        help_text=_('الراتب الشهري للموظف')
    )
    permissions = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name=_('الصلاحيات'),
        help_text=_('صلاحيات الموظف في النظام')
    )
    
    class Meta:
        verbose_name = _('الملف الشخصي للموظف')
        verbose_name_plural = _('الملفات الشخصية للموظفين')
        ordering = ['employee_id']
    
    def __str__(self):
        return f"الملف الشخصي للموظف - {self.user.get_full_name()}"
