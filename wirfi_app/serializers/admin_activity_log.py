from rest_framework import serializers

from wirfi_app.models import AdminActivityLog


class AdminActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminActivityLog
        fields = '__all__'
        read_only_fields = ['timestamp', ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['admin'] = instance.admin.email
        return response
