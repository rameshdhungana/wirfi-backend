from django.contrib import admin
from wirfi_app.models import User, Profile, Business, Billing, Device, Subscription, ServicePlan, AuthorizationToken

admin.site.register(User)
admin.site.register([Profile, Billing, Business, Device, Subscription, AuthorizationToken])
