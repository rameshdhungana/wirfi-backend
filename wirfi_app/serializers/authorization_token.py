from rest_framework import serializers

from wirfi_app.models import AuthorizationToken


class AuthorizationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizationToken
        exclude = ('user',)