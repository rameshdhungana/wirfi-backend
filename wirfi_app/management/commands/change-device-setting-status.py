import pytz
import json
import time
from django.core.management import BaseCommand
from wirfi_app.models import DeviceSetting
from datetime import timedelta, datetime
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from wirfi_app.views import add_or_get_cached_device_list

CACHE_TTL = getattr(settings, ' CACHE_TTL', DEFAULT_TIMEOUT)

utc = pytz.UTC


class Command(BaseCommand):
    help = 'this changes the mute status to false (unmute) after mute period ends'

    def handle(self, *args, **kwargs):
        t = time.time()
        device_list = add_or_get_cached_device_list()
        for key, device in enumerate(device_list):
            print(device['id'], device['is_muted'])
            mute_end_time = datetime.strptime(device['mute_start'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(
                minutes=device['mute_duration'])
            sleep_end_time = datetime.strptime(device['sleep_start'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(
                minutes=device['sleep_duration'])
            obj = DeviceSetting.objects.get(id=device['id'])

            if datetime.now().replace(tzinfo=utc) > mute_end_time.replace(tzinfo=utc) and device['is_muted']:
                device['is_muted'] = False
                try:
                    obj.is_muted = False
                    obj.mute_duration = 0
                except:
                    pass
            if datetime.now().replace(tzinfo=utc) > sleep_end_time.replace(tzinfo=utc) and device['is_asleep']:
                device['is_asleep'] = False
                try:
                    obj.is_asleep = False
                    obj.sleep_duration = 0
                except:
                    pass
            obj.save()

            print('muted:', device['is_muted'], 'end_date:', mute_end_time.replace(tzinfo=utc), 'now:',
                  datetime.now().replace(tzinfo=utc),
                  'invalid mute:', datetime.now().replace(tzinfo=utc) > sleep_end_time.replace(tzinfo=utc))
            print('slept:', device['is_asleep'], 'end_date:', sleep_end_time.replace(tzinfo=utc), 'now:',
                  datetime.now().replace(tzinfo=utc),
                  'invalid sleep:', datetime.now().replace(tzinfo=utc) > mute_end_time.replace(tzinfo=utc))
        cache.delete('cached_device_list')
        cache.set('cached_device_list', json.dumps(device_list), timeout=CACHE_TTL)
        print(time.time() - t)
