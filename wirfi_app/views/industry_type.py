from django.conf import settings
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Industry
from wirfi_app.views.login_logout import get_token_obj
from wirfi_app.serializers import IndustryTypeSerializer


def industry_type_name_already_exits(name, token):
    for key, value in enumerate(
            Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user)).values_list('name', flat=True)):
        if name.upper() == value.upper():
            return True
        return False


class IndustryTypeListView(generics.ListCreateAPIView):
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user))

    def list(self, request, *args, **kwargs):
        industry_types = self.get_queryset()
        serializer = IndustryTypeSerializer(industry_types, many=True)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully fetched industry types.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if industry_type_name_already_exits(request.data['name'], token):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndustryTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully added industry type.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class IndustryTypeDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    lookup_field = 'id'
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=token.user)).filter(pk=self.kwargs['id'])

    def update(self, request, *args, **kwargs):
        industry_type = self.get_object()
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if industry_type_name_already_exits(request.data['name'], token):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndustryTypeSerializer(industry_type, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully updated industry type.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted industry type."
        }, status=status.HTTP_200_OK)