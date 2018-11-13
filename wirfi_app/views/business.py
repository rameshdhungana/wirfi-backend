from django.conf import settings

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Business
from wirfi_app.serializers import BusinessSerializer
from wirfi_app.views.login_logout import get_token_obj


class BusinessView(generics.ListCreateAPIView):
    serializer_class = BusinessSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Business.objects.filter(user=token.user)

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
        token = get_token_obj(request.auth)
        serializer = BusinessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        headers = self.get_success_headers(serializer.data)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully created.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class BusinessDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    lookup_field = 'id'
    serializer_class = BusinessSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Business.objects.filter(user=token.user).filter(pk=self.kwargs.get('id', ''))

    def update(self, request, *args, **kwargs):
        token = get_token_obj(request.auth)
        business = self.get_object()
        serializer = BusinessSerializer(business, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Business Info successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)