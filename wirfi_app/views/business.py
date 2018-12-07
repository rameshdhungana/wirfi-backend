from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Business
from wirfi_app.serializers import BusinessSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log


class BusinessView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer

    def get_queryset(self):
        return Business.objects.filter(user=self.request.auth.user)

    def list(self, request, *args, **kwargs):
        businesses = self.get_queryset()
        if not businesses:
            data = {
                'code': getattr(settings, 'NO_DATA_CODE', 2),
                'message': "No any associated business info. Please add them."
            }
            return Response(data, status=status.HTTP_200_OK)

        serializer = BusinessSerializer(businesses[0])
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Details successfully fetched.",
            'data': {
                'business_info': serializer.data
            }
        }
        return Response(data, status=status.HTTP_200_OK, headers=headers)

    def create(self, request, *args, **kwargs):
        user = request.auth.user
        serializer = BusinessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        create_activity_log(request, "Business information of user '{}' added.".format(user.email))
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class BusinessDetailView(generics.UpdateAPIView):
    lookup_field = 'id'
    serializer_class = BusinessSerializer

    def get_queryset(self):
        return Business.objects.filter(user=self.request.auth.user).filter(pk=self.kwargs.get('id', ''))

    def update(self, request, *args, **kwargs):
        user = request.auth.user
        business = self.get_object()
        serializer = BusinessSerializer(business, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        create_activity_log(request, "Business information of user '{}' updated.".format(user.email))
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
