from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class FeeType(models.Model):
    """Different types of fees that can be charged"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class StudentFee(models.Model):
    """Fees assigned to students"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('partial', 'Partially Paid'),
    )
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_fees')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.university_id} - {self.fee_type.name} - ${self.amount}"
    
    @property
    def amount_paid(self):
        """Calculate total amount paid for this fee"""
        return self.payments.filter(status='verified').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def remaining_balance(self):
        """Calculate remaining balance"""
        return self.amount - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if fee is overdue"""
        return self.due_date < timezone.now().date() and self.status != 'paid'
    
    def update_status(self):
        """Update fee status based on payments"""
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
    """Available payment providers"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    instructions = models.TextField(help_text="Payment instructions for students")
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='payment_providers/', null=True, blank=True)
    
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
