from django import forms
from .models import TeacherRecord, Timetable
from .models import AcademicYear, Term

class TeacherRecordForm(forms.ModelForm):
    class Meta:
        model = TeacherRecord
        fields = [
            'full_name', 'gender', 'phone', 'email', 'qualification',
            'specialization', 'assigned_streams', 'employment_date',
            'status', 'photo'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'assigned_streams': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'employment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = [
            'stream', 'day_of_week', 'start_time', 'end_time',
            'subject', 'teacher_record', 'teacher_name',
            'is_substitution', 'room'
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        tr = cleaned.get("teacher_record")
        tn = cleaned.get("teacher_name", "").strip()
        if not tr and not tn:
            self.add_error("teacher_name", "Provide a teacher (record) or a teacher name.")
        return cleaned
    
class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['year_start', 'year_end', 'is_active']
        widgets = {
            'year_start': forms.NumberInput(attrs={'class': 'form-control'}),
            'year_end': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['name', 'academic_year', 'start_date', 'end_date', 'is_current']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }    