from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import PresetFilter
from wirfi_app.serializers import PresetFilterSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log


class PresetFilterView(generics.ListCreateAPIView):
    serializer_class = PresetFilterSerializer

    def get_queryset(self):
        return PresetFilter.objects.filter(user=self.request.auth.user)

    def list(self, request, *args, **kwargs):
        presets = self.get_queryset()
        serializer = PresetFilterSerializer(presets, many=True)
        return Response({
            "code": getattr(settings, "SUCCESS_CODE", 1),
            "message": "Successfully fetched preset filter data.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.auth.user
        serializer = PresetFilterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(user=user)
            create_activity_log(request,
                                "Preset '{preset}' added to user '{email}'.".format(preset=serializer.data['name'],
                                                                                    email=user.email))
            return Response({
                "code": getattr(settings, "SUCCESS_CODE", 1),
                "message": "Successfully fetched preset filter data.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "code": getattr(settings, "ERROR_CODE", 0),
                "message": "This preset name already exists",
            }, status=status.HTTP_400_BAD_REQUEST)


class PresetFilterDeleteView(generics.RetrieveAPIView, generics.DestroyAPIView):
    serializer_class = PresetFilterSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return PresetFilter.objects.filter(user=self.request.auth.user).filter(pk=self.kwargs['id'])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.auth.user
        create_activity_log(request, "Preset '{preset}' of user '{email}' deleted.".format(preset=instance.name,
                                                                                           email=user.email))
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted preset filter."
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Preset Detail is fetched successfully.",
            "data": PresetFilterSerializer(instance).data
        }, status=status.HTTP_200_OK)
