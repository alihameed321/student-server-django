from django import forms
from django.core.exceptions import ValidationError
from .models import ServiceRequest, SupportTicket, TicketResponse


class ServiceRequestForm(forms.ModelForm):
    """Form for creating service requests"""
    
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
    



class SupportTicketForm(forms.ModelForm):
    """Form for creating support tickets"""
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'description', 'priority']
        widgets = {

            'subject': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter ticket subject'
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