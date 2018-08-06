from rest_framework.authentication import TokenAuthentication
from wirfi_app.models import AuthorizationToken


class MyOwnTokenAuthentication(TokenAuthentication):
    model = AuthorizationToken
