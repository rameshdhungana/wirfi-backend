from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import DeviceStatus


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
