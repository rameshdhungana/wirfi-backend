from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

PLAN_INTERVAL = 'month'
PLAN_CURRENCY = 'usd'


class DateTimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ServicePlan(DateTimeModel):
    stripe_id = models.CharField(max_length=255)
    name = models.CharField(max_length=128)
    interval = models.CharField(max_length=128, default=PLAN_INTERVAL)
    currency = models.CharField(max_length=128, default=PLAN_CURRENCY)
    amount = models.FloatField(null=True, blank=True)


class Subscription(DateTimeModel):
    customer_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    service_plan = models.ForeignKey(ServicePlan, on_delete=models.CASCADE)
