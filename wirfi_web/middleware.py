from django.conf import settings
from django.http import JsonResponse

from wirfi_app.models import AuthorizationToken


class AuthKeyRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.lstrip('/') != 'login/':
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
