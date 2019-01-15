import copy
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceStatus, Industry, Franchise, DEVICE_STATUS
from wirfi_app.serializers import DeviceStatusSerializer


@api_view(['GET'])
def dashboard_view(request):
    '''
    API to get User's dashboard information.
    '''

    industry_type = []
    donut_chart = {}
    device_status_dict = {x: y for x, y in DEVICE_STATUS}
    donut = {value: 0 for key, value in device_status_dict.items()}
    device_industries = Industry.objects.filter(Q(user=request.auth.user) | Q(user_id__isnull=True))
    for industry in device_industries:
        industry_type.append(industry.name)
        donut_chart[industry.name] = copy.deepcopy(donut)
    device_status = DeviceStatus.objects.filter(device__user=request.auth.user).\
        order_by('device', '-id').distinct('device')

    for device in device_status:
        donut_chart[device.device.industry_type.name][device_status_dict[device.status]] += 1

    donut_chart = {key: [{'status': device_status, 'value': count} for device_status, count in value.items()] for
                   key, value in donut_chart.items()}

    # get statuses since 8 hours ago
    line_graph = {industry.name: [] for industry in device_industries}

    current_time = datetime.now()
    eight_hours_ago = (current_time - timedelta(hours=8)).replace(minute=0, second=0, microsecond=0)
    priority_devices = Device.objects.filter(user=request.auth.user).filter(device_settings__priority=True)
    for device in priority_devices:
        statuses = DeviceStatus.objects.filter(device=device). \
            filter(timestamp__gte=eight_hours_ago).order_by('id')
        status_list = [statuses[0], ] if statuses else []

        for i in range(len(statuses)):
            if i == 0:
                continue

            if statuses[i].status != statuses[i - 1].status:
                status_list.append(statuses[i])
        data_device = {
            'name': device.name,
            'data': DeviceStatusSerializer(status_list, many=True).data
        }

        line_graph[device.industry_type.name].append(data_device)

    return Response({
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'message': "Successfully data fetched.",
        'data': {
            'donut_chart': donut_chart,
            'line_graph': line_graph,
            'industry_type': industry_type,
            'donut_count': len(device_status),
            'donut_data_format': [{'status': key, 'value': 0} for key in donut.keys()]
        }
    }, status=status.HTTP_200_OK)
