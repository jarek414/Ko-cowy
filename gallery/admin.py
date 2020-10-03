from django.contrib import admin
from .models import Handicraft, Author, Comment

admin.site.register(Handicraft, admin.ModelAdmin)

# Register your models here.
