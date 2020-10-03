from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


def email_validation_function(value):
    validator = EmailValidator()
    validator(value)
    return value