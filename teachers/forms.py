from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500',
                'placeholder': 'Email Address'
            }),
        }
