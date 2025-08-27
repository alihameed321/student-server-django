from rest_framework import serializers
from ..models import FeeType, StudentFee, PaymentProvider, Payment, PaymentReceipt, FinancialReport
from accounts.models import User
from decimal import Decimal
from django.utils import timezone


class FeeTypeSerializer(serializers.ModelSerializer):
    """Serializer for fee types"""
    class Meta:
        model = FeeType
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentFeeSerializer(serializers.ModelSerializer):
    """Serializer for student fees"""
    fee_type = FeeTypeSerializer(read_only=True)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.university_id', read_only=True)
    
    class Meta:
        model = StudentFee
        fields = [
            'id', 'student', 'student_name', 'student_id', 'fee_type', 'amount', 
            'due_date', 'status', 'description', 'created_at', 'amount_paid', 
            'remaining_balance', 'is_overdue'
        ]
        read_only_fields = ['id', 'student', 'created_at', 'amount_paid', 'remaining_balance', 'is_overdue']


class PaymentProviderSerializer(serializers.ModelSerializer):
    """Serializer for payment providers"""
    class Meta:
        model = PaymentProvider
        fields = [
            'id', 'name', 'description', 'instructions', 'is_active', 'logo',
            'university_account_name', 'university_account_number', 
            'university_phone', 'additional_info'
        ]
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    fee = StudentFeeSerializer(read_only=True)
    payment_provider = PaymentProviderSerializer(read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.university_id', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_view_receipt = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'student_name', 'student_id', 'fee', 'payment_provider',
            'amount', 'transaction_reference', 'payment_date', 'status', 'status_display',
            'sender_name', 'sender_phone', 'transfer_notes', 'verification_notes',
            'verified_by', 'verified_by_name', 'verified_at', 'created_at', 'can_view_receipt'
        ]
        read_only_fields = [
            'id', 'student', 'status', 'verification_notes', 'verified_by', 
            'verified_at', 'created_at', 'can_view_receipt'
        ]
    
    def get_can_view_receipt(self, obj):
        return obj.status == 'verified'


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payments"""
    fees = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        help_text="List of fee objects with id and amount to pay"
    )
    payment_provider_id = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = serializers.CharField(max_length=200)
    sender_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    sender_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    transfer_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_fees(self, value):
        if not value:
            raise serializers.ValidationError("يجب اختيار رسم واحد على الأقل.")
        
        for fee_data in value:
            if 'id' not in fee_data or 'amount' not in fee_data:
                raise serializers.ValidationError("يجب أن يحتوي كل رسم على حقلي 'id' و 'amount'.")
            
            try:
                Decimal(fee_data['amount'])
            except (ValueError, TypeError):
                raise serializers.ValidationError("تنسيق المبلغ غير صحيح.")
        
        return value
    
    def validate_payment_provider_id(self, value):
        try:
            provider = PaymentProvider.objects.get(id=value, is_active=True)
        except PaymentProvider.DoesNotExist:
            raise serializers.ValidationError("مقدم الدفع غير صحيح أو غير نشط.")
        return value
    
    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("يجب أن يكون مبلغ الدفع أكبر من الصفر.")
        return value


class PaymentReceiptSerializer(serializers.ModelSerializer):
    """Serializer for payment receipts"""
    payment = PaymentSerializer(read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = PaymentReceipt
        fields = [
            'id', 'payment', 'receipt_number', 'receipt_file', 
            'generated_at', 'generated_by', 'generated_by_name'
        ]
        read_only_fields = ['id', 'receipt_number', 'generated_at', 'generated_by']


class FinancialSummarySerializer(serializers.Serializer):
    """Serializer for financial summary data"""
    total_fees = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
    paid_this_semester = serializers.DecimalField(max_digits=15, decimal_places=2)
    overdue_count = serializers.IntegerField()
    recent_transactions = PaymentSerializer(many=True)
    fee_breakdown = StudentFeeSerializer(many=True)
    
    class Meta:
        fields = [
            'total_fees', 'pending_payments', 'paid_this_semester', 
            'overdue_count', 'recent_transactions', 'fee_breakdown'
        ]


class EnhancedStudentFeeSerializer(StudentFeeSerializer):
    """Enhanced serializer for student fees with additional mobile-friendly fields"""
    days_until_due = serializers.SerializerMethodField()
    payment_urgency = serializers.SerializerMethodField()
    fee_category = serializers.CharField(source='fee_type.name', read_only=True)
    
    class Meta(StudentFeeSerializer.Meta):
        fields = StudentFeeSerializer.Meta.fields + [
            'days_until_due', 'payment_urgency', 'fee_category'
        ]
    
    def get_days_until_due(self, obj):
        """Calculate days until due date"""
        if not obj.due_date:
            return None
        today = timezone.now().date()
        delta = obj.due_date - today
        return delta.days
    
    def get_payment_urgency(self, obj):
        """Determine payment urgency level"""
        if not obj.due_date:
            return 'normal'
        
        days_until_due = self.get_days_until_due(obj)
        if days_until_due is None:
            return 'normal'
        
        if days_until_due < 0:
            return 'overdue'
        elif days_until_due <= 7:
            return 'urgent'
        elif days_until_due <= 30:
            return 'moderate'
        else:
            return 'normal'


class MobilePaymentSerializer(PaymentSerializer):
    """Mobile-optimized payment serializer with simplified fields"""
    fee_name = serializers.CharField(source='fee.fee_type.name', read_only=True)
    payment_provider_name = serializers.CharField(source='payment_provider.name', read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    payment_status_color = serializers.SerializerMethodField()
    
    class Meta(PaymentSerializer.Meta):
        fields = [
            'id', 'fee_name', 'payment_provider_name', 'amount', 'formatted_amount',
            'transaction_reference', 'payment_date', 'status', 'status_display',
            'payment_status_color', 'verified_at', 'can_view_receipt'
        ]
    
    def get_formatted_amount(self, obj):
        """Format amount for mobile display"""
        return f"${obj.amount:,.2f}"
    
    def get_payment_status_color(self, obj):
        """Get color code for payment status"""
        status_colors = {
            'pending': '#FFA500',  # Orange
            'verified': '#28A745',  # Green
            'rejected': '#DC3545',  # Red
            'cancelled': '#6C757D'  # Gray
        }
        return status_colors.get(obj.status, '#6C757D')


class PaymentStatisticsSerializer(serializers.Serializer):
    """Serializer for payment statistics data"""
    success = serializers.BooleanField(default=True)
    summary = serializers.DictField()
    payment_counts = serializers.DictField()
    payment_amounts = serializers.DictField()
    current_year = serializers.DictField()
    monthly_summary = serializers.ListField()
    provider_usage = serializers.ListField()
    
    class Meta:
        fields = [
            'success', 'summary', 'payment_counts', 'payment_amounts',
            'current_year', 'monthly_summary', 'provider_usage'
        ]


class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for financial reports"""
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'report_type', 'report_type_display', 'start_date', 'end_date',
            'total_fees_issued', 'total_payments_received', 'total_pending_verification',
            'report_data', 'generated_at', 'generated_by', 'generated_by_name'
        ]
        read_only_fields = ['id', 'generated_at', 'generated_by']