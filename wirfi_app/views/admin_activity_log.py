from django.conf import settings

from rest_framework import generics, status, filters
from rest_framework.response import Response

from wirfi_app.models import AdminActivityLog
from wirfi_app.serializers import AdminActivityLogSerializer


class AdminActivityLogListView(generics.ListAPIView):
    serializer_class = AdminActivityLogSerializer
    queryset = AdminActivityLog.objects.all().order_by('-id')
    search_fields = ('admin__email', 'timestamp', 'activity')
    filter_backends = (filters.SearchFilter,)

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': 'You do not have permission.',
            }, status=status.HTTP_403_FORBIDDEN)

        response = super().list(request, *args, **kwargs)
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Successfully fetched activity log.',
            'data': response.data
        }
        return response
