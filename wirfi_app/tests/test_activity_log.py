from django.urls import reverse
from django.test import TestCase
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from wirfi_app.models import AuthorizationToken, AdminActivityLog

User = settings.AUTH_USER_MODEL


class ActivityLogTest(APITestCase):
    def setup(self):
        self.user = User.objects.create(email='ssumedhiw@gmail.com')
        token = AuthorizationToken.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token' + token.key)