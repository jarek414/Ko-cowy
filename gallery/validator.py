from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django import forms


def should_be_empty(value):
    if value:
        raise forms.ValidationError('field is not empty')


def email_validation_function(value):
    validator = EmailValidator()
    validator(value)
    return value