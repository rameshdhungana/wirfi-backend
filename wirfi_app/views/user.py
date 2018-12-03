from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from wirfi_app.models import Profile
from wirfi_app.serializers import UserSerializer
from wirfi_app.views.login_logout import get_token_obj

User = get_user_model()


class UserDetailView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserSerializer(user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        token = get_token_obj(self.request.auth)
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=token.user)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "User successfully updated",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def profile_images_view(request, id):
    profile_picture = request.FILES.get('profile_picture', '')
    user = get_token_obj(request.auth).user
    if not profile_picture:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": "Please upload the image."},
            status=status.HTTP_400_BAD_REQUEST)

    profile = Profile.objects.filter(user__id=id)
    if profile:
        profile[0].profile_picture = profile_picture
        profile[0].save()
    else:
        profile = Profile.objects.create(user=user, phone_number='', address='', profile_picture=profile_picture)

    user = UserSerializer(user).data
    return Response({
        "code": getattr(settings, 'SUCCESS_CODE', 1),
        "message": "Images Successfully uploaded.",
        "data": user},
        status=status.HTTP_200_OK)
