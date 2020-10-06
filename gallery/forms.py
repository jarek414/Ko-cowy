from django import forms
from .validator import email_validation_function
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .validator import EmailValidator, should_be_empty


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=120, validators=[EmailValidator])
    message = forms.CharField(widget=forms.Textarea)
    protect = forms.CharField(required=False, widget=forms.HiddenInput, label='Leave empty',
                              validators=[should_be_empty])
