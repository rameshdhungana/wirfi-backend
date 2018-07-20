from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets

from wirfi_app.serializers import UserSerializer

# Create your views here.

User = get_user_model()


class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.filter()
    serializer_class = UserSerializer
