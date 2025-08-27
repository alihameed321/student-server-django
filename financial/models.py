from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class FeeType(models.Model):
    """أنواع مختلفة من الرسوم التي يمكن فرضها"""
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name=_('الاسم'),
        help_text=_('اسم نوع الرسوم')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف نوع الرسوم')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل نوع الرسوم نشط')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء نوع الرسوم')
    )
    
    class Meta:
        verbose_name = _('نوع الرسوم')
        verbose_name_plural = _('أنواع الرسوم')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class StudentFee(models.Model):
    """الرسوم المخصصة للطلاب"""
    
    STATUS_CHOICES = (
        ('pending', _('في انتظار الدفع')),
        ('paid', _('مدفوع')),
        ('overdue', _('متأخر')),
        ('cancelled', _('ملغي')),
        ('partial', _('مدفوع جزئياً')),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='fees',
        verbose_name=_('الطالب'),
        help_text=_('الطالب المخصص له الرسوم')
    )
    fee_type = models.ForeignKey(
        FeeType, 
        on_delete=models.CASCADE,
        verbose_name=_('نوع الرسوم'),
        help_text=_('نوع الرسوم')
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('المبلغ'),
        help_text=_('مبلغ الرسوم')
    )
    due_date = models.DateField(
        verbose_name=_('تاريخ الاستحقاق'),
        help_text=_('تاريخ استحقاق الدفع')
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('الحالة'),
        help_text=_('حالة الرسوم')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف الرسوم')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء'),
        help_text=_('تاريخ ووقت إنشاء الرسوم')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_fees',
        verbose_name=_('أنشأ بواسطة'),
        help_text=_('الموظف الذي أنشأ الرسوم')
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('رسوم الطالب')
        verbose_name_plural = _('رسوم الطلاب')
    
    def __str__(self):
        return f"{self.student.university_id} - {self.fee_type.name} - ${self.amount}"
    
    @property
    def amount_paid(self):
        """حساب إجمالي المبلغ المدفوع لهذه الرسوم"""
        return self.payments.filter(status='verified').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def remaining_balance(self):
        """حساب الرصيد المتبقي"""
        return self.amount - self.amount_paid
    
    @property
    def is_overdue(self):
        """التحقق من تأخر الرسوم"""
        return self.due_date < timezone.now().date() and self.status != 'paid'
    
    def update_status(self):
        """تحديث حالة الرسوم بناءً على المدفوعات"""
        paid_amount = self.amount_paid
        if paid_amount >= self.amount:
            self.status = 'paid'
        elif paid_amount > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'pending'
        self.save()


class PaymentProvider(models.Model):
    """مقدمو خدمات الدفع المتاحة"""
    name = models.CharField(
        max_length=100,
        verbose_name=_('الاسم'),
        help_text=_('اسم مقدم خدمة الدفع')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('الوصف'),
        help_text=_('وصف مقدم خدمة الدفع')
    )
    instructions = models.TextField(
        verbose_name=_('التعليمات'),
        help_text=_('تعليمات الدفع للطلاب')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('نشط'),
        help_text=_('هل مقدم الخدمة نشط')
    )
    logo = models.ImageField(
        upload_to='payment_providers/', 
        null=True, 
        blank=True,
        verbose_name=_('الشعار'),
        help_text=_('شعار مقدم خدمة الدفع')
    )
    
    # معلومات حساب الجامعة
    university_account_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name=_('اسم حساب الجامعة'),
        help_text=_('اسم صاحب حساب الجامعة')
    )
    university_account_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name=_('رقم حساب الجامعة'),
        help_text=_('رقم حساب الجامعة')
    )
    university_phone = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_('هاتف الجامعة'),
        help_text=_('رقم هاتف الجامعة لهذا المقدم')
    )
    additional_info = models.TextField(
        blank=True,
        verbose_name=_('معلومات إضافية'),
        help_text=_('معلومات حساب إضافية (IBAN، رقم التوجيه، إلخ)')
    )
    
    class Meta:
        verbose_name = _('مقدم خدمة الدفع')
        verbose_name_plural = _('مقدمو خدمات الدفع')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Payment(models.Model):
    """Student payments"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    payment_provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=200)
    payment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Transfer details from student
    sender_name = models.CharField(max_length=200, blank=True, null=True, help_text="Name of person who sent the money")
    sender_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number of sender")
    transfer_notes = models.TextField(blank=True, help_text="Additional notes from student about the transfer")
    
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.university_id} - {self.transaction_reference} - ${self.amount}"
    
    def verify_payment(self, staff_member, notes=""):
        """Verify the payment"""
        self.status = 'verified'
        self.verified_by = staff_member
        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.save()
        
        # Update fee status
        self.fee.update_status()
    
    def reject_payment(self, staff_member, reason):
        """Reject the payment"""
        self.status = 'rejected'
        self.verified_by = staff_member
        self.verified_at = timezone.now()
        self.verification_notes = reason
        self.save()
        
        # Update fee status
        self.fee.update_status()


class PaymentReceipt(models.Model):
    """Official payment receipts"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_file = models.FileField(upload_to='receipts/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.payment.student.university_id}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate unique receipt number
            import uuid
            self.receipt_number = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class FinancialReport(models.Model):
    """Financial reports and summaries"""
    
    REPORT_TYPES = (
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('yearly', 'Yearly Report'),
    )
    
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    total_fees_issued = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_payments_received = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_pending_verification = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    report_data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.start_date} to {self.end_date}"
