from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from address.models import AddressField
from django.conf import settings
from django.shortcuts import reverse


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

    def add_to_order(self):
        return reverse("buy", kwargs={
            'pk': self.pk
        })

    def remove_from_order(self):
        return reverse("remove", kwargs={
            'pk': self.pk
        })


class Comment(models.Model):
    handicraft = models.ForeignKey(Handicraft, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']


class OrderArt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    handicraft = models.ForeignKey(Handicraft, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def get_price(self):
        return self.handicraft.price

    def __str__(self):
        return f'{self.handicraft} {self.user}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    handicrafts = models.ManyToManyField(OrderArt)
    additional_info = models.CharField(max_length=1024, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    citi = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    house_number = models.SmallIntegerField(blank=True, null=True)
    flat_number = models.SmallIntegerField(null=True)

    def __str__(self):
        return f'{self.ordered}'

    def get_total_price(self):
        total = 0
        for order_handicraft in self.handicrafts.all():
            total += order_handicraft.get_price()
        return total
