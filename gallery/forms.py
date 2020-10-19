from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

from .validator import EmailValidator, should_be_empty


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


class UserAddForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


# class UpdateUserForm(UserChangeForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=120, validators=[EmailValidator])
    message = forms.CharField(widget=forms.Textarea)
    protect = forms.CharField(required=False, widget=forms.HiddenInput, label='Leave empty',
                              validators=[should_be_empty])


class OrderConfirmationForm(forms.Form):
    additional_info = forms.CharField(max_length=1024, widget=forms.Textarea)
    country = forms.CharField(max_length=100)
    citi = forms.CharField(max_length=100)
    zip = forms.CharField(max_length=100)
    street_address = forms.CharField(max_length=100)
    house_number = forms.CharField(max_length=100)
    flat_number = forms.CharField(max_length=100)


