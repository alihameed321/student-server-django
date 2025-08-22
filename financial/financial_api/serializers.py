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
            raise serializers.ValidationError("At least one fee must be selected.")
        
        for fee_data in value:
            if 'id' not in fee_data or 'amount' not in fee_data:
                raise serializers.ValidationError("Each fee must have 'id' and 'amount' fields.")
            
            try:
                Decimal(fee_data['amount'])
            except (ValueError, TypeError):
                raise serializers.ValidationError("Invalid amount format.")
        
        return value
    
    def validate_payment_provider_id(self, value):
        try:
            provider = PaymentProvider.objects.get(id=value, is_active=True)
        except PaymentProvider.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive payment provider.")
        return value
    
    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than zero.")
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