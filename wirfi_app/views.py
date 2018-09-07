import stripe
import datetime
import re
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
from rest_framework import status
from rest_auth.registration.views import RegisterView, VerifyEmailView, VerifyEmailSerializer
from rest_auth.views import LoginView, \
    PasswordResetView, PasswordResetConfirmView, PasswordChangeView, \
    PasswordResetSerializer, PasswordResetConfirmSerializer, PasswordChangeSerializer

from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup

from wirfi_app.models import Billing, Business, Profile, \
    Device, Industry, DeviceLocationHours, DeviceNetwork, DeviceStatus, \
    Subscription, AuthorizationToken, DEVICE_STATUS, DeviceSetting, DeviceNotification, NOTIFICATION_TYPE, READ, \
    PresetFilter
from wirfi_app.serializers import UserSerializer, \
    DeviceSerializer, DeviceLocationHoursSerializer, DeviceNetworkSerializer, \
    DeviceStatusSerializer, \
    BusinessSerializer, BillingSerializer, \
    UserRegistrationSerializer, LoginSerializer, AuthorizationTokenSerializer, \
    IndustryTypeSerializer, DeviceMuteSettingSerializer, DevicePrioritySettingSerializer, DeviceNotificationSerializer, \
    PresetFilterSerializer

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)

User = get_user_model()


def valid_password_regex(password):
    valid = re.match(settings.PASSWORD_VALIDATION_REGEX_PATTERN, password)
    return valid


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
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def profile_images_view(request, id):
    profile_picture = request.FILES.get('profile_picture', '')
    user = get_token_obj(request.auth).user
    if not profile_picture and not user.profile.profile_picture:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Please upload the image."},
            status=status.HTTP_400_BAD_REQUEST)

    try:
        profile = Profile.objects.get(user__id=id)
        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()
        user = UserSerializer(profile.user).data
        return Response({
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Images Successfully uploaded.",
            "data": user},
            status=status.HTTP_200_OK)

    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)


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
        serializer = IndustryTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully added industry type.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class IndustryTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user)).filter(pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        industry_type = self.get_object()
        serializer = IndustryTypeSerializer(industry_type)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully fetched industry type.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        industry_type = self.get_object()
        token = get_token_obj(self.request.auth)
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


class DeviceView(generics.ListCreateAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Device.objects.filter(user=token.user)

    def list(self, request, *args, **kwargs):
        devices = self.get_queryset()
        serializer = DeviceSerializer(devices, many=True)
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
        industry_id = request.data.get('industry_type_id', '')
        if not industry_id:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry Type can't be null/blank."
            }, status=status.HTTP_400_BAD_REQUEST)

        industry = Industry.objects.get(pk=industry_id)

        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user, industry_type=industry)
        DeviceSetting.objects.create(device_id=serializer.data['id'])
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully device created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['POST'])
def mute_device_view(request, device_id):
    try:
        device_obj = Device.objects.get(pk=device_id)
        device_setting, _ = DeviceSetting.objects.get_or_create(device=device_obj)
        mute_serializer = DeviceMuteSettingSerializer(device_setting, data=request.data)
        mute_serializer.is_valid(raise_exception=True)
        mute_serializer.save()
        # payload = mute_serializer.data

        # except:
        #     device_setting_obj = DeviceSetting.objects.get(device=device_obj)
        #     device_setting_obj.is_muted = request.data['is_muted']
        #     device_setting_obj.mute_duration = request.data['mute_duration']
        #     device_setting_obj.save()
        #     payload = {
        #         "mute_settings": {
        #             'is_muted': device_setting_obj.is_muted,
        #             'mute_start': device_setting_obj.mute_start,
        #             'mute_duration': device_setting_obj.mute_duration
        #         },
        #     }
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
        if not industry_id and not industry_name:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry Type can't be null/blank."
            }, status=status.HTTP_400_BAD_REQUEST)

        if industry_name:
            industry = Industry.objects.create(name=industry_name, user=token.user)
        else:
            industry = Industry.objects.get(pk=industry_id)

        serializer = DeviceSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user, industry_type=industry)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
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
            'data': DeviceNetworkSerializer(network[0]).data if network else {}
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device = Device.objects.get(pk=self.kwargs['device_id'])
        serializer = DeviceNetworkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=device)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceNetworkDetailView(generics.RetrieveUpdateAPIView):
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


class DeviceNotificationView(generics.ListCreateAPIView):
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(device_id=self.kwargs['device_id'], type=type).order_by('-id')

    def list(self, request, *args, **kwargs):
        notifications = []

        for key, value in enumerate(NOTIFICATION_TYPE):
            type_value, type_name = value[0], value[1]
            print(type_value, type_name)
            noti = self.get_each_type_queryset(type_value)
            serializer = DeviceNotificationSerializer(noti, many=True)

            notifications.append({"type": type_value, "type_name": type_name, "notifications": serializer.data})

        print(notifications[0])

        data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Notifications fetched successfully",
            "data":
                {"read_type": READ,
                 "notifications": notifications}
        }
        return Response(data, status=status.HTTP_200_OK)


def create(self, request, *args, **kwargs):
    print(request.data)
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


class AllNotificationView(generics.ListAPIView):
    serializer_class = DeviceNotificationSerializer

    def get_each_type_queryset(self, type):
        return DeviceNotification.objects.filter(type=type).order_by('-id')

    def list(self, request, *args, **kwargs):
        notifications = []

        for key, value in enumerate(NOTIFICATION_TYPE):
            type_value, type_name = value[0], value[1]
            print(type_value, type_name)
            noti = self.get_each_type_queryset(type_value)
            serializer = DeviceNotificationSerializer(noti, many=True)

            notifications.append({"type": type_value, "type_name": type_name, "notifications": serializer.data})

        print(notifications[0])

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
        billings = self.get_queryset()
        stripe_customer_info = self.retrieve_stripe_customer_info()
        if stripe_customer_info:
            message = "Details successfully fetched"
            code = getattr(settings, 'SUCCESS_CODE', 1)
        else:
            message = "No any billing data"
            code = 2

        serializer = BillingSerializer(billings, many=True)

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
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_200_OK, headers=headers)

    def create(self, request, *args, **kwargs):
        data = request.data
        # Set your secret key: remember to change this to your live secret key in production
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = settings.STRIPE_API_KEY

        # Token is created using Checkout or Elements!
        # Get the payment token ID submitted by the form:
        stripe_token = data['id'].strip()
        email = data['email']

        token = get_token_obj(request.auth)
        serializer = BillingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            billing_obj = Billing.objects.get(user=token.user)
            customer = stripe.Customer.retrieve(billing_obj.customer_id)
            customer.sources.create(source=stripe_token)
        except:
            customer = stripe.Customer.create(
                source=stripe_token,
                email=email
            )
            serializer.save(user=token.user, customer_id=customer.id)

        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Billing Info successfully created.",
            'data': serializer.data
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
        serializer.save(user=token.user)
        return Response({
            "code": getattr(settings, "SUCCESS_CODE", 1),
            "message": "Successfully fetched preset filter data.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class PresetFilterDeleteView(generics.DestroyAPIView):
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
                'profile_picture': self.user.profile.profile_picture.url if hasattr(self.user, 'profile') else '',
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


class ResetPasswordView(PasswordResetView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).post(request, *args, **kwargs)
        try:
            User.objects.get(email=request.data['email'])

            response.data = {
                "code": getattr(settings, 'SUCCESS_CODE', 1),
                "message": "Password reset e-mail has been sent. Please check your e-mail."
            }
        except ObjectDoesNotExist:
            response.data = {
                "code": 0,
                "message": "User with this email does not exit"
            }
        return response


class ResetPasswordConfirmView(PasswordResetConfirmView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        if not valid_password_regex(request.data['new_password1']):
            data = {
                "code": 0,
                "message": "Password must be 6 characters long with at least 1 capital, 1 small and 1 special character."
            }
            return Response(data)
        response = super(ResetPasswordConfirmView, self).post(request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Password has been successfully reset with new password."
        }
        return response


class ChangePasswordView(PasswordChangeView):
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        if not valid_password_regex(request.data['new_password1']):
            data = {
                "code": 0,
                "message": "Password must be 6 characters long with at least 1 capital, 1 small and 1 special character."
            }
            return Response(data)
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
                "code": 0,
                "message": "Password Reset Link is Invalid",
            }
        return Response(data, status=status.HTTP_200_OK)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        data = {
            "code": 0,
            "message": "Password Reset Link is Invalid",
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
