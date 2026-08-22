from django import forms
from .models import StudentProfile
from accounts.models import User
from school.models import Stream


class StudentCreationForm(forms.ModelForm):
    stream = forms.ModelChoiceField(
        queryset=Stream.objects.all(),
        required=True,
        label="Stream",
        help_text="Select the stream the student belongs to.",
    )

    class Meta:
        model = StudentProfile
        fields = ['user', 'student_id', 'stream']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["grade", "date_of_birth", "address"]  # example fields


class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['photo', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }