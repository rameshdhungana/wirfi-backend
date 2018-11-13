from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from wirfi_app.models import Industry, Franchise


class IndustryTypeSerializer(serializers.ModelSerializer):
    is_user_created = serializers.SerializerMethodField()

    class Meta:
        model = Industry
        fields = ('id', 'name', 'is_user_created')

    def get_is_user_created(self, obj):
        return True if obj.user else False


class LocationTypeSerializer(serializers.ModelSerializer):
    is_user_created = serializers.SerializerMethodField()

    class Meta:
        model = Franchise
        fields = ('id', 'name', 'user', 'is_user_created')
        validators = [
            UniqueTogetherValidator(
                queryset=Franchise.objects.all(),
                fields=('name', 'user'),
                message="Franchise name already exists."
            )
        ]

    def get_is_user_created(self, obj):
        return True if obj.user else False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {
            'id': data['id'],
            'name': data['name'],
            'is_user_created': data['is_user_created']
        }