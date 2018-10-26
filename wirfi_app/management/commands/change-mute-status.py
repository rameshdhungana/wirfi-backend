import pytz
import json
from django.core.management import BaseCommand
from wirfi_app.models import DeviceSetting
from datetime import timedelta, datetime
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, ' CACHE_TTL', DEFAULT_TIMEOUT)

utc = pytz.UTC


class Command(BaseCommand):
    help = 'this changes the mute status to false (unmute) after mute period ends'

    def handle(self, *args, **kwargs):
        print(CACHE_TTL, DEFAULT_TIMEOUT)
        if 'muted_device_list' in cache:
            device_list = cache.get('muted_device_list')
            print(device_list, 'this is from cache')
            cache.delete('muted_device_list')
            device_list = json.loads(device_list)
            for key, device in enumerate(device_list):
                print(key, device['is_muted'])

                mute_end_time = datetime.strptime(device['mute_start'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(
                    minutes=device['mute_duration'])
                if datetime.now().replace(tzinfo=utc) > mute_end_time.replace(tzinfo=utc):
                    device['is_muted'] = False
                print(device['is_muted'], mute_end_time, datetime.now().replace(tzinfo=utc),
                      datetime.now().replace(tzinfo=utc) > mute_end_time.replace(tzinfo=utc))

        else:
            device_list = DeviceSetting.objects.filter(is_muted=True)
            print(device_list)
            data = []
            for device in device_list.iterator():
                data.append({
                    'id': device.id,
                    'is_muted': device.is_muted,
                    'mute_start': device.mute_start.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'mute_duration': device.mute_duration
                })
            data = json.dumps(data)
            cache.set('muted_device_list', data, timeout=DEFAULT_TIMEOUT)
