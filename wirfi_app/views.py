import stripe
import datetime
import re, hashlib
import copy

from django.db.models import Q
from django.contrib.auth import get_user_model, logout as django_logout
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.contrib.auth.tokens import default_token_generator

from django.views.decorators.debug import sensitive_post_parameters

from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_auth.registration.views import RegisterView, VerifyEmailView, VerifyEmailSerializer
from rest_auth.views import LoginView, \
    PasswordResetConfirmView, PasswordChangeView, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, PasswordChangeSerializer

from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup

from wirfi_app.models import Billing, Business, Profile, Franchise, \
    Device, Industry, DeviceNetwork, DeviceStatus, DeviceSetting, DeviceCameraServices, \
    Subscription, AuthorizationToken, DEVICE_STATUS, DeviceNotification, PresetFilter, \
    UserActivationCode, READ, NOTIFICATION_TYPE
from wirfi_app.serializers import UserSerializer, \
    DeviceSerializer, DeviceNetworkSerializer, DeviceCameraSerializer, \
    DeviceStatusSerializer, IndustryTypeSerializer, LocationTypeSerializer, \
    BusinessSerializer, BillingSerializer, \
    UserRegistrationSerializer, LoginSerializer, AuthorizationTokenSerializer, \
    DeviceMuteSettingSerializer, DeviceSleepSerializer, \
    DevicePrioritySettingSerializer, DeviceNotificationSerializer, \
    PresetFilterSerializer, ResetPasswordMobileSerializer, CheckVersionSerializer

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)

User = get_user_model()


def valid_password_regex(password):
    valid = re.match(settings.PASSWORD_VALIDATION_REGEX_PATTERN, password)
    return valid


def franchise_type_name_already_exits(name, token):
    for key, value in enumerate(
            Franchise.objects.filter(Q(user__isnull=True) | Q(user=token.user)).values_list('name', flat=True)):
        if name.upper() == value.upper():
            return True
        return False


def industry_type_name_already_exits(name, token):
    for key, value in enumerate(
            Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user)).values_list('name', flat=True)):
        if name.upper() == value.upper():
            return True
        return False


class CheckVersion(generics.CreateAPIView):
    serializer_class = CheckVersionSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_type = serializer.validated_data['device_type']
        version = serializer.validated_data['app_version']
        print(device_type, version)
        if not self.check_version(device_type, version):
            data = {
                "message": "Your app is outdated. Please update it."
            }
            if getattr(settings, 'OPTIONAL_UPDATE'):
               data["code"] = getattr(settings, 'APP_UPDATE_MANDATORY')
            else: 
                data["code"] = getattr(settings, 'APP_UPDATE_OPTIONAL')
            
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)
    
        return Response({
            "code": getattr(settings, 'SUCCESS_CODE'),
            "message": "Your app is up to date."
        }, status=status.HTTP_200_OK)

    def check_version(self, device_type, version):
        if device_type == '1':
            if version == getattr(settings, 'IOS_VERSION'):
                return True

        elif device_type == '2':
            if version == getattr(settings, 'ANDROID_VERSION'):
                return True

        return False

class UserDetailView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        token = get_token_obj(self.request.auth)
        data = request.data
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "User successfully updated",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def profile_images_view(request, id):
    profile_picture = request.FILES.get('profile_picture', '')
    user = get_token_obj(request.auth).user
    if not profile_picture:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Please upload the image."},
            status=status.HTTP_400_BAD_REQUEST)

    profile = Profile.objects.filter(user__id=id)
    if profile:
        profile[0].profile_picture = profile_picture
        profile[0].save()
    else:
        profile = Profile.objects.create(user=user, phone_number='', address='', profile_picture=profile_picture)

    user = UserSerializer(user).data
    return Response({
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Images Successfully uploaded.",
        "data": user},
        status=status.HTTP_200_OK)


class IndustryTypeListView(generics.ListCreateAPIView):
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user))

    def list(self, request, *args, **kwargs):
        industry_types = self.get_queryset()
        serializer = IndustryTypeSerializer(industry_types, many=True)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully fetched industry types.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if industry_type_name_already_exits(request.data['name'], token):
            return Response({
            'code': getattr(settings, 'ERROR_CODE', 0),
            'message': "Industry type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndustryTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully added industry type.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class IndustryTypeDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    lookup_field = 'id'
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user)).filter(pk=self.kwargs['id'])

    def update(self, request, *args, **kwargs):
        industry_type = self.get_object()
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if industry_type_name_already_exits(request.data['name'], token):
            return Response({
            'code': getattr(settings, 'ERROR_CODE', 0),
            'message': "Industry type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndustryTypeSerializer(industry_type, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully updated industry type.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted industry type."
        }, status=status.HTTP_200_OK)


class LocationTypeListView(generics.ListCreateAPIView):
    serializer_class = LocationTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Franchise.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        location_types = self.get_queryset()
        serializer = LocationTypeSerializer(location_types, many=True)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully fetched location types.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if franchise_type_name_already_exits(request.data['name'], token):
            return Response({
            'code': getattr(settings, 'ERROR_CODE', 0),
            'message': "Franchise type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        data['user'] = token.user.id
        serializer = LocationTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully added location type.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class LocationTypeDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    lookup_field = 'id'
    serializer_class = LocationTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Franchise.objects.filter(user=token.user)

    def update(self, request, *args, **kwargs):
        franchise_type = self.get_object()
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if franchise_type_name_already_exits(request.data['name'], token):
            return Response({
            'code': getattr(settings, 'ERROR_CODE', 0),
            'message': "Franchise type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        data = {**request.data, 'user': token.user.id}
        serializer = LocationTypeSerializer(franchise_type, data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully updated franchise type.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted franchise type."
        }, status=status.HTTP_200_OK)


class DeviceView(generics.ListCreateAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        token_obj = get_token_obj(self.request.auth)
        industry_types = Industry.objects.filter(Q(user=token_obj.user) | Q(user__isnull=True))
        industry_serializer = IndustryTypeSerializer(industry_types, many=True)
        location_types = Franchise.objects.filter(user=token_obj.user)
        location_serailizer = LocationTypeSerializer(location_types, many=True)
        devices = self.get_queryset()
        serializer = DeviceSerializer(devices, many=True)
        response_data = serializer.data
        for data in response_data:
            data['device_status'] = get_current_device_status(data['id'])

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Details successfully fetched.",
            'data': {
                'device': response_data,
                'industry_type': industry_serializer.data,
                'location_type': location_serailizer.data,
                'status_dict': {x: y for x, y in DEVICE_STATUS}
            }
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        industry_id = request.data.get('industry_type_id', '')
        franchise_id = request.data.get('location_type_id', '')
        if not industry_id:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry Type can't be null/blank."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not franchise_id:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Location Type can't be null/blank."
            }, status=status.HTTP_400_BAD_REQUEST)

        industry = Industry.objects.get(pk=industry_id)
        franchise = Franchise.objects.get(pk=franchise_id)

        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user, industry_type=industry, location_type=franchise)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully device created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED)


def get_current_device_status(device_id):
    statuses = DeviceStatus.objects.filter(device_id=device_id).order_by('-id')
    for i in range(len(statuses)):
        if statuses[i].status != statuses[0].status:
            return DeviceStatusSerializer(statuses[i - 1]).data
    return {}


@api_view(['POST'])
def mute_device_view(request, id):
    try:
        device_obj = Device.objects.get(pk=id)
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device_obj)
        mute_serializer = DeviceMuteSettingSerializer(device_setting, data=request.data)
        mute_serializer.is_valid(raise_exception=True)
        mute_serializer.save()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device Mute status is Changed.",
            'data': mute_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def device_priority_view(request, id):
    try:
        device = Device.objects.get(pk=id)
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device)
        serializer = DevicePrioritySettingSerializer(device_setting, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully priority updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)


class DeviceSleepView(generics.CreateAPIView):
    serializer_class = DeviceSleepSerializer

    def get_queryset(self):
        device_obj = Device.objects.get(pk=self.kwargs['id'])
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device_obj)
        return device_setting

    def create(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = DeviceSleepSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully sleep settings updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceCameraView(generics.ListCreateAPIView):
    serializer_class = DeviceCameraSerializer

    def get_queryset(self):
        return DeviceCameraServices.objects.filter(device_id=self.kwargs['id'])

    def list(self, request, *args, **kwargs):
        serializer = DeviceCameraSerializer(self.get_queryset(), many=True)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully fetched device's camera information.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device_obj = Device.objects.get(pk=self.kwargs['id'])
        serializer = DeviceCameraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device_obj)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully added device's camera information.",
            'data': {'camera_service': serializer.data}
        }
        return Response(data, status=status.HTTP_201_CREATED)


class DeviceCameraDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = DeviceCameraSerializer

    def get_queryset(self):
        return DeviceCameraServices.objects.filter(device_id=self.kwargs['device_id'])

    def update(self, request, *args, **kwargs):
        serializer = DeviceCameraSerializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully updated device's camera information.",
            'data': {'camera_service': serializer.data}
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Sucesfully deleted device's camera information."
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def device_images_view(request, id):
    location_logo = request.FILES.get('location_logo', '')
    machine_photo = request.FILES.get('machine_photo', '')
    if not (location_logo and machine_photo):
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Please upload both the images."},
            status=status.HTTP_400_BAD_REQUEST)

    try:
        device = Device.objects.get(pk=id)
        device.location_logo = location_logo
        device.machine_photo = machine_photo
        device.save()
        data = DeviceSerializer(device).data
        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Images Successfully uploaded.",
            "data": data},
            status=status.HTTP_200_OK)

    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)


class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = DeviceSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user).filter(pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        device = self.get_object()
        serializer = DeviceSerializer(device)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        device = self.get_object()
        token = get_token_obj(self.request.auth)
        industry_id = request.data.get('industry_type_id', '')
        industry_name = request.data.get('industry_name', '')
        franchise_id = request.data.get('location_type_id', '')

        if not franchise_id:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Location Type can't be null/blank."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not industry_id and not industry_name:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry Type can't be null/blank."
            }, status=status.HTTP_400_BAD_REQUEST)

        if industry_name:
            industry = Industry.objects.create(name=industry_name, user=token.user)
        else:
            industry = Industry.objects.get(pk=industry_id)

        franchise = Franchise.objects.get(pk=franchise_id)

        serializer = DeviceSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user, industry_type=industry, location_type=franchise)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully deleted."
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceNetworkView(generics.ListCreateAPIView):
    serializer_class = DeviceNetworkSerializer

    def get_queryset(self):
        return DeviceNetwork.objects.filter(device__id=self.kwargs['device_id'])

    def list(self, request, *args, **kwargs):
        network = self.get_queryset()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': DeviceNetworkSerializer(network, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device = Device.objects.get(pk=self.kwargs['device_id'])
        device_network = DeviceNetwork.objects.filter(device=device)
        if len(device_network) >= 2:
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Multiple secondary networks can't be set."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        if (len(DeviceNetwork.objects.filter(device=device, primary_network=True))==0 and not data['primary_network']):
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Secondary network can't be set first."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if (len(DeviceNetwork.objects.filter(device=device, primary_network=True))==1 and data['primary_network']):
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Multiple primary network can't be set."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = DeviceNetworkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceNetworkDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = DeviceNetworkSerializer

    def get_queryset(self):
        return DeviceNetwork.objects.filter(pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        network = self.get_object()
        serializer = DeviceNetworkSerializer(network)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        network = self.get_object()
        device = Device.objects.get(pk=self.kwargs['device_id'])
        serializer = DeviceNetworkSerializer(network, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.primary_network:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Primary network can't be deleted."
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Secondary network successfully deleted."
        }, status=status.HTTP_200_OK)


class DeviceNotificationView(generics.CreateAPIView):
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(device_id=self.kwargs['device_id'], type=type).order_by('-id')

    # def list(self, request, *args, **kwargs):
    #     notifications = []
    #
    #     for index, (type_value, type_name) in enumerate(NOTIFICATION_TYPE):
    #         noti = self.get_each_type_queryset(type_value)
    #         serializer = DeviceNotificationSerializer(noti, many=True)
    #
    #         notifications.append({"type": type_value, "type_name": type_name, "notifications": serializer.data})
    #
    #     data = {
    #         "code": getattr(settings, 'SUCCESS_CODE', 1),
    #         'message': "Notifications fetched successfully",
    #         "data":
    #             {"read_type": READ,
    #              "notifications": notifications}
    #     }
    #     return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device = Device.objects.get(pk=self.kwargs['device_id'])
        serializer = DeviceNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device Notifications created successfully",
            "data": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class UpdateNotificationView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = DeviceNotificationSerializer
    queryset = DeviceNotification.objects.all()

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.type = READ
        notification.save()
        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Notifications is updated to READ Type successfully",
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Successfully deleted notification."
        }, status=status.HTTP_200_OK)


class AllNotificationView(generics.ListAPIView):
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(type=type).order_by('-id')

    def list(self, request, *args, **kwargs):
        notifications = []

        for index, (type_value, type_name) in enumerate(NOTIFICATION_TYPE):
            noti = self.get_each_type_queryset(type_value)
            serializer = DeviceNotificationSerializer(noti, many=True)

            notifications.append({"type": type_value, "type_name": type_name, "notifications": serializer.data})

        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "All Notifications fetched successfully",
            "data":
                {"read_type": READ,
                 "notifications": notifications}
        }
        return Response(data, status=status.HTTP_200_OK)


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
        business = self.get_object()
        serializer = BusinessSerializer(business, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_device_status_view(request, id):
    device_status = DeviceStatus()
    device_status.status = request.data['status']
    device_status.device_id = id
    device_status.save()
    return Response({
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'message': 'Device status successfully added.'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def dashboard_view(request):
    industry_type = []
    donut_chart = {}
    token = get_token_obj(request.auth)
    device_status_dict = {x: y for x, y in DEVICE_STATUS}
    donut = {value: 0 for key, value in device_status_dict.items()}
    device_industries = Industry.objects.filter(Q(user=token.user) | Q(user_id__isnull=True))
    for industry in device_industries:
        industry_type.append(industry.name)
        donut_chart[industry.name] = copy.deepcopy(donut)

    # today_date = datetime.date.today()
    device_status = DeviceStatus.objects.filter(device__user=token.user).order_by('device', '-id').distinct('device')
    # .filter(date__year=2018, date__month=8, date__day=16)

    for device in device_status:
        donut_chart[device.device.industry_type.name][device_status_dict[device.status]] += 1

    donut_chart = {key: [{'status': device_status, 'value': count} for device_status, count in value.items()] for
                   key, value in donut_chart.items()}

    return Response({
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'message': "Successfully data fetched.",
        'data': {
            'donut_chart': donut_chart,
            'signal_graph': '2',
            'industry_type': industry_type,
            'donut_count': len(device_status),
            'donut_data_format': [{'status': key, 'value': 0} for key in donut.keys()]
        }
    }, status=status.HTTP_200_OK)


class PresetFilterView(generics.ListCreateAPIView):
    serializer_class = PresetFilterSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return PresetFilter.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        presets = self.get_queryset()
        serializer = PresetFilterSerializer(presets, many=True)
        return Response({
            "code": getattr(settings, "SUCCESS_CODE", 1),
            "message": "Successfully fetched preset filter data.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        token = get_token_obj(self.request.auth)
        serializer = PresetFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(user=token.user)
            return Response({
                "code": getattr(settings, "SUCCESS_CODE", 1),
                "message": "Successfully fetched preset filter data.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "code": getattr(settings, "ERROR_CODE", 0),
                "messsage": "This preset name already exists",
            }, status=status.HTTP_400_BAD_REQUEST)


class PresetFilterDeleteView(generics.RetrieveAPIView, generics.DestroyAPIView):
    serializer_class = PresetFilterSerializer
    lookup_field = 'id'

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return PresetFilter.objects.filter(user=token.user).filter(pk=self.kwargs['id'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted preset filter."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PresetFilterSerializer(instance)

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Preset Detail is fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class Login(LoginView):
    """
        Check the credentials and return the REST Token
        if the credentials are valid and authenticated.k
        Calls Django Auth login method to register User ID
        in Django session framework

        Accept the following POST parameters: username, password
        Return the REST Framework Token Object's key.
    """

    serializer_class = LoginSerializer
    token_model = AuthorizationToken

    def create_token(self):
        push_notification = self.serializer.validated_data['push_notification_token']
        device_id = self.serializer.validated_data['device_id']
        device_type = self.serializer.validated_data['device_type']
        token, _ = self.token_model.objects.get_or_create(user=self.user,
                                                          push_notification_token=push_notification,
                                                          device_id=device_id,
                                                          device_type=device_type)
        return token

    def get_response_serializer(self):
        response_serializer = AuthorizationTokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.token = self.create_token()
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        first_login = False if self.serializer.validated_data['user'].last_login else True
        self.login()
        self.user.last_login = datetime.datetime.now()
        self.user.save()
        response = self.get_response()
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully Logged In.",
            'data': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'profile_picture': self.user.profile.profile_picture.url if (
                        hasattr(self.user, 'profile') and self.user.profile.profile_picture) else '',
                'auth_token': response.data.get('key'),
                'device_id': response.data.get('device_id'),
                'device_type': response.data.get('device_type'),
                'push_notification_token': response.data.get('push_notification_token'),
                'is_first_login': first_login
            }
        }
        return response


@api_view(['POST'])
def logout(request):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    try:
        AuthorizationToken.objects.filter(key=request.auth).delete()
    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)

    django_logout(request)
    return Response({"code": getattr(settings, 'SUCCESS_CODE', 1), "message": "Successfully logged out."},
                    status=status.HTTP_200_OK)


class RegisterUserView(RegisterView):
    serializer_class = UserRegistrationSerializer
    token_model = AuthorizationToken

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            data = {
                'code': getattr(settings, 'SUCCESS_CODE', 1),
                'message': "Please check your email for account validation link. Thank you.",
            }
            return data

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user


class VerifyEmailRegisterView(VerifyEmailView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        response = super(VerifyEmailRegisterView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Email Successfully verified."
        }
        return response


class ResetPasswordView(generics.CreateAPIView):
    """
    Calls Django Auth PasswordResetForm save method.

    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data['email'])
            activation_obj = UserActivationCode.objects.filter(user=user)

            if activation_obj:
                activation_code = get_activation_code(user, activation_obj[0].count)
                activation_obj.update(code=activation_code, count=activation_obj[0].count + 1, once_used=False)

            else:
                activation_code = get_activation_code(user, 0)
                activation_obj = UserActivationCode.objects.create(user=user, code=activation_code)

            # Create a serializer with request.data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Return the success message with OK HTTP status
            return Response({
                "code": getattr(settings, 'SUCCESS_CODE', 1),
                "message": "Password reset e-mail has been sent. Please check your e-mail."
            }, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password reset e-mail has been sent. Please check your e-mail."
            }, status=status.HTTP_200_OK)


def get_activation_code(user, count):
    hash_string = "{uid}:{email}#{count}".format(uid=str(user.id), email=user.email, count=str(count + 1))
    return int(hashlib.sha256(hash_string.encode('utf-8')).hexdigest(), 16) % 10 ** 6


class ResetPasswordConfirmView(PasswordResetConfirmView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        if not valid_password_regex(request.data['new_password1']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password must be 8 characters long with at least 1 number or 1 special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (request.data['new_password1'] == request.data['new_password2']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Passwords didn't match."
            }, status=status.HTTP_400_BAD_REQUEST)

        response = super().post(request, *args, **kwargs)
        UserActivationCode.objects.filter(user__email=request.data['email']).update(once_used=True)

        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password has been successfully reset with new password."
        }
        return response


class ResetPasswordConfirmMobileView(generics.CreateAPIView):
    serializer_class = ResetPasswordMobileSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        if not valid_password_regex(data['new_password1']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password must be 8 characters long with at least 1 number or 1 special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordMobileSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password reset successfully done."
        }, status=status.HTTP_200_OK)


class ChangePasswordView(PasswordChangeView):
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        if not valid_password_regex(request.data['new_password1']):
            return Response({
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password must be 8 characters long with at least 1 number or 1 special character."
            }, status=status.HTTP_400_BAD_REQUEST)

        response = super(ChangePasswordView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "New password has been saved."
        }
        return response


@api_view(['GET'])
def get_logged_in_user(request):
    serializer = UserSerializer(request.user, context={'request': request})
    serializer_data = serializer.data
    data = {
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Successfully fetched.",
        "data": serializer_data
    }

    return Response(data, status=status.HTTP_200_OK)


def get_token_obj(token):
    return AuthorizationToken.objects.get(key=token)


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


@api_view(['GET'])
def validate_reset_password(request, uid, token):
    # Decode the uidb64 to uid to get User object
    try:
        uid = force_text(uid_decoder(uid))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            data = {
                "code": getattr(settings, 'SUCCESS_CODE', 1),
                "message": "Password Reset Link is valid",
                "data": {
                    "email": user.email
                }
            }
        else:
            data = {
                "code": getattr(settings, 'ERROR_CODE', 0),
                "message": "Password Reset Link is Invalid",
            }
        return Response(data, status=status.HTTP_200_OK)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        data = {
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Password Reset Link is Invalid",
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
