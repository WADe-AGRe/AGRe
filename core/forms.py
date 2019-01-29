from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from core.models import Review


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Given name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Family name')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    BOOLEAN_CHOICES = ((True, 'Yes'), (False, 'No'))
    is_professor = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=True, label='Are you a professor?',
                                     widget=forms.RadioSelect())
    is_student = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=True, label='Are you a student?',
                                   widget=forms.RadioSelect())

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_professor', 'is_student',)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ('reviewer',)

