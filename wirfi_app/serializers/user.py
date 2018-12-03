import stripe

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers

from wirfi_app.models import Billing, Profile 
from wirfi_app.serializers.user_detail import UserProfileSerializer, BusinessSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(max_length=15, write_only=True, allow_blank=True, required=False)
    address = serializers.CharField(max_length=100, write_only=True, required=False, allow_blank=True)
    profile = UserProfileSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)
    billing = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name', 'phone_number', 'address', 'profile', 'business',
            'billing', 'is_superuser', 'is_staff')
        read_only_fields = ('is_superuser', 'is_staff')

    def update(self, instance, validated_data):
        profile_data = {"phone_number": validated_data.pop('phone_number', ''),
                        "address": validated_data.pop('address', '')}
        user = super().update(instance, validated_data)
        profile = Profile.objects.filter(user=user)
        if profile:
            profile_validated_data = UserProfileSerializer().validate(profile_data)
            profile_obj = UserProfileSerializer().update(profile.first(), profile_validated_data)
        else:
            serializer = UserProfileSerializer(data=profile_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            profile_obj = Profile.objects.get(pk=serializer.data['id'])
        user.profile = profile_obj
        return user

    def get_billing(self, obj):
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                billing = Billing.objects.get(user=request.user)
                return stripe.Customer.retrieve(billing.customer_id)

        except:
            return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data['profile']:
            data['profile'] = {
                "address": '',
                "phone_number": '',
                "profile_picture": None
            }
        data['profile']['first_name'] = data.pop('first_name')
        data['profile']['last_name'] = data.pop('last_name')
        data['profile']['full_name'] = data.pop('full_name')
        if data['profile']['profile_picture']:
            data['profile']['profile_picture'] = 'media' + data['profile']['profile_picture'].split('/media')[1]
        return data


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ('pk', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)
