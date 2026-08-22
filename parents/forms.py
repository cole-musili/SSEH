from django import forms
from .models import ParentProfile

class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ["photo", "first_name", "last_name", "phone", "address", "occupation"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "w-full p-2 border border-gray-300 rounded-md"}),
            "last_name": forms.TextInput(attrs={"class": "w-full p-2 border border-gray-300 rounded-md"}),
            "phone": forms.TextInput(attrs={"class": "w-full p-2 border border-gray-300 rounded-md"}),
            "address": forms.TextInput(attrs={"class": "w-full p-2 border border-gray-300 rounded-md"}),
            "occupation": forms.TextInput(attrs={"class": "w-full p-2 border border-gray-300 rounded-md"}),
        }

