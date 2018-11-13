import stripe
from django.conf import settings

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Billing
from wirfi_app.serializers import BillingSerializer
from wirfi_app.views.login_logout import get_token_obj


class BillingView(generics.ListCreateAPIView):
    serializer_class = BillingSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Billing.objects.filter(user=token.user)

    def retrieve_stripe_customer_info(self):
        stripe.api_key = settings.STRIPE_API_KEY
        token = get_token_obj(self.request.auth)
        billing = Billing.objects.filter(user=token.user).first()
        if billing:
            return stripe.Customer.retrieve(billing.customer_id)
        else:
            return None

    def list(self, request, *args, **kwargs):
        stripe_customer_info = self.retrieve_stripe_customer_info()

        if stripe_customer_info:
            data = {
                'code': getattr(settings, 'SUCCESS_CODE', 1),
                'message': "Details successfully fetched",
                'data': {
                    'billing_info': stripe_customer_info,
                    'email': request.user.email,
                },
            }
        else:
            data = {
                'code': 2,
                'message': "No any billing data"
            }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        stripe.api_key = settings.STRIPE_API_KEY
        stripe_token = data['id'].strip()

        email = data['email']

        token = get_token_obj(request.auth)
        billing_obj = Billing.objects.filter(user=token.user)
        serializer = BillingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if billing_obj:
            stripe.Customer.retrieve(billing_obj.first().customer_id).sources.create(source=stripe_token)
            customer = stripe.Customer.retrieve(billing_obj.first().customer_id)

        else:
            try:
                customer = stripe.Customer.create(
                    source=stripe_token,
                    email=email
                )
                serializer.save(user=token.user, customer_id=customer.id)

            except:
                return Response({
                    'code': getattr(settings, 'ERROR_CODE', 0),
                    'message': "Stripe Token has already been used. Please try again with new token."
                }, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Billing Info successfully created.",
            'data': customer
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class BillingDetailView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = BillingSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Billing.objects.filter(user=token.user).filter(pk=self.kwargs.get('id', ''))

    def retrieve(self, request, *args, **kwargs):
        billing = self.get_object()
        serializer = BillingSerializer(billing)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Details successfully fetched.",
            'data': {
                'billing_info': serializer.data,
                'email': request.user.email
            }
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        billing = self.get_object()
        serializer = BillingSerializer(billing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Billing Info successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_billing_card(request):
    stripe.api_key = settings.STRIPE_API_KEY
    card_id = request.data['id']
    token = get_token_obj(request.auth)
    billing_obj = Billing.objects.get(user=token.user)
    customer = stripe.Customer.retrieve(billing_obj.customer_id)
    customer.sources.retrieve(card_id).delete()

    data = {
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Card is Successfully removed",
    }
    return Response(data, status=status.HTTP_200_OK)