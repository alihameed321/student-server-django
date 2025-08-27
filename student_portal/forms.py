from django import forms
from django.core.exceptions import ValidationError
from .models import ServiceRequest, SupportTicket, TicketResponse


class ServiceRequestForm(forms.ModelForm):
    """Form for creating service requests"""
    
    # Remove supporting_documents field as students don't upload files when requesting documents
    # supporting_documents = forms.FileField(
    #     required=False,
    #     widget=forms.ClearableFileInput(attrs={
    #         'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
    #         'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
    #     }),
    #     help_text='Upload supporting documents (PDF, DOC, DOCX, JPG, PNG) - Max 10MB'
    # )
    
    class Meta:
        model = ServiceRequest
        fields = ['request_type', 'title', 'description', 'priority']
        widgets = {
            'request_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'أدخل عنوان الطلب'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'اوصف طلبك بالتفصيل',
                'rows': 5
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),

        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('يجب أن يكون العنوان 5 أحرف على الأقل.')
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise ValidationError('يجب أن يكون الوصف 20 حرفاً على الأقل.')
        return description
    
    def clean_supporting_documents(self):
        file = self.cleaned_data.get('supporting_documents')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('يجب أن يكون حجم الملف أقل من 10 ميجابايت.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('يُسمح فقط بملفات PDF و DOC و DOCX و JPG و PNG.')
        
        return file
    



class SupportTicketForm(forms.ModelForm):
    """Form for creating support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'description', 'priority']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'أدخل موضوع التذكرة'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'اوصف مشكلتك بالتفصيل',
                'rows': 6
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 5:
            raise ValidationError('يجب أن يكون الموضوع 5 أحرف على الأقل.')
        return subject
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise ValidationError('يجب أن يكون الوصف 20 حرفاً على الأقل.')
        return description
    



class TicketResponseForm(forms.ModelForm):
    """Form for responding to support tickets"""
    
    class Meta:
        model = TicketResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'أدخل ردك...'
            })
        }
    
    def clean_message(self):
        """Validate message length"""
        message = self.cleaned_data.get('message')
        
        if message and len(message.strip()) < 10:
            raise ValidationError('يجب أن يكون الرد 10 أحرف على الأقل.')
        
        return message