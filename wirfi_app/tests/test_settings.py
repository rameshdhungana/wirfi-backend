from unittest import TestCase
from django.conf import settings


class SettingsTestCase(TestCase):
    # to prevent from accidently changing the server timezone,its value should be UTC
    def test_server_timezone_unchanged(self):
        target_timezone = 'UTC'
        self.assertEqual(target_timezone, settings.TIME_ZONE)
