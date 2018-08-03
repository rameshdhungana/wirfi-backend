import stripe
from django.core.management import BaseCommand
from django.conf import settings
from wirfi_app.models import Subscription


class Command(BaseCommand):
    help = "Creates subscription for the Customers"
    stripe_api_key = settings.STRIPE_API_KEY

    def handle(self, *args, **options):
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'plan': plan_id}],
        )
