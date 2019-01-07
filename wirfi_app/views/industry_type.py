from django.conf import settings
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Industry
from wirfi_app.views.create_admin_activity_log import create_activity_log
from wirfi_app.serializers import IndustryTypeSerializer


def industry_type_name_already_exits(name, user):
    for key, value in enumerate(
            Industry.objects.filter(Q(user__isnull=True) | Q(user=user)).values_list('name', flat=True)):
        if name.upper() == value.upper():
            return True
        return False


class IndustryTypeListView(generics.ListCreateAPIView):
    '''
    API to list and add logged in User's industry types.
    '''
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=self.request.auth.user)).order_by('id')

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
        user = request.auth.user

        # case sensitive validation of name
        if industry_type_name_already_exits(request.data['name'], user):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndustryTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        create_activity_log(
            request,
            "Industry Type '{name}' added to user '{email}'.".format(name=serializer.data['name'],
                                                                     email=user.email)
        )

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully added industry type.",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class IndustryTypeDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    '''
    API to update and delete logged in user added industry types
    '''
    lookup_field = 'id'
    serializer_class = IndustryTypeSerializer

    def get_queryset(self):
        return Industry.objects.filter(Q(user__isnull=True) | Q(user=self.request.auth.user)).filter(pk=self.kwargs['id'])

    def update(self, request, *args, **kwargs):
        industry_type = self.get_object()
        user = request.auth.user

        # case sensitive validation of name
        if industry_type_name_already_exits(request.data['name'], user):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Industry type with this name already exists.",

            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndustryTypeSerializer(industry_type, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(user=user)

        create_activity_log(
            request,
            "Industry Type '{name}' of user '{email}' updated.".format(name=serializer.data['name'],
                                                                       email=user.email)
        )

        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully updated industry type.",
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.auth.user
        create_activity_log(
            request,
            "Industry Type '{name}' of user '{email}' deleted.".format(name=instance.name,
                                                                       email=user.email)
        )
        self.perform_destroy(instance)
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully deleted industry type."
        }, status=status.HTTP_200_OK)
