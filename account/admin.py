from django.contrib import admin
from .models import *
# Register your models here.

class userAdmin(admin.ModelAdmin):
    readonly_fields = ("created_date",)

admin.site.register(user)