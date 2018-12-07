import stripe
from django.conf import settings

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Billing
from wirfi_app.serializers import BillingSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log


class BillingView(generics.ListCreateAPIView):
    serializer_class = BillingSerializer

    def get_queryset(self):
        return Billing.objects.filter(user=self.request.auth.user)

    def retrieve_stripe_customer_info(self):
        stripe.api_key = settings.STRIPE_API_KEY
        user = self.request.auth.user
        billing = Billing.objects.filter(user=user).first()
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

        user = request.auth.user
        billing_obj = Billing.objects.filter(user=user)
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
                serializer.save(user=user, customer_id=customer.id)


            except:
                return Response({
                    'code': getattr(settings, 'ERROR_CODE', 0),
                    'message': "Stripe Token has already been used. Please try again with new token."
                }, status=status.HTTP_400_BAD_REQUEST)

        create_activity_log(request, "A card added to user '{email}'.".format(email=user.email))
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Billing Info successfully created.",
            'data': customer
        }
        return Response(data, status=status.HTTP_201_CREATED)


class BillingDetailView(generics.RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = BillingSerializer

    def get_queryset(self):
        return Billing.objects.filter(user=self.request.auth.user).filter(pk=self.kwargs.get('id', ''))

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

    # def update(self, request, *args, **kwargs):
    #     user = request.auth.user
    #     billing = self.get_object()
    #     serializer = BillingSerializer(billing, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=user)
    #     data = {
    #         'code': getattr(settings, 'SUCCESS_CODE', 1),
    #         'message': "Billing Info successfully updated.",
    #         'data': serializer.data
    #     }
    #     return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def delete_billing_card(request):
    stripe.api_key = settings.STRIPE_API_KEY
    card_id = request.data['id']
    user = request.auth.user
    billing_obj = Billing.objects.get(user=user)
    customer = stripe.Customer.retrieve(billing_obj.customer_id)
    customer.sources.retrieve(card_id).delete()
    create_activity_log(request, "A card of user '{email}' deleted.".format(email=user.email))

    data = {
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Card is Successfully removed",
    }
    return Response(data, status=status.HTTP_200_OK)
