import json
import time

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from wirfi_app.models import Device, DeviceSetting

CACHE_TTL = getattr(settings, ' CACHE_TTL', DEFAULT_TIMEOUT)


def add_or_get_cached_device_list():
    if 'cached_device_list' in cache:
        cached_data = cache.get('cached_device_list')

    else:
        device_list = DeviceSetting.objects.all()
        data = []
        for device in device_list.iterator():
            data.append({
                'id': device.id,
                'is_muted': device.is_muted,
                'mute_start': device.mute_start.strftime('%Y-%m-%d %H:%M:%S.%f'),
                'mute_duration': device.mute_duration,
                'is_asleep': device.is_asleep,
                'sleep_duration': device.sleep_duration,
                'sleep_start': device.sleep_start.strftime('%Y-%m-%d %H:%M:%S.%f')

            })
            print(111111111, device.sleep_start,
                  device.mute_start.strftime('%Y-%m-%d %H:%M:%S.%f'))
        data1 = json.dumps(data)
        cache.set('cached_device_list', data1, timeout=CACHE_TTL)
        cached_data = cache.get('cached_device_list')
    return json.loads(cached_data)


def update_cached_device_list(data):
    t = time.time()
    device_list = add_or_get_cached_device_list()
    device_already = [device for key, device in enumerate(device_list) if device['id'] == data['id']]
    if device_already:
        device_already[0].update(data)
    else:
        device_list.append({
            data
        })

    cache.delete('cached_device_list')
    cache.set('cached_device_list', json.dumps(device_list), timeout=CACHE_TTL)
    print('this is updated list', cache.get('cached_device_list'))
    print(time.time() - t)