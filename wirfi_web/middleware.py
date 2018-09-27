from re import compile

from django.conf import settings
from django.http import JsonResponse

from wirfi_app.models import AuthorizationToken

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class AuthKeyRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        if not AuthKeyRequiredMiddleware.is_exempt_url(path):
            token = request.META.get('HTTP_AUTHORIZATION', 'token ')[6:]
            if not token:
                return JsonResponse({
                    "code": getattr(settings, 'NO_AUTH_KEY', 3),
                    "message": "Session Expired. Please Login."
                }, status=400)
            else:
                if not AuthorizationToken.objects.filter(key=token).exists():
                    return JsonResponse({
                        "code": getattr(settings, 'NO_AUTH_KEY', 3),
                        "message": "Session Expired. Please Login."
                    }, status=400)
        response = self.get_response(request)
        return response

    @classmethod
    def is_exempt_url(cls, path):
        if not any(url.match(path) for url in EXEMPT_URLS):
            return False
        return True
