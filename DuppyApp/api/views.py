"""
API Views
"""
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.authentication import TokenAuthentication, \
                                          SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

import datetime
import json

from base import models
from .models import Controller, Data, Node, Sensor
from .serializers import ControllerSerializer, DataSerializer, \
                         NodeSerializer, SensorSerializer

class ControllerView(APIView):
    """
    API Controller View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ControllerView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id):
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        response = Controller(
                uri=reverse('api-controller-view',
                            args=[controller.controller_id],
                            request=request),
                controller_id=controller.controller_id,
                name=controller.name,
                location=controller.location,
                nodes=reverse('api-node-set-view',
                              args=[controller.controller_id],
                              request=request))

        serializer = ControllerSerializer(response)
        return Response(serializer.data)


class ControllerSetView(APIView):
    """
    API Controller Set View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ControllerSetView, self).dispatch(*args, **kwargs)

    def get(self, request):
        controllers = models.Controller.objects.filter(user=request.user)

        response = [Controller(
                        uri=reverse('api-controller-view',
                                    args=[controller.controller_id],
                                    request=request),
                        controller_id=controller.controller_id,
                        name=controller.name,
                        location=controller.location,
                        nodes=reverse('api-controller-view',
                                      args=[controller.controller_id],
                                      request=request))
                    for controller in controllers]

        serializer = ControllerSerializer(response, many=True)
        return Response(serializer.data)


class DataView(APIView):
    """
    API Data Set View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(DataView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = []
        for data in models.Data.objects.all():
            response.append(Data(
                    controller_id=data.sensor.node.controller.controller_id,
                    node_id=data.sensor.node.node_id,
                    sensor_id=data.sensor.sensor_id,
                    payload=data.payload,
                    created=data.created))
        serializer = DataSerializer(response, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = DataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.data

        # find the controller
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=obj.get("controller_id"))

        # find the node
        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=obj.get("node_id"))

        # find the sensor
        sensor = get_object_or_404(models.Sensor,
                node=node,
                sensor_id=obj.get("sensor_id"))

        data = models.Data(
                controller=controller,
                sensor=sensor,
                payload=obj.get("payload"))
        data.save()

        return Response(status=status.HTTP_201_CREATED)

class NodeView(APIView):
    """
    API Node View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(NodeView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id, node_id):
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=node_id)

        response = Node(
                controller_id=controller.controller_id,
                node_id=node.node_id,
                name=node.name)

        serializer = NodeSerializer(response)
        return Response(serializer.data)


class NodeSetView(APIView):
    """
    API Node Set View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(NodeSetView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id):
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        nodes = models.Node.objects.filter(controller=controller)

        response = [Node(
                        controller_id=controller.controller_id,
                        node_id=node.node_id,
                        name=node.name)
                    for node in nodes]

        serializer = NodeSerializer(response, many=True)
        return Response(serializer.data)

    def post(self, request, controller_id):
        serializer = NodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.data

        # find the controller
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        # try to find the node
        node_id = obj.get("node_id")
        try:
            node = models.Node.objects.get(
                    controller=controller,
                    node_id=node_id)
            return Response(status=status.HTTP_409_CONFLICT)
        except models.Node.DoesNotExist:
            pass

        node_name = obj.get("name")
        if not node_name:
            node_name = "New Node #%s" % \
                (models.Node.objects.filter(controller=controller).count() + 1)

        node = models.Node(
                controller=controller,
                node_id=node_id,
                name=node_name)
        node.save()

        headers = {"Location": reverse("api-node-view",
                                       args=[controller.controller_id,
                                             node.node_id])}
        return Response(status=status.HTTP_201_CREATED, headers=headers)


class SensorView(APIView):
    """
    API Sensor View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SensorView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id, node_id, sensor_id):
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=node_id)

        sensor = get_object_or_404(models.Sensor,
                node=node,
                sensor_id=sensor_id)

        data = sensor.data_set.latest("created")
        latest_data = data.payload if data else None
        last_update = data.created if data else None

        response = Sensor(
                controller_id=controller.controller_id,
                node_id=node.node_id,
                sensor_id=sensor.sensor_id,
                sensor_type=sensor.sensor_type,
                name=sensor.name,
                latest_data=latest_data,
                last_update=last_update)

        serializer = SensorSerializer(response)
        return Response(serializer.data)


class SensorSetView(APIView):
    """
    API Sensor Set View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SensorSetView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id, node_id):
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=node_id)

        sensors = models.Sensor.objects.filter(node=node)

        response = [Sensor(
                        controller_id=controller.controller_id,
                        node_id=node.node_id,
                        sensor_id=sensor.sensor_id,
                        sensor_type=sensor.sensor_type,
                        name=sensor.name,
                        latest_data=sensor.data_set.latest("created").payload,
                        last_update=sensor.data_set.latest("created").created)
                    for sensor in sensors]

        serializer = SensorSerializer(response, many=True)
        return Response(serializer.data)

    def post(self, request, controller_id, node_id):
        serializer = SensorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = serializer.data

        # find the controller
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        # find the node
        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=node_id)

        # try to find the sensor
        sensor_id = obj.get("sensor_id")
        try:
            sensor = models.Sensor.objects.get(
                    node=node,
                    sensor_id=sensor_id)
            return Response(status=status.HTTP_409_CONFLICT)
        except models.Sensor.DoesNotExist:
            pass

        sensor_name = obj.get("sensor_name")
        sensor_type = obj.get("sensor_type")
        if not sensor_name:
            sensor_name = "New Node %s: %s sensor #%s" % \
                (node, sensor_type,
                 (models.Sensor.objects.filter(
                        node=node,
                        sensor_type=sensor_type).count() + 1))

        sensor = models.Sensor(
            node=node,
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            name=sensor_name)
        sensor.save()

        headers = {"Location": reverse("api-sensor-view",
                                       args=[controller.controller_id,
                                             node.node_id,
                                             sensor.sensor_id])}
        return Response(status=status.HTTP_201_CREATED, headers=headers)

class SensorTypeView(APIView):
    """
    API Sensor Type View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SensorTypeView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id):
        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        sensorTypes = models.Sensor.objects \
            .filter(node__controller=controller) \
            .values("sensor_type").distinct()

        data = json.dumps(list(sensorTypes))

        return Response(data)

class SensorSetTypeView(APIView):
    """
    API Sensor Set Type View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SensorSetTypeView, self).dispatch(*args, **kwargs)

    def get(self, request, sensor_type):

        sensors = models.Sensor.objects.filter(sensor_type=sensor_type)

        response = [Sensor(
                        controller_id=sensor.node.controller.controller_id,
                        node_id=sensor.node.node_id,
                        sensor_id=sensor.sensor_id,
                        sensor_type=sensor.sensor_type,
                        name=sensor.name)
                    for sensor in sensors]

        serializer = SensorSerializer(response, many=True)
        return Response(serializer.data)

class SensorDataView(APIView):
    """
    API Sensor Data View
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SensorDataView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id, node_id, sensor_id):
        response = []

        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=node_id)

        sensor = get_object_or_404(models.Sensor,
                node=node,
                sensor_id=sensor_id)

        #Eventually we will use the following call for range
        #end = sensor.data_set.latest().created
        #begin  = end - timedelta(minutes=monitor.notice_range)
        #data = sensor.data_set.filter(created__range=[begin,end])  
        for data in sensor.data_set.all():
            response.append(Data(
                    controller_id=data.sensor.node.controller.controller_id,
                    node_id=data.sensor.node.node_id,
                    sensor_id=data.sensor.sensor_id,
                    payload=data.payload,
                    created=data.created))

        serializer = DataSerializer(response, many=True)
        return Response(serializer.data)

class SensorDataDateView(APIView):
    """
    API Sensor Data View With Date Range
    """

    authentication_classes = (TokenAuthentication, SessionAuthentication)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SensorDataDateView, self).dispatch(*args, **kwargs)

    def get(self, request, controller_id, node_id, sensor_id, beginSec, endSec):
        response = []

        controller = get_object_or_404(models.Controller,
                user=request.user,
                controller_id=controller_id)

        node = get_object_or_404(models.Node,
                controller=controller,
                node_id=node_id)

        sensor = get_object_or_404(models.Sensor,
                node=node,
                sensor_id=sensor_id)

        begin = datetime.datetime.fromtimestamp(int(beginSec))
        end = datetime.datetime.fromtimestamp(int(endSec)) + datetime.timedelta(days=1)
        data_set = sensor.data_set.filter(created__range=[begin,end])
 
        for data in data_set:
            response.append(Data(
                    controller_id=data.sensor.node.controller.controller_id,
                    node_id=data.sensor.node.node_id,
                    sensor_id=data.sensor.sensor_id,
                    payload=data.payload,
                    created=data.created))

        serializer = DataSerializer(response, many=True)
        return Response(serializer.data)

