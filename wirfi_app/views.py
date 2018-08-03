import stripe

from django.contrib.auth import get_user_model
from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import status
from rest_auth.registration.views import RegisterView
from allauth.account import app_settings as allauth_settings
from rest_auth.views import LoginView
from django.views.generic import TemplateView
from rest_auth.app_settings import (TokenSerializer,
                                    JWTSerializer,
                                    create_token)

from wirfi_app.models import Billing, Business, Profile, Device, Subscription
from wirfi_app.serializers import UserSerializer, UserProfileSerializer, DeviceSerializer, DeviceSerialNoSerializer, \
    DeviceNetworkSerializer, BusinessSerializer, BillingSerializer, UserRegistrationSerializer, LoginSerializer

User = get_user_model()


class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DeviceSerialNoView(generics.ListCreateAPIView):
    serializer_class = DeviceSerialNoSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        devices = self.get_queryset()
        serializer = DeviceSerialNoSerializer(devices, many=True)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Details successfully fetched.",
            'data': {
                'device': serializer.data
            }
        }
        return Response(data, status=status.HTTP_200_OK, headers=headers)

    def create(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        serializer = DeviceSerialNoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully device created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = DeviceSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user).filter(pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        device = self.get_object()
        serializer = DeviceSerialNoSerializer(device)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        device = self.get_object()
        token = get_token_obj(self.request.auth)
        serial_number = request.data.pop('serial_number', '')
        if serial_number:
            serializer = DeviceSerialNoSerializer(device, data={'serial_number': serial_number})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=token.user)

        serializer = DeviceSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceNetworkView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = DeviceNetworkSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user).filter(pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        device = self.get_object()
        serializer = DeviceSerialNoSerializer(device)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        device = self.get_object()
        token = get_token_obj(self.request.auth)
        serializer = DeviceNetworkSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class BillingView(generics.ListCreateAPIView):
    serializer_class = BillingSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Billing.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        billings = self.get_queryset()
        serializer = BillingSerializer(billings, many=True)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Details successfully fetched.",
            'data': {
                'billing_info': serializer.data,
                'email': request.user.email
            }
        }
        return Response(data, status=status.HTTP_200_OK, headers=headers)

    def create(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        serializer = BillingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Billing Info successfully created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

# Overwrites email confirmation url so that the correct url is sent in the email.
# to change the actual address, see core.urls name: 'account_confirm_email'

class MyAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse(
            "account_confirm_email",
            args=[emailconfirmation.key])
        print("test:",url);
        return settings.FRONTEND_HOST + url
        
class BillingDetailView(generics.RetrieveUpdateDestroyAPIView):
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


class BusinessApiView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer


class ProfileApiView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer


def get_token_obj(token):
    return Token.objects.get(key=token)


@api_view(['POST'])
def stripe_token_registration(request):
    data = request.data
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys
    stripe.api_key = settings.STRIPE_API_KEY

    # Token is created using Checkout or Elements!
    # Get the payment token ID submitted by the form:
    token = data['id'].strip()
    email = data['email']

    # # Create a Customer:
    customer = stripe.Customer.create(
        source=token,
        email=email
    )

    # Charge the Customer instead of the card:
    Subscription.objects.create(customer_id=customer.id, user=request.user, email=email, service_plan=1)

    # charge = stripe.Charge.create(
    #     amount=999,
    #     currency='usd',
    #     description='Example charge',
    #     source=token,
    #     statement_descriptor='Custom descriptor'
    # )
    charge = stripe.Charge.create(
        amount=1000,
        currency='usd',
        customer=customer.id,
        receipt_email=email
    )
    return Response({"code": 1, "message": "Got some data!", "data": data})


class RegisterUser(RegisterView):
    serializer_class = UserRegistrationSerializer

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            data = {
                'code': getattr(settings, 'SUCCESS_CODE', 1),
                'message': "Verification e-mail sent.",
            }
            return data


class Login(LoginView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        response = super(Login, self).post(request, *args, **kwargs)
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully Logged In.",
            'data': {'auth_token': response.data.get('key')}
        }
        return response


class VerifyEmailView(TemplateView):
    template_name = 'test.html'
