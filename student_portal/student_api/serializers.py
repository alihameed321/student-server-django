from rest_framework import serializers
from ..models import ServiceRequest, StudentDocument, SupportTicket, TicketResponse, RequestDocument
from accounts.models import User
from django.utils import timezone


class StudentBasicSerializer(serializers.ModelSerializer):
    """Basic student information for mobile app"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'university_id', 'full_name', 'email']


class RequestDocumentSerializer(serializers.ModelSerializer):
    """Serializer for request supporting documents"""
    file_size = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RequestDocument
        fields = ['id', 'document_name', 'uploaded_at', 'file_size', 'file_url']
    
    def get_file_size(self, obj):
        try:
            return obj.document.size
        except:
            return 0
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.document and request:
            return request.build_absolute_uri(obj.document.url)
        return None


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for service request list view"""
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_icon = serializers.CharField(read_only=True)
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'request_type', 'request_type_display', 'title', 'description',
            'status', 'status_display', 'status_icon', 'priority',
            'created_at', 'updated_at', 'days_since_created'
        ]
    
    def get_days_since_created(self, obj):
        return (timezone.now() - obj.created_at).days


class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for service request detail view"""
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_icon = serializers.CharField(read_only=True)
    student = serializers.CharField(source='student.university_id', read_only=True)
    processed_by = StudentBasicSerializer(read_only=True)
    documents = RequestDocumentSerializer(many=True, read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'student', 'request_type', 'request_type_display', 'title', 'description',
            'status', 'status_display', 'status_icon', 'priority', 'priority_display',
            'created_at', 'updated_at', 'processed_by', 'rejection_reason',
            'additional_info_request', 'documents', 'can_cancel'
        ]
    
    def get_can_cancel(self, obj):
        return obj.status in ['pending', 'in_review']


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating service requests"""
    
    class Meta:
        model = ServiceRequest
        fields = ['request_type', 'title', 'description', 'priority']
    
    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("يجب أن يكون العنوان مكوناً من 5 أحرف على الأقل.")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("يجب أن يكون الوصف مكوناً من 20 حرفاً على الأقل.")
        return value.strip()
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class StudentDocumentSerializer(serializers.ModelSerializer):
    """Enhanced serializer for student documents with mobile app optimizations"""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    file_size = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    issued_by_name = serializers.CharField(source='issued_by.get_full_name', read_only=True)
    issued_date_formatted = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    is_downloadable = serializers.SerializerMethodField()
    status_badge = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'title',
            'issued_date', 'issued_date_formatted', 'issued_by_name', 'is_official', 
            'download_count', 'file_size', 'file_size_formatted', 'download_url', 
            'preview_url', 'file_extension', 'is_downloadable', 'status_badge'
        ]
    
    def get_file_size(self, obj):
        try:
            return obj.document_file.size if obj.document_file else 0
        except:
            return 0
    
    def get_file_size_formatted(self, obj):
        try:
            if not obj.document_file:
                return "N/A"
            size = obj.document_file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "N/A"
    
    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse('student_api:document_download', kwargs={'document_id': obj.id})
            )
        return None
    
    def get_preview_url(self, obj):
        request = self.context.get('request')
        if request:
            from django.urls import reverse
            return request.build_absolute_uri(
                reverse('student_api:document_detail', kwargs={'document_id': obj.id})
            )
        return None
    
    def get_issued_date_formatted(self, obj):
        if obj.issued_date:
            return obj.issued_date.strftime('%B %d, %Y')
        return None
    
    def get_file_extension(self, obj):
        try:
            if obj.document_file and obj.document_file.name:
                import os
                return os.path.splitext(obj.document_file.name)[1].lower()
        except:
            pass
        return None
    
    def get_is_downloadable(self, obj):
        return bool(obj.document_file)
    
    def get_status_badge(self, obj):
        if obj.is_official:
            return {
                'text': 'رسمي',
                'color': '#28a745',
                'background': '#d4edda'
            }
        else:
            return {
                'text': 'غير رسمي',
                'color': '#6c757d',
                'background': '#e2e3e5'
            }


class TicketResponseSerializer(serializers.ModelSerializer):
    """Serializer for ticket responses"""
    responder_name = serializers.CharField(source='responder.get_full_name', read_only=True)
    responder_type = serializers.SerializerMethodField()
    
    class Meta:
        model = TicketResponse
        fields = [
            'id', 'message', 'created_at', 'responder_name', 
            'responder_type', 'is_internal'
        ]
    
    def get_responder_type(self, obj):
        if obj.responder.is_staff:
            return 'staff'
        return 'student'


class SupportTicketListSerializer(serializers.ModelSerializer):
    """Simplified serializer for support ticket list view"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    response_count = serializers.SerializerMethodField()
    last_response_date = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'subject', 'category', 'category_display', 'priority', 'priority_display',
            'status', 'status_display', 'created_at', 'updated_at',
            'response_count', 'last_response_date'
        ]
    
    def get_response_count(self, obj):
        return obj.responses.filter(is_internal=False).count()
    
    def get_last_response_date(self, obj):
        last_response = obj.responses.filter(is_internal=False).last()
        return last_response.created_at if last_response else obj.created_at


class SupportTicketDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for support ticket detail view"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    responses = TicketResponseSerializer(many=True, read_only=True)
    can_respond = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'subject', 'description', 'category', 'category_display',
            'priority', 'priority_display', 'status', 'status_display',
            'created_at', 'updated_at', 'assigned_to_name', 'responses', 'can_respond'
        ]
    
    def get_can_respond(self, obj):
        return obj.status in ['open', 'in_progress']


class SupportTicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'description', 'category', 'priority']
    
    def validate_subject(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("يجب أن يكون الموضوع مكوناً من 5 أحرف على الأقل.")
        return value.strip()
    
    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("يجب أن يكون الوصف مكوناً من 10 أحرف على الأقل.")
        return value.strip()
    
    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)


class TicketResponseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ticket responses"""
    
    class Meta:
        model = TicketResponse
        fields = ['message']
    
    def validate_message(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("يجب أن تكون الرسالة مكونة من 5 أحرف على الأقل.")
        return value.strip()
    
    def create(self, validated_data):
        validated_data['responder'] = self.context['request'].user
        validated_data['ticket'] = self.context['ticket']
        return super().create(validated_data)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    pending_requests = serializers.IntegerField()
    new_documents = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    recent_requests = ServiceRequestListSerializer(many=True)
    recent_documents = StudentDocumentSerializer(many=True)
    recent_tickets = SupportTicketListSerializer(many=True)