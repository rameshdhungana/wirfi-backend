from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Business, Billing, Device

admin.site.register(User, UserAdmin)
admin.site.register([Profile, Billing, Business, Device])
