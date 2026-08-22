from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded p-2'}),
            'subject': forms.TextInput(attrs={'class': 'w-full border rounded p-2'}),
            'message': forms.Textarea(attrs={'class': 'w-full border rounded p-2 h-28'}),
        }
