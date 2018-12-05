from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from wirfi_app.models import AuthorizationToken

User = get_user_model()


@api_view(['GET'])
def impersonate_user(request, user_id):
    if not request.user.is_superuser:
        return Response({
            'code': getattr(settings, 'ERROR_CODE', 0),
            'message': 'You do not have permission.'
        }, status=status.HTTP_403_FORBIDDEN)

    if not User.objects.filter(id=int(user_id)).exists():
        return Response({
            'code': getattr(settings, 'ERROR_CODE', 0),
            'message': 'User doesn\'t exists.'
        }, status=status.HTTP_400_BAD_REQUEST)

    super_admin_token = request.auth.key
    user_auth, _ = AuthorizationToken.objects.get_or_create(user_id=user_id, device_type=0)
    user_token = user_auth.key

    return Response({
        'code': getattr(settings, 'SUCCESS_CODE', 1),
        'message': 'User successfully impersonated.',
        'data': {
            'impersonator': super_admin_token,
            'user_token': user_token
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def stop_impersonate(request):
    pass


