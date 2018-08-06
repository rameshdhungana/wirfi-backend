import stripe

from django.contrib.auth import get_user_model, logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import status
from rest_auth.registration.views import RegisterView, VerifyEmailView, VerifyEmailSerializer
from rest_auth.views import LoginView, \
    PasswordResetView, PasswordResetConfirmView, PasswordChangeView, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, PasswordChangeSerializer

from allauth.account import app_settings as allauth_settings
# from rest_auth.app_settings import TokenSerializer, JWTSerializer, create_token

from wirfi_app.models import Billing, Business, Profile, Device, Subscription
from wirfi_app.serializers import UserSerializer, UserProfileSerializer, \
    DeviceSerializer, DeviceSerialNoSerializer, DeviceNetworkSerializer, \
    BusinessSerializer, BillingSerializer, \
    UserRegistrationSerializer, LoginSerializer

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


class BusinessView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Business.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        businesses = self.get_queryset()
        if not businesses:
            data = {
                'code': getattr(settings, 'NO_DATA_CODE', 2),
                'message': "No any associated business info. Please add them."
            }
            return Response(data, status=status.HTTP_200_OK)


        serializer = BusinessSerializer(businesses[0])
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Details successfully fetched.",
            'data': {
                'business_info': serializer.data
            }
        }
        return Response(data, status=status.HTTP_200_OK, headers=headers)

    def create(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        serializer = BusinessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class BusinessDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    lookup_field = 'id'
    serializer_class = BusinessSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Business.objects.filter(user=token.user).filter(pk=self.kwargs.get('id', ''))

    def update(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        billing = self.get_object()
        serializer = BillingSerializer(billing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


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


class Login(LoginView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        user = self.serializer.validated_data['user']
        super(Login, self).login()
        response = super(Login, self).get_response()

        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully Logged In.",
            'data': {
                'auth_token': response.data.get('key'),
                'is_first_login': False if user.last_login else True,
                'last_login': user.last_login
             }
        }
        return response


@api_view(['POST'])
def logout(request, *args, **kwargs):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)

    django_logout(request)
    return Response({"code": getattr(settings, 'SUCCESS_CODE', 1), "message": "Successfully logged out."},
                    status=status.HTTP_200_OK)


class RegisterUserView(RegisterView):
    serializer_class = UserRegistrationSerializer

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            data = {
                'code': getattr(settings, 'SUCCESS_CODE', 1),
                'message': "Please check your email for account validation link. Thank you.",
            }
            return data


class VerifyEmailRegisterView(VerifyEmailView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        response = super(VerifyEmailRegisterView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Email Successfully verified."
        }
        return response


class ResetPasswordView(PasswordResetView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password reset e-mail has been sent. Please check your e-mail."
        }
        return response


class ResetPasswordConfirmView(PasswordResetConfirmView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        response = super(ResetPasswordConfirmView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password has been successfully reset with new password."
        }
        return response


class ChangePasswordView(PasswordChangeView):
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        response = super(ChangePasswordView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "New password has been saved."
        }
        return response
