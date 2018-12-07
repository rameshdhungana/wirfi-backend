from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceStatus, Industry, Franchise, DEVICE_STATUS
from wirfi_app.serializers import DeviceSerializer, DeviceStatusSerializer, IndustryTypeSerializer, \
    LocationTypeSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log


class DeviceView(generics.ListCreateAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return Device.objects.filter(user=self.request.auth.user)

    def list(self, request, *args, **kwargs):
        user = request.auth.user
        industry_types = Industry.objects.filter(Q(user=user) | Q(user__isnull=True))
        industry_serializer = IndustryTypeSerializer(industry_types, many=True)
        location_types = Franchise.objects.filter(user=user)
        location_serializer = LocationTypeSerializer(location_types, many=True)
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
                'location_type': location_serializer.data,
                'status_dict': {x: y for x, y in DEVICE_STATUS}
            }
        }

        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.auth.user
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
        serializer.save(user=user, industry_type=industry, location_type=franchise)

        create_activity_log(
            request,
            "Device '{s_no}' added to user '{email}'.".format(s_no=serializer.data['serial_number'], email=user.email)
        )

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully device created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED)


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
        return Device.objects.filter(user=self.request.auth.user).filter(pk=self.kwargs['id'])

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
        user = request.auth.user
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
            industry = Industry.objects.create(name=industry_name, user=user)
        else:
            industry = Industry.objects.get(pk=industry_id)

        franchise = Franchise.objects.get(pk=franchise_id)

        serializer = DeviceSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, industry_type=industry, location_type=franchise)
        create_activity_log(
            request,
            "Device '{s_no}' of user '{email} updated.".format(s_no=serializer.data['serial_number'], email=user.email)
        )
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        create_activity_log(
            request,
            "Device '{s_no}' of user '{email}' deleted.".format(s_no=instance.serial_number,
                                                                email=request.auth.user.email)
        )
        instance.delete()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully deleted."
        }
        return Response(data, status=status.HTTP_200_OK)


def get_current_device_status(device_id):
    statuses = DeviceStatus.objects.filter(device_id=device_id).order_by('-id')
    for i in range(len(statuses)):
        if statuses[i].status != statuses[0].status:
            return DeviceStatusSerializer(statuses[i - 1]).data
    return {}
