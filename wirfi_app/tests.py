from django.test import TestCase
from wirfi_web.middleware import AuthKeyRequiredMiddleware

# Create your tests here.
class MiddlewareTestCase(TestCase):
    def test_check_path_true(self):
        self.assertTrue(AuthKeyRequiredMiddleware.is_exempt_url('login/'))
        self.assertTrue(AuthKeyRequiredMiddleware.is_exempt_url('reset-password-mobile/'))
        self.assertTrue(AuthKeyRequiredMiddleware.is_exempt_url('validate-reset-password/AB/12-aewr/'))
        self.assertTrue(AuthKeyRequiredMiddleware.is_exempt_url('reset/AS/vrt1234hrtr/'))

    def test_check_path_false(self):
        self.assertFalse(AuthKeyRequiredMiddleware.is_exempt_url(''))
        self.assertFalse(AuthKeyRequiredMiddleware.is_exempt_url('logout'))
        self.assertFalse(AuthKeyRequiredMiddleware.is_exempt_url('device'))
        self.assertFalse(AuthKeyRequiredMiddleware.is_exempt_url('notifications'))
        