from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    first_name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    curriculum_vitae = models.TextField()

    class Meta:
        ordering = ['surname']

    def __str__(self):
        return f'{self.first_name} {self.surname}'


class Handicraft(models.Model):
    class Category(models.TextChoices):
        OBRAZ = 'OBRAZ', _('Obraz')
        ZDJĘCIE = 'ZDJĘCIE', _('Zdjęcie')
        WIERSZ = 'WIERSZ', _('Wiersz')

    image = models.ImageField()
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=Category.choices)
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    added_date = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.title


class Comment(models.Model):
    handicraft = models.ForeignKey(Handicraft, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']