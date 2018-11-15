from django.core.management import BaseCommand
from django.conf import settings
import subprocess


class Command(BaseCommand):
    help = 'this is for device test WiRFi'
    DEVICE_CONNECTION_HOST_NAME = getattr(settings, 'DEVICE_CONNECTION_HOST_NAME')
    DEVICE_CONNECTION_PASSWORD = getattr(settings, 'DEVICE_CONNECTION_PASSWORD')
    BACKEND_PING_URL_FOR_DEVICE = getattr(settings, 'BACKEND_PING_URL_FOR_DEVICE')
    command = 'sshpass -p {} ssh root@{}'.format(DEVICE_CONNECTION_PASSWORD, DEVICE_CONNECTION_HOST_NAME)

    def handle(self, *args, **options):
        print(self.DEVICE_CONNECTION_HOST_NAME)
        ssh = subprocess.run(['sshpass', '-p', self.DEVICE_CONNECTION_PASSWORD, 'ssh',
                              'root@{}'.format(self.DEVICE_CONNECTION_HOST_NAME), 'cd', 'custom', '&&', 'python',
                              'add-ping-server-ip-address.py',
                              '{0}'.format(self.BACKEND_PING_URL_FOR_DEVICE)],
                             shell=False,
                             )

        print(ssh)
