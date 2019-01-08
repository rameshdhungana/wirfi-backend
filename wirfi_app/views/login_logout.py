import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout as django_logout

from rest_auth.views import LoginView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import AuthorizationToken
from wirfi_app.serializers import LoginSerializer, AuthorizationTokenSerializer, UserSerializer


def get_token_obj(token):
    return AuthorizationToken.objects.get(key=token)


class Login(LoginView):
    """
        Check the credentials and return the REST Token
        if the credentials are valid and authenticated.k
        Calls Django Auth login method to register User ID
        in Django session framework

        Accept the following POST parameters: username, password
        Return the REST Framework Token Object's key.
    """

    serializer_class = LoginSerializer
    token_model = AuthorizationToken

    def create_token(self):
        push_notification = self.serializer.validated_data['push_notification_token']
        device_id = self.serializer.validated_data['device_id']
        device_type = self.serializer.validated_data['device_type']
        token, _ = self.token_model.objects.get_or_create(user=self.user,
                                                          push_notification_token=push_notification,
                                                          device_id=device_id,
                                                          device_type=device_type)
        return token

    def get_response_serializer(self):
        response_serializer = AuthorizationTokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.token = self.create_token()
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        first_login = False if self.serializer.validated_data['user'].last_login else True
        self.login()
        self.user.last_login = datetime.datetime.now()
        self.user.save()
        response = self.get_response()
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully Logged In.",
            'data': {
                'id': self.user.id,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'profile_picture': self.user.profile.profile_picture.url if (
                        hasattr(self.user, 'profile') and self.user.profile.profile_picture) else '',
                'auth_token': response.data.get('key'),
                'device_id': response.data.get('device_id'),
                'device_type': response.data.get('device_type'),
                'push_notification_token': response.data.get('push_notification_token'),
                'is_first_login': first_login,
                'is_superuser': self.user.is_superuser,
                'is_staff': self.user.is_staff
            }
        }
        return response


@api_view(['POST'])
def logout(request):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    try:
        AuthorizationToken.objects.filter(key=request.auth).delete()
    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)

    django_logout(request)
    return Response({"code": getattr(settings, 'SUCCESS_CODE', 1), "message": "Successfully logged out."},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
def get_logged_in_user(request):
    '''
    API to get logged in user's information
    :param request:
    :return:
    '''
    serializer = UserSerializer(request.user, context={'request': request})
    serializer_data = serializer.data
    data = {
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Successfully fetched.",
        "data": serializer_data
    }
    return Response(data, status=status.HTTP_200_OK)
