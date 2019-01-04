from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.serializers import CheckVersionSerializer


class CheckVersion(generics.CreateAPIView):
    '''
    API to check mobile app's version.
    '''
    serializer_class = CheckVersionSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_type = serializer.validated_data['device_type']
        version = serializer.validated_data['app_version']
        if not self.check_version(device_type, version):
            if getattr(settings, 'OPTIONAL_UPDATE'):
                data = {
                    'code': getattr(settings, 'APP_UPDATE_OPTIONAL'),
                    'message': "A newer version of app is available in store. Please update your app for better experience"
                }
            else:
                data = {
                    'code': getattr(settings, 'APP_UPDATE_MANDATORY'),
                    'message': "A newer version of app is available in store. Please update your app."
                }

            data['app_link'] = getattr(settings, 'IOS_LINK') if device_type == '1' else getattr(settings,
                                                                                                'ANDROID_LINK')
            return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response({
            "code": getattr(settings, 'SUCCESS_CODE'),
            "message": "Your app is up to date."
        }, status=status.HTTP_200_OK)

    def check_version(self, device_type, version):
        if device_type == '1':
            if version == getattr(settings, 'IOS_VERSION'):
                return True

        elif device_type == '2':
            if version == getattr(settings, 'ANDROID_VERSION'):
                return True

        return False
