import copy

from django.conf import settings
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceStatus, Industry, Franchise, DEVICE_STATUS
from wirfi_app.views.login_logout import get_token_obj


@api_view(['GET'])
def dashboard_view(request):
    '''
    API to get User's dashboard information.
    '''
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
