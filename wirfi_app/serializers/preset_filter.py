from rest_framework import serializers

from wirfi_app.models import PresetFilter


class PresetFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresetFilter
        exclude = ('user',)