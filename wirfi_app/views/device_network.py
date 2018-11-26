from django.conf import settings
from django.db.models import signals

from rest_framework import generics, status
from rest_framework.response import Response

from wirfi_app.models import Device, DeviceNetwork
from wirfi_app.serializers import DeviceNetworkSerializer, DeviceNetworkUpdateSerializer


class DeviceNetworkView(generics.ListCreateAPIView):
    serializer_class = DeviceNetworkSerializer

    def get_queryset(self):
        self.device = Device.objects.get(pk=self.kwargs['device_id'])
        return DeviceNetwork.objects.filter(device=self.device)

    def list(self, request, *args, **kwargs):
        network = self.get_queryset()
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': DeviceNetworkSerializer(network, many=True).data
        }
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        device_network = self.get_queryset()
        if len(device_network) >= 2:
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Multiple secondary networks can't be set."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        if (len(device_network.filter(primary_network=True)) == 0 and not data[
            'primary_network']):
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Secondary network can't be set first."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if (len(device_network.filter(primary_network=True)) == 1 and data['primary_network']):
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Multiple primary network can't be set."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer = DeviceNetworkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(device=self.device)

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class DeviceNetworkDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = DeviceNetworkUpdateSerializer

    def get_queryset(self):
        return DeviceNetwork.objects.filter(pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        network = self.get_object()
        serializer = DeviceNetworkSerializer(network)
        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Detail successfully fetched.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        network = self.get_object()
        device = Device.objects.get(pk=self.kwargs['device_id'])
        print(request.data, 'this is data')
        serializer = DeviceNetworkUpdateSerializer(network, data=request.data)
        serializer.is_valid(raise_exception=True)
        if network.password != request.data['old_password']:
            data = {
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Old password is not correct."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(device=device)

        data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Device successfully updated.",
            'data': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.primary_network:
            return Response({
                'code': getattr(settings, 'ERROR_CODE', 0),
                'message': "Primary network can't be deleted."
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response({
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Secondary network successfully deleted."
        }, status=status.HTTP_200_OK)
