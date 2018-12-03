from django.conf import settings

from rest_framework import generics

from wirfi_app.activity_log_paginator import ActivityLogPagination
from wirfi_app.models import AdminActivityLog
from wirfi_app.serializers import AdminActivityLogSerializer


class AdminActivityLogListView(generics.ListAPIView):
    serializer_class = AdminActivityLogSerializer
    pagination_class = ActivityLogPagination
    queryset = AdminActivityLog.objects.all().order_by('-id')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Successfully fetched activity log.',
            'data': response.data
        }
        return response
