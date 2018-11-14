from django.conf import settings
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Franchise
from wirfi_app.views.login_logout import get_token_obj
from wirfi_app.serializers import LocationTypeSerializer


def franchise_type_name_already_exits(name, token):
    for key, value in enumerate(
            Franchise.objects.filter(Q(user__isnull=True) | Q(user=token.user)).values_list('name', flat=True)):
        if name.upper() == value.upper():
            return True
        return False


class LocationTypeListView(generics.ListCreateAPIView):
    serializer_class = LocationTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Franchise.objects.filter(user=token.user).order_by('id')

    def list(self, request, *args, **kwargs):
        location_types = self.get_queryset()
        serializer = LocationTypeSerializer(location_types, many=True)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully fetched location types.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if franchise_type_name_already_exits(request.data['name'], token):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Franchise type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        data['user'] = token.user.id
        serializer = LocationTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully added location type.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class LocationTypeDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    lookup_field = 'id'
    serializer_class = LocationTypeSerializer

    def get_queryset(self):
        token = get_token_obj(self.request.auth)
        return Franchise.objects.filter(user=token.user)

    def update(self, request, *args, **kwargs):
        franchise_type = self.get_object()
        token = get_token_obj(self.request.auth)

        # case sensitive validation of name
        if franchise_type_name_already_exits(request.data['name'], token):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Franchise type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        data = {**request.data, 'user': token.user.id}
        serializer = LocationTypeSerializer(franchise_type, data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=token.user)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully updated franchise type.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted franchise type."
        }, status=status.HTTP_200_OK)