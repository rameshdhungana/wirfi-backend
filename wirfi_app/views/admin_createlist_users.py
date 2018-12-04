from django.conf import settings
from django.contrib.auth import get_user_model

from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.activity_log_paginator import ActivityLogPagination
from wirfi_app.serializers import AdminUserSerializer

User = get_user_model()


class AdminListCreateUserView(generics.ListCreateAPIView):
    serializer_class = AdminUserSerializer
    pagination_class = ActivityLogPagination

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.id)

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': 'You do not have permission.',
            }, status=status.HTTP_403_FORBIDDEN)

        response = super().list(request, *args, **kwargs)
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Successfully fetched users list data.',
            'data': response.data
        }
        return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': 'You do not have permission.',
            }, status=status.HTTP_403_FORBIDDEN)

        response = super().create(request, *args, **kwargs)
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': 'Successfully created users list data.',
            'data': response.data
        }
        return response
