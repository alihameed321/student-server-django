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
                'placeholder': 'Enter request title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Describe your request in detail',
                'rows': 5
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),

        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('Title must be at least 5 characters long.')
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise ValidationError('Description must be at least 20 characters long.')
        return description
    
    def clean_supporting_documents(self):
        file = self.cleaned_data.get('supporting_documents')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size must be less than 10MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Only PDF, DOC, DOCX, JPG, and PNG files are allowed.')
        
        return file
    



class SupportTicketForm(forms.ModelForm):
    """Form for creating support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'description', 'priority']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter ticket subject'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Describe your issue in detail',
                'rows': 6
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 5:
            raise ValidationError('Subject must be at least 5 characters long.')
        return subject
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise ValidationError('Description must be at least 20 characters long.')
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
                'placeholder': 'Enter your response...'
            })
        }
    
    def clean_message(self):
        """Validate message length"""
        message = self.cleaned_data.get('message')
        
        if message and len(message.strip()) < 10:
            raise ValidationError('Response must be at least 10 characters long.')
        
        return message