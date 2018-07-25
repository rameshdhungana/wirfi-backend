from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import status

from wirfi_app.models import Billing, Business, Profile, Device
from wirfi_app.serializers import UserSerializer, DeviceSerializer, DeviceSerialNoSerializer, BusinessSerializer, UserProfileSerializer, BillingSerializer

User = get_user_model()


class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DeviceSerialNoView(generics.ListCreateAPIView):
    serializer_class = DeviceSerialNoSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.META.get('HTTP_AUTHORIZATION', ''))
        return Device.objects.filter(user=token.user)

    def create(self, request, *args, **kwargs):
        token = get_token_obj(request.META.get('HTTP_AUTHORIZATION', ''))
        serializer = DeviceSerialNoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = DeviceSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.META.get('HTTP_AUTHORIZATION', ''))
        return Device.objects.filter(user=token.user).get(pk=self.kwargs['id'])

    def update(self, request, *args, **kwargs):
        device = self.get_object()
        serial_number = request.data.pop('serial_number', '')
        if serial_number:
            serializer = DeviceSerialNoSerializer(device, data={'serial_number': serial_number})
            serializer.is_valid(raise_exception=True)
            serializer.save()

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
    print(token[6:])
    return Token.objects.get(key=token[6:])
