import copy
from datetime import datetime

from django.conf import settings
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceStatus, Industry, DEVICE_STATUS, STATUS_COLOR
from wirfi_app.serializers import DeviceLocationSerializer
from wirfi_app.serializers.device import get_eight_hours_statuses


@api_view(['GET'])
def dashboard_view(request):
    '''
    API to get User's dashboard information.
    '''

    current_time = datetime.now()
    industry_type = []
    donut_chart = {}
    device_status_dict = {x: y for x, y in DEVICE_STATUS}
    status_color = {device_status_dict[x]: y for x, y in STATUS_COLOR}
    donut = {value: 0 for key, value in device_status_dict.items()}

    devices = Device.objects.filter(user=request.auth.user)
    device_industries = Industry.objects.filter(Q(user=request.auth.user) | Q(user_id__isnull=True))

    for industry in device_industries:
        industry_type.append(industry.name)
        donut_chart[industry.name] = copy.deepcopy(donut)

    # doughnut chart
    device_status = DeviceStatus.objects.filter(device__user=request.auth.user).\
        order_by('device', '-id').distinct('device')
    for device in device_status:
        donut_chart[device.device.industry_type.name][device_status_dict[device.status]] += 1

    donut_chart = {
        key: [
            {'status': name,
             'value': value[name],
             'color': status_color[name]
             } for status_id, name in DEVICE_STATUS
        ] for key, value in donut_chart.items()}

    # line graph get statuses since 8 hours ago
    line_graph = {industry.name: [] for industry in device_industries}
    priority_devices = devices.filter(device_settings__priority=True)
    for device in priority_devices:

        data = get_eight_hours_statuses(device, current_time)
        data.append({
            'timestamp': current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': data[-1]['status']
        })

        data_device = {
            'name': device.name,
            'data': data
        }

        line_graph[device.industry_type.name].append(data_device)

    return Response({
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'message': "Successfully data fetched.",
        'data': {
            'donut_chart': donut_chart,
            'line_graph': line_graph,
            'device_location': DeviceLocationSerializer(devices, many=True).data,
            'industry_type': industry_type,
            'donut_data_format': [
                {'status': name, 'value': 0, 'color': status_color[name]} for i, name in DEVICE_STATUS
            ]
        }
    }, status=status.HTTP_200_OK)
