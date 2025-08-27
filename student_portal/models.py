from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ServiceRequest(models.Model):
    """نموذج طلبات الخدمات الطلابية"""
    
    REQUEST_TYPES = (
        ('enrollment_certificate', _('شهادة قيد')),
        ('schedule_modification', _('تعديل الجدول الدراسي')),
        ('semester_postponement', _('تأجيل الفصل الدراسي')),
        ('transcript', _('كشف الدرجات الرسمي')),
        ('graduation_certificate', _('شهادة التخرج')),
        ('other', _('أخرى')),
    )
    
    STATUS_CHOICES = (
        ('pending', _('في انتظار المراجعة')),
        ('in_review', _('قيد المراجعة')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('completed', _('مكتمل')),
        ('more_info_needed', _('يحتاج معلومات إضافية')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='service_requests',
        verbose_name=_('الطالب'),
        help_text=_('الطالب الذي قدم الطلب')
    )
    request_type = models.CharField(
        max_length=30, 
        choices=REQUEST_TYPES,
        verbose_name=_('نوع الطلب'),
        help_text=_('نوع الخدمة المطلوبة')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان الطلب'),
        help_text=_('عنوان مختصر للطلب')
    )
    description = models.TextField(
        verbose_name=_('وصف الطلب'),
        help_text=_('وصف تفصيلي للطلب')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('حالة الطلب'),
        help_text=_('الحالة الحالية للطلب')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء الطلب')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث'),
        help_text=_('تاريخ ووقت آخر تحديث')
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='processed_requests',
        verbose_name=_('تمت معالجته بواسطة'),
        help_text=_('الموظف الذي عالج الطلب')
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_('سبب الرفض'),
        help_text=_('سبب رفض الطلب إن وجد')
    )
    additional_info_request = models.TextField(
        blank=True,
        verbose_name=_('طلب معلومات إضافية'),
        help_text=_('المعلومات الإضافية المطلوبة من الطالب')
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name=_('الأولوية'),
        help_text=_('أولوية معالجة الطلب')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('طلب خدمة')
        verbose_name_plural = _('طلبات الخدمات')
    
    def __str__(self):
        return f"{self.student.university_id} - {self.get_request_type_display()}"
    
    @property
    def status_icon(self):
        icons = {
            'pending': '⏳',
            'in_review': '👀',
            'approved': '✅',
            'rejected': '❌',
            'completed': '🎉',
            'more_info_needed': '❓',
        }
        return icons.get(self.status, '📄')


class RequestDocument(models.Model):
    """المستندات المرفقة بطلبات الخدمات"""
    
    request = models.ForeignKey(
        ServiceRequest, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name=_('طلب الخدمة'),
        help_text=_('طلب الخدمة المرتبط بهذا المستند')
    )
    document = models.FileField(
        upload_to='request_documents/',
        verbose_name=_('المستند'),
        help_text=_('ملف المستند المرفق')
    )
    document_name = models.CharField(
        max_length=200,
        verbose_name=_('اسم المستند'),
        help_text=_('اسم المستند المرفق')
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الرفع'),
        help_text=_('تاريخ ووقت رفع المستند')
    )
    
    class Meta:
        verbose_name = _('مستند الطلب')
        verbose_name_plural = _('مستندات الطلبات')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.request} - {self.document_name}"


class StudentDocument(models.Model):
    """المستندات الرسمية الصادرة للطلاب"""
    
    DOCUMENT_TYPES = (
        ('enrollment_certificate', _('شهادة قيد')),
        ('transcript', _('كشف الدرجات الرسمي')),
        ('graduation_certificate', _('شهادة التخرج')),
        ('payment_receipt', _('إيصال دفع')),
        ('other', _('مستند آخر')),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name=_('الطالب'),
        help_text=_('الطالب المالك للمستند')
    )
    document_type = models.CharField(
        max_length=30, 
        choices=DOCUMENT_TYPES,
        verbose_name=_('نوع المستند'),
        help_text=_('نوع المستند أو الشهادة')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('عنوان المستند'),
        help_text=_('عنوان أو اسم المستند')
    )
    document_file = models.FileField(
        upload_to='student_documents/',
        verbose_name=_('ملف المستند'),
        help_text=_('ملف المستند المرفق')
    )
    issued_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإصدار'),
        help_text=_('تاريخ ووقت إصدار المستند')
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='issued_documents',
        verbose_name=_('أصدر بواسطة'),
        help_text=_('الموظف الذي أصدر المستند')
    )
    is_official = models.BooleanField(
        default=True,
        verbose_name=_('رسمي'),
        help_text=_('هل المستند رسمي')
    )
    download_count = models.IntegerField(
        default=0,
        verbose_name=_('عدد التحميلات'),
        help_text=_('عدد مرات تحميل المستند')
    )
    
    class Meta:
        ordering = ['-issued_date']
        verbose_name = _('مستند الطالب')
        verbose_name_plural = _('مستندات الطلاب')
    
    def __str__(self):
        return f"{self.student.university_id} - {self.title}"
    
    def increment_download_count(self):
        self.download_count += 1
        self.save()


class SupportTicket(models.Model):
    """تذاكر الدعم الفني لاستفسارات الطلاب"""
    
    CATEGORY_CHOICES = (
        ('technical', _('الدعم الفني')),
        ('academic', _('الخدمات الأكاديمية')),
        ('financial', _('الخدمات المالية')),
        ('general', _('استفسار عام')),
    )
    
    PRIORITY_CHOICES = (
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('urgent', _('عاجل')),
    )
    
    STATUS_CHOICES = (
        ('open', _('مفتوح')),
        ('in_progress', _('قيد المعالجة')),
        ('resolved', _('تم الحل')),
        ('closed', _('مغلق')),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='support_tickets',
        verbose_name=_('الطالب'),
        help_text=_('الطالب الذي أنشأ التذكرة')
    )
    subject = models.CharField(
        max_length=200,
        verbose_name=_('الموضوع'),
        help_text=_('موضوع التذكرة')
    )
    description = models.TextField(
        verbose_name=_('الوصف'),
        help_text=_('وصف تفصيلي للمشكلة أو الاستفسار')
    )
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='general',
        verbose_name=_('الفئة'),
        help_text=_('فئة التذكرة')
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name=_('الأولوية'),
        help_text=_('أولوية التذكرة')
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='open',
        verbose_name=_('الحالة'),
        help_text=_('حالة التذكرة الحالية')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء التذكرة')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث'),
        help_text=_('تاريخ ووقت آخر تحديث')
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets',
        verbose_name=_('مُسند إلى'),
        help_text=_('الموظف المسؤول عن التذكرة')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('تذكرة دعم')
        verbose_name_plural = _('تذاكر الدعم')
    
    def __str__(self):
        return f"{self.student.university_id} - {self.subject}"


class TicketResponse(models.Model):
    """ردود على تذاكر الدعم"""
    
    ticket = models.ForeignKey(
        SupportTicket, 
        on_delete=models.CASCADE, 
        related_name='responses',
        verbose_name=_('التذكرة'),
        help_text=_('التذكرة المرتبطة بهذا الرد')
    )
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name=_('المجيب'),
        help_text=_('الشخص الذي كتب الرد')
    )
    message = models.TextField(
        verbose_name=_('الرسالة'),
        help_text=_('نص الرد')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت كتابة الرد')
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name=_('ملاحظة داخلية'),
        help_text=_('هل هذا الرد ملاحظة داخلية للموظفين فقط')
    )
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('رد التذكرة')
        verbose_name_plural = _('ردود التذاكر')
    
    def __str__(self):
        return f"رد على {self.ticket.subject} بواسطة {self.responder.get_full_name()}"
