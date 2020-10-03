from django import forms
from .validator import email_validation_function
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
