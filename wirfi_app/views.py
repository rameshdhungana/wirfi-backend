from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets

from wirfi_app.serializers import UserSerializer, BusinessInfoSerializer, UserProfileSerializer, BillingInfoSerializer
from wirfi_app.models import Billing, Business, Profile

# Create your views here.

User = get_user_model()


class UserApiView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BillingApiView(viewsets.ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingInfoSerializer


class BusinessApiView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessInfoSerializer


class ProfileApiView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer
