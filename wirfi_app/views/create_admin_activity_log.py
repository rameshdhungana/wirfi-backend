from wirfi_app.models import AdminActivityLog
from wirfi_app.views.login_logout import get_token_obj


def create_activity_log(request, message):
    if request.META.get('HTTP_PERSONATOR', '') and request.META.get('HTTP_PERSONATOR', '') != 'null':
        impersonator = get_token_obj(request.META.get('HTTP_PERSONATOR')).user
        AdminActivityLog.objects.create(
            admin=impersonator,
            activity=message
        )
