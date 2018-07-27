import stripe
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import status

from wirfi_app.models import Billing, Business, Profile, Device
from wirfi_app.serializers import UserSerializer, DeviceSerializer, DeviceSerialNoSerializer, BusinessSerializer, \
    UserProfileSerializer, BillingSerializer

User = get_user_model()


class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DeviceSerialNoView(generics.ListCreateAPIView):
    serializer_class = DeviceSerialNoSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user)

    def create(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        serializer = DeviceSerialNoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = DeviceSerializer

    def get(self, request, *args, **kwargs):
        token = get_token_obj(self.request.auth)
        device = Device.objects.filter(user=token.user).get(pk=self.kwargs['id'])
        return Response(DeviceSerializer(device).data)

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
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BillingApiView(viewsets.ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer


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
    print(data)
    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here: https://dashboard.stripe.com/account/apikeys
    stripe.api_key = "sk_test_FLCaTLlnXR6AZEu3JTsMv9Ld"

    # Token is created using Checkout or Elements!
    # Get the payment token ID submitted by the form:
    token = data['id'].strip()
    print(token)

    charge = stripe.Charge.create(
        amount=999,
        currency='usd',
        description='Example charge',
        source=token,
    )
    return Response({"message": "Got some data!", "data": data})
