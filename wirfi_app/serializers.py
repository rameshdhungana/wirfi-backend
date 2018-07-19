from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

from wirfi_app.models import UserProfile, BillingInfo, BusinessInfo


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'phone_number')


class BillingInfoSerializser(ModelSerializer):
    class Meta:
        model = BillingInfo
        fields = ('user', 'name', 'address', 'email', 'phone_number')


class BusinessInfoSerializser(ModelSerializer):
    class Meta:
        model = BusinessInfo
        fields = ('user', 'name', 'address', 'security_code', 'expiration_code')


class UserSerializer(ModelSerializer):
    profile = UserProfileSerializer(many=True)
    billing = BillingInfoSerializser(many=True)
    business = BillingInfoSerializser(many=True)

    class Meta:
        model: get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name',)
