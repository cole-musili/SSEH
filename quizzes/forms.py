from django import forms
from .models import Question, Quiz

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Quiz Title'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional description'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter the question'}),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A'}),
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D'}),
            'correct_answer': forms.Select(choices=[('A','A'),('B','B'),('C','C'),('D','D')]),
        }
