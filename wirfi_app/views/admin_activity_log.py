from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.activity_log_paginator import ActivityLogPagination
from wirfi_app.models import AdminActivityLog
from wirfi_app.serializers import AdminActivityLogSerializer


class AdminActivityLogListView(generics.ListAPIView):
    serializer_class = AdminActivityLogSerializer
    pagination_class = ActivityLogPagination
    queryset = AdminActivityLog.objects.all().order_by('-id')

    def list(self, request, *args, **kwargs):
        return Response(

        )
