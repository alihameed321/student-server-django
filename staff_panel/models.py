from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Sum
from django.utils.translation import gettext_lazy as _


class DashboardStats(models.Model):
    """إحصائيات لوحة التحكم لموظفي الجامعة"""
    
    date = models.DateField(
        unique=True,
        verbose_name=_('التاريخ'),
        help_text=_('تاريخ الإحصائيات')
    )
    
    # إحصائيات الطلاب
    total_students = models.IntegerField(
        default=0,
        verbose_name=_('إجمالي الطلاب'),
        help_text=_('العدد الإجمالي للطلاب المسجلين')
    )
    new_students_today = models.IntegerField(
        default=0,
        verbose_name=_('الطلاب الجدد اليوم'),
        help_text=_('عدد الطلاب الذين سجلوا اليوم')
    )
    active_students = models.IntegerField(
        default=0,
        verbose_name=_('الطلاب النشطون'),
        help_text=_('عدد الطلاب الذين دخلوا النظام اليوم')
    )
    
    # إحصائيات الطلبات
    total_requests = models.IntegerField(
        default=0,
        verbose_name=_('إجمالي الطلبات'),
        help_text=_('العدد الإجمالي لطلبات الخدمات')
    )
    pending_requests = models.IntegerField(
        default=0,
        verbose_name=_('الطلبات المعلقة'),
        help_text=_('عدد الطلبات في انتظار المراجعة')
    )
    approved_requests_today = models.IntegerField(
        default=0,
        verbose_name=_('الطلبات المعتمدة اليوم'),
        help_text=_('عدد الطلبات التي تم اعتمادها اليوم')
    )
    rejected_requests_today = models.IntegerField(
        default=0,
        verbose_name=_('الطلبات المرفوضة اليوم'),
        help_text=_('عدد الطلبات التي تم رفضها اليوم')
    )
    
    # الإحصائيات المالية
    total_fees_collected_today = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name=_('إجمالي الرسوم المحصلة اليوم'),
        help_text=_('المبلغ الإجمالي للرسوم المحصلة اليوم')
    )
    pending_payments = models.IntegerField(
        default=0,
        verbose_name=_('المدفوعات المعلقة'),
        help_text=_('عدد المدفوعات في انتظار التحقق')
    )
    verified_payments_today = models.IntegerField(
        default=0,
        verbose_name=_('المدفوعات المتحققة اليوم'),
        help_text=_('عدد المدفوعات التي تم التحقق منها اليوم')
    )
    
    # إحصائيات الدعم الفني
    open_support_tickets = models.IntegerField(
        default=0,
        verbose_name=_('تذاكر الدعم المفتوحة'),
        help_text=_('عدد تذاكر الدعم المفتوحة')
    )
    resolved_tickets_today = models.IntegerField(
        default=0,
        verbose_name=_('التذاكر المحلولة اليوم'),
        help_text=_('عدد تذاكر الدعم التي تم حلها اليوم')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء السجل')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث'),
        help_text=_('تاريخ ووقت آخر تحديث')
    )
    
    class Meta:
        ordering = ['-date']
        verbose_name = _('إحصائيات لوحة التحكم')
        verbose_name_plural = _('إحصائيات لوحة التحكم')
    
    def __str__(self):
        return f"إحصائيات لوحة التحكم - {self.date}"
    
    @classmethod
    def get_or_create_today(cls):
        """Get or create today's dashboard stats"""
        today = timezone.now().date()
        stats, created = cls.objects.get_or_create(date=today)
        if created:
            stats.calculate_stats()
        return stats
    
    def calculate_stats(self):
        """Calculate and update all statistics"""
        from accounts.models import User
        from student_portal.models import ServiceRequest, SupportTicket
        from financial.models import Payment, StudentFee
        
        # Student statistics
        self.total_students = User.objects.filter(user_type='student').count()
        self.new_students_today = User.objects.filter(
            user_type='student',
            date_joined__date=self.date
        ).count()
        self.active_students = User.objects.filter(
            user_type='student',
            last_login__date=self.date
        ).count()
        
        # Request statistics
        self.total_requests = ServiceRequest.objects.count()
        self.pending_requests = ServiceRequest.objects.filter(
            status__in=['pending', 'in_review']
        ).count()
        self.approved_requests_today = ServiceRequest.objects.filter(
            status='approved',
            updated_at__date=self.date
        ).count()
        self.rejected_requests_today = ServiceRequest.objects.filter(
            status='rejected',
            updated_at__date=self.date
        ).count()
        
        # Financial statistics
        verified_payments_today = Payment.objects.filter(
            status='verified',
            verified_at__date=self.date
        )
        self.total_fees_collected_today = verified_payments_today.aggregate(
            total=Sum('amount')
        )['total'] or 0
        self.pending_payments = Payment.objects.filter(status='pending').count()
        self.verified_payments_today = verified_payments_today.count()
        
        # Support statistics
        self.open_support_tickets = SupportTicket.objects.filter(
            status__in=['open', 'in_progress']
        ).count()
        self.resolved_tickets_today = SupportTicket.objects.filter(
            status='resolved',
            updated_at__date=self.date
        ).count()
        
        self.save()


class StaffActivity(models.Model):
    """تتبع أنشطة الموظفين لأغراض المراجعة"""
    
    ACTIVITY_TYPES = (
        ('login', _('تسجيل دخول المستخدم')),
        ('logout', _('تسجيل خروج المستخدم')),
        ('request_approved', _('اعتماد طلب')),
        ('request_rejected', _('رفض طلب')),
        ('payment_verified', _('التحقق من دفعة')),
        ('payment_rejected', _('رفض دفعة')),
        ('document_uploaded', _('رفع مستند')),
        ('announcement_created', _('إنشاء إعلان')),
        ('notification_created', _('إنشاء إشعار')),
        ('report_generated', _('إنشاء تقرير')),
        ('fee_created', _('إنشاء رسوم')),
        ('user_created', _('إنشاء مستخدم')),
        ('user_modified', _('تعديل مستخدم')),
        ('other', _('نشاط آخر')),
    )
    
    staff_member = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='activities',
        verbose_name=_('عضو الطاقم'),
        help_text=_('الموظف الذي قام بالنشاط')
    )
    activity_type = models.CharField(
        max_length=20, 
        choices=ACTIVITY_TYPES,
        verbose_name=_('نوع النشاط'),
        help_text=_('نوع النشاط المنجز')
    )
    description = models.TextField(
        verbose_name=_('الوصف'),
        help_text=_('وصف تفصيلي للنشاط')
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='targeted_activities',
        verbose_name=_('المستخدم المستهدف'),
        help_text=_('المستخدم الذي تأثر بالنشاط')
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name=_('عنوان IP'),
        help_text=_('عنوان IP للمستخدم')
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('وكيل المستخدم'),
        help_text=_('معلومات المتصفح')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('الطابع الزمني'),
        help_text=_('تاريخ ووقت النشاط')
    )
    
    # بيانات السياق الإضافية
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name=_('البيانات الوصفية'),
        help_text=_('بيانات إضافية حول النشاط')
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('نشاط الموظف')
        verbose_name_plural = _('أنشطة الموظفين')
    
    def __str__(self):
        return f"{self.staff_member.get_full_name()} - {self.get_activity_type_display()}"


class WorkflowTemplate(models.Model):
    """قوالب سير العمل الشائعة للموظفين"""
    
    WORKFLOW_TYPES = (
        ('request_processing', _('معالجة الطلبات')),
        ('payment_verification', _('التحقق من المدفوعات')),
        ('document_generation', _('إنشاء المستندات')),
        ('student_onboarding', _('تسجيل الطلاب الجدد')),
        ('fee_management', _('إدارة الرسوم')),
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('الاسم'),
        help_text=_('اسم قالب سير العمل')
    )
    workflow_type = models.CharField(
        max_length=25, 
        choices=WORKFLOW_TYPES,
        verbose_name=_('نوع سير العمل'),
        help_text=_('نوع سير العمل')
    )
    description = models.TextField(
        verbose_name=_('الوصف'),
        help_text=_('وصف سير العمل')
    )
    steps = models.JSONField(
        default=list,
        verbose_name=_('الخطوات'),
        help_text=_('قائمة خطوات سير العمل')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل القالب نشط')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name=_('أنشأ بواسطة'),
        help_text=_('الموظف الذي أنشأ القالب')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء القالب')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث'),
        help_text=_('تاريخ ووقت آخر تحديث')
    )
    
    class Meta:
        verbose_name = _('قالب سير العمل')
        verbose_name_plural = _('قوالب سير العمل')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_workflow_type_display()})"


class QuickAction(models.Model):
    """الإجراءات السريعة للوحة تحكم الموظفين"""
    
    ACTION_TYPES = (
        ('create_announcement', _('إنشاء إعلان')),
        ('verify_payments', _('التحقق من المدفوعات')),
        ('review_requests', _('مراجعة الطلبات')),
        ('generate_report', _('إنشاء تقرير')),
        ('manage_fees', _('إدارة الرسوم')),
        ('student_lookup', _('البحث عن طالب')),
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name=_('الاسم'),
        help_text=_('اسم الإجراء السريع')
    )
    action_type = models.CharField(
        max_length=25, 
        choices=ACTION_TYPES,
        verbose_name=_('نوع الإجراء'),
        help_text=_('نوع الإجراء السريع')
    )
    description = models.CharField(
        max_length=200,
        verbose_name=_('الوصف'),
        help_text=_('وصف الإجراء السريع')
    )
    url_pattern = models.CharField(
        max_length=200,
        verbose_name=_('نمط الرابط'),
        help_text=_('نمط الرابط للإجراء')
    )
    icon_class = models.CharField(
        max_length=50, 
        default='fas fa-cog',
        verbose_name=_('فئة الأيقونة'),
        help_text=_('فئة CSS للأيقونة')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل الإجراء نشط')
    )
    required_permissions = models.JSONField(
        default=list,
        verbose_name=_('الصلاحيات المطلوبة'),
        help_text=_('قائمة الصلاحيات المطلوبة')
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_('الترتيب'),
        help_text=_('ترتيب عرض الإجراء')
    )
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('إجراء سريع')
        verbose_name_plural = _('إجراءات سريعة')
    
    def __str__(self):
        return self.name
    
    def is_accessible_by(self, user):
        """Check if user has required permissions for this action"""
        if not self.required_permissions:
            return True
        
        # Check if user has any of the required permissions
        for permission in self.required_permissions:
            if user.has_perm(permission):
                return True
        return False


class SystemConfiguration(models.Model):
    """إعدادات التكوين على مستوى النظام"""
    
    CONFIG_TYPES = (
        ('general', _('الإعدادات العامة')),
        ('academic', _('الإعدادات الأكاديمية')),
        ('financial', _('الإعدادات المالية')),
        ('notification', _('إعدادات الإشعارات')),
        ('security', _('إعدادات الأمان')),
    )
    
    category = models.CharField(
        max_length=15, 
        choices=CONFIG_TYPES,
        verbose_name=_('الفئة'),
        help_text=_('فئة الإعداد')
    )
    key = models.CharField(
        max_length=100,
        verbose_name=_('المفتاح'),
        help_text=_('مفتاح الإعداد')
    )
    value = models.TextField(
        verbose_name=_('القيمة'),
        help_text=_('قيمة الإعداد')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف الإعداد')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل الإعداد نشط')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء الإعداد')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث'),
        help_text=_('تاريخ ووقت آخر تحديث')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_('حُدث بواسطة'),
        help_text=_('الموظف الذي قام بآخر تحديث')
    )
    
    class Meta:
        unique_together = ['category', 'key']
        ordering = ['category', 'key']
        verbose_name = _('إعداد النظام')
        verbose_name_plural = _('إعدادات النظام')
    
    def __str__(self):
        return f"{self.category}.{self.key}"
    
    @classmethod
    def get_value(cls, category, key, default=None):
        """الحصول على قيمة الإعداد"""
        try:
            config = cls.objects.get(category=category, key=key, is_active=True)
            return config.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, category, key, value, user=None, description=""):
        """تعيين قيمة الإعداد"""
        config, created = cls.objects.get_or_create(
            category=category,
            key=key,
            defaults={
                'value': value,
                'description': description,
                'updated_by': user
            }
        )
        if not created:
            config.value = value
            config.updated_by = user
            if description:
                config.description = description
            config.save()
        return config
