import pytz
import json
import time
from django.core.management import BaseCommand
from wirfi_app.models import DeviceSetting, DevicePingStatus, DeviceStatus
from datetime import timedelta, datetime
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from wirfi_app.views import add_or_get_cached_device_list

CACHE_TTL = getattr(settings, ' CACHE_TTL', DEFAULT_TIMEOUT)

utc = pytz.UTC

DEVICE_ONLINE_TIME_LIMIT_IN_SECONDS = float(getattr(settings, ' CACHE_TTL', 60))
DEVICE_OFFLINE_TIME_LIMIT_IN_SECONDS = float(getattr(settings, ' CACHE_TTL', 5 * 60))

from wirfi_app.models import DEVICE_STATUS


class Command(BaseCommand):
    help = 'this changes the mute status to false (unmute) after mute period ends'

    @staticmethod
    def check_and_change_device_status():
        device_ping_status_queryset = DevicePingStatus.objects.all()
        for key, device_ping_status_obj in enumerate(device_ping_status_queryset):
            current_device_status = DeviceStatus.objects.filter(device=device_ping_status_obj.device)[:1].first().status
            time_interval = (datetime.now().replace(tzinfo=utc) - device_ping_status_obj.pinged_at.replace(
                tzinfo=utc)).total_seconds()
            if time_interval <= DEVICE_ONLINE_TIME_LIMIT_IN_SECONDS:
                if current_device_status != DEVICE_STATUS[0][0]:
                    DeviceStatus.objects.create(device=device_ping_status_obj.device, status=DEVICE_STATUS[0][0])

            elif DEVICE_ONLINE_TIME_LIMIT_IN_SECONDS < time_interval < DEVICE_OFFLINE_TIME_LIMIT_IN_SECONDS:

                if current_device_status != DEVICE_STATUS[3][0]:
                    DeviceStatus.objects.create(device=device_ping_status_obj.device, status=DEVICE_STATUS[3][0])
            else:

                if current_device_status != DEVICE_STATUS[2][0]:
                    DeviceStatus.objects.create(device=device_ping_status_obj.device, status=DEVICE_STATUS[4][0])

    def handle(self, *args, **kwargs):
        t = time.time()
        device_list = add_or_get_cached_device_list()
        for key, device in enumerate(device_list):
            print(device['id'], device['is_muted'])
            mute_end_time = datetime.strptime(device['mute_start'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(
                minutes=device['mute_duration'])
            sleep_end_time = datetime.strptime(device['sleep_start'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(
                minutes=device['sleep_duration'])
            device_setting = DeviceSetting.objects.get(id=device['id'])

            if datetime.now().replace(tzinfo=utc) > mute_end_time.replace(tzinfo=utc) and device['is_muted']:
                device['is_muted'] = False
                try:
                    device_setting.is_muted = False
                    device_setting.mute_duration = 0
                except:
                    pass
            if datetime.now().replace(tzinfo=utc) > sleep_end_time.replace(tzinfo=utc) and device['is_asleep']:
                device['is_asleep'] = False
                try:
                    device_setting.is_asleep = False
                    device_setting.sleep_duration = 0
                except:
                    pass
            device_setting.save()

            print('muted:', device['is_muted'], 'end_date:', mute_end_time.replace(tzinfo=utc), 'now:',
                  datetime.now().replace(tzinfo=utc),
                  'invalid mute:', datetime.now().replace(tzinfo=utc) > sleep_end_time.replace(tzinfo=utc))
            print('slept:', device['is_asleep'], 'end_date:', sleep_end_time.replace(tzinfo=utc), 'now:',
                  datetime.now().replace(tzinfo=utc),
                  'invalid sleep:', datetime.now().replace(tzinfo=utc) > mute_end_time.replace(tzinfo=utc))
        cache.delete('cached_device_list')
        cache.set('cached_device_list', json.dumps(device_list), timeout=CACHE_TTL)
        print(time.time() - t)

        # we now call check_and_change_device_status function to check and change the device status
        # for each device
        self.check_and_change_device_status()
