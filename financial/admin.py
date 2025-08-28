from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from decimal import Decimal
from .models import FeeType, StudentFee, PaymentProvider, Payment, PaymentReceipt, FinancialReport


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    """Admin for Fee Types with university branding"""
    
    list_display = ('name', 'get_active_badge', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('معلومات نوع الرسوم', {
            'fields': ('name', 'description', 'is_active'),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">ACTIVE</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">INACTIVE</span>'
        )
    get_active_badge.short_description = 'الحالة'
    get_active_badge.admin_order_field = 'is_active'


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    """Admin for Student Fees"""
    
    list_display = ('get_student_id', 'get_student_name', 'fee_type', 'get_amount_display', 'get_status_badge', 'due_date')
    list_filter = ('status', 'fee_type', 'due_date', 'created_at')
    search_fields = ('student__university_id', 'student__first_name', 'student__last_name', 'fee_type__name')
    ordering = ('-created_at',)
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('معلومات الرسوم', {
            'fields': ('student', 'fee_type', 'amount', 'due_date', 'description'),
            'classes': ('wide',)
        }),
        ('الحالة والمعالجة', {
            'fields': ('status', 'created_by'),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_student_id(self, obj):
        return obj.student.university_id
    get_student_id.short_description = 'رقم الطالب'
    get_student_id.admin_order_field = 'student__university_id'
    
    def get_student_name(self, obj):
        return obj.student.get_full_name()
    get_student_name.short_description = 'اسم الطالب'
    get_student_name.admin_order_field = 'student__first_name'
    
    def get_amount_display(self, obj):
        return f"${obj.amount:,.2f}"
    get_amount_display.short_description = 'المبلغ'
    get_amount_display.admin_order_field = 'amount'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#F5C400',
            'paid': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d',
            'partial': '#102A71'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'الحالة'
    get_status_badge.admin_order_field = 'status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for Payments"""
    
    list_display = ('get_student_info', 'get_fee_info', 'get_amount', 'get_status_badge', 'payment_date')
    list_filter = ('status', 'payment_date', 'payment_provider')
    search_fields = ('student__university_id', 'student__first_name', 'student__last_name', 'transaction_reference')
    ordering = ('-payment_date',)
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('معلومات الدفع', {
            'fields': ('student', 'fee', 'amount', 'payment_provider'),
            'classes': ('wide',)
        }),
        ('تفاصيل المعاملة', {
            'fields': ('transaction_reference', 'payment_date'),
            'classes': ('wide',)
        }),
        ('الحالة والتحقق', {
            'fields': ('status', 'verification_notes', 'verified_by', 'verified_at'),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'verified_at')
    actions = ['verify_payments', 'reject_payments']
    
    def get_student_info(self, obj):
        return f"{obj.student.university_id} - {obj.student.get_full_name()}"
    get_student_info.short_description = 'الطالب'
    get_student_info.admin_order_field = 'student__university_id'
    
    def get_fee_info(self, obj):
        return f"{obj.fee.fee_type.name} - ${obj.fee.amount}"
    get_fee_info.short_description = 'الرسوم'
    get_fee_info.admin_order_field = 'fee__fee_type__name'
    
    def get_amount(self, obj):
        return f"${obj.amount:,.2f}"
    get_amount.short_description = 'المبلغ'
    get_amount.admin_order_field = 'amount'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#F5C400',
            'verified': '#28a745',
            'rejected': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'الحالة'
    get_status_badge.admin_order_field = 'status'
    
    def verify_payments(self, request, queryset):
        """Bulk verify payments"""
        updated = 0
        for payment in queryset.filter(status='pending'):
            payment.verify_payment(request.user)
            updated += 1
        self.message_user(request, f'تم التحقق من {updated} دفعة بنجاح.')
    verify_payments.short_description = "التحقق من المدفوعات المحددة"
    
    def reject_payments(self, request, queryset):
        """Bulk reject payments"""
        updated = 0
        for payment in queryset.filter(status='pending'):
            payment.reject_payment(request.user, "Bulk rejection")
            updated += 1
        self.message_user(request, f'تم رفض {updated} دفعة.')
    reject_payments.short_description = "رفض المدفوعات المحددة"


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    """Admin for Payment Providers"""
    
    list_display = ('name', 'get_status_badge', 'get_payments_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('معلومات مقدم الخدمة', {
            'fields': ('name', 'description', 'instructions'),
            'classes': ('wide',)
        }),
        ('العرض والحالة', {
            'fields': ('logo', 'is_active'),
            'classes': ('wide',)
        }),
    )
    
    def get_status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">Inactive</span>'
            )
    get_status_badge.short_description = 'الحالة'
    get_status_badge.admin_order_field = 'is_active'
    
    def get_payments_count(self, obj):
        return obj.payments.count()
    get_payments_count.short_description = 'إجمالي المدفوعات'


@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    """Admin for Payment Receipts"""
    
    list_display = ('receipt_number', 'get_student_info', 'get_payment_amount', 'generated_at', 'generated_by')
    list_filter = ('generated_at', 'generated_by')
    search_fields = ('receipt_number', 'payment__student__university_id', 'payment__student__first_name', 'payment__student__last_name')
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('معلومات الإيصال', {
            'fields': ('receipt_number', 'payment'),
            'classes': ('wide',)
        }),
        ('الملف والإنشاء', {
            'fields': ('receipt_file', 'generated_by', 'generated_at'),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ('generated_at',)
    
    def get_student_info(self, obj):
        return f"{obj.payment.student.university_id} - {obj.payment.student.get_full_name()}"
    get_student_info.short_description = 'الطالب'
    get_student_info.admin_order_field = 'payment__student__university_id'
    
    def get_payment_amount(self, obj):
        return f"${obj.payment.amount:,.2f}"
    get_payment_amount.short_description = 'المبلغ'
    get_payment_amount.admin_order_field = 'payment__amount'


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    """Admin for Financial Reports"""
    
    list_display = ('report_type', 'get_period_display', 'get_total_amount_display', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'start_date', 'end_date', 'generated_at')
    search_fields = ('report_type', 'generated_by__username')
    ordering = ('-generated_at',)
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('معلومات التقرير', {
            'fields': ('report_type', 'start_date', 'end_date', 'generated_by'),
            'classes': ('wide',)
        }),
        ('بيانات التقرير', {
            'fields': ('report_data', 'total_payments_received'),
            'classes': ('wide',)
        }),
        ('البيانات الوصفية', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('generated_at',)
    
    def get_period_display(self, obj):
        return f"{obj.start_date} to {obj.end_date}"
    get_period_display.short_description = 'الفترة'
    
    def get_total_amount_display(self, obj):
        return f"${obj.total_payments_received:,.2f}" if obj.total_payments_received else '-'
    get_total_amount_display.short_description = 'إجمالي المبلغ'
    get_total_amount_display.admin_order_field = 'total_payments_received'
