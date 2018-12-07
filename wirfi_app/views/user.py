from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Profile, AdminActivityLog
from wirfi_app.serializers import UserSerializer
from wirfi_app.views.create_admin_activity_log import create_activity_log

User = get_user_model()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': UserSerializer(user).data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = request.auth.user
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        create_activity_log(request, "User profile of '{}' updated.".format(user.email))

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "User successfully updated",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "You don't have permission."
            }, status=status.HTTP_403_FORBIDDEN)

        user = self.get_object()
        activity = "User `{email}` deleted".format(email=user.email)
        AdminActivityLog.objects.create(admin=request.user, activity=activity)
        user.delete()
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "User successfully deleted."
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def profile_images_view(request, id):
    profile_picture = request.FILES.get('profile_picture', '')
    user = request.auth.user
    if not profile_picture:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Please upload the image."},
            status=status.HTTP_400_BAD_REQUEST)

    profile = Profile.objects.filter(user=user)
    if profile:
        profile[0].profile_picture = profile_picture
        profile[0].save()
    else:
        Profile.objects.create(user=user, phone_number='', address='', profile_picture=profile_picture)

    return Response({
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Images Successfully uploaded.",
        "data": UserSerializer(user).data},
        status=status.HTTP_200_OK)
