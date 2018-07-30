from django.core.management.base import BaseCommand
import stripe
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates products and and plans is stripe through api call'
    stripe_api_key = settings.STRIPE_API_KEY
    LITE_ACCOUNT = 'Lite Account'
    PRO_ACCOUNT = 'Pro Account:vvv-Monitoring'

    def create_products(self):
        stripe.api_key = self.stripe_api_key
        product_type = [
            {
                "name": self.LITE_ACCOUNT,
                "type": "service"
            },
            {
                "name": self.PRO_ACCOUNT,
                "type": "service"
            },

        ]
        products_stripe = [stripe.Product.create(**p) for p in product_type]

        for product in products_stripe:
            plan = stripe.Plan.create(
                product=product.id,
                nickname="Lite Plan" if (product.name == self.LITE_ACCOUNT) else "Pro Plan",
                interval='month',
                currency='usd',
                ammount=10000,

            )

        def handle(self, *args, **options):
            self.create_products()
