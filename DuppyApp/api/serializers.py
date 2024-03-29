"""
API Serializers
"""
from rest_framework import serializers

from .models import Controller, Data, Node, Sensor


class ControllerSerializer(serializers.Serializer):
    uri = serializers.CharField(read_only=True)
    controller_id = serializers.CharField()
    name = serializers.CharField()
    location = serializers.CharField()
    nodes = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return Controller(**validated_data)


class DataSerializer(serializers.Serializer):
    controller_id = serializers.CharField()
    node_id = serializers.IntegerField()
    sensor_id = serializers.IntegerField()
    payload = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Data(**validated_data)


class NodeSerializer(serializers.Serializer):
    controller_id = serializers.CharField(read_only=True)
    node_id = serializers.IntegerField()
    name = serializers.CharField(required=False)

    def create(self, validated_data):
        return Node(**validated_data)


class SensorSerializer(serializers.Serializer):
    controller_id = serializers.CharField(read_only=True)
    node_id = serializers.IntegerField(read_only=True)
    sensor_id = serializers.IntegerField()
    sensor_type = serializers.CharField()
    name = serializers.CharField(required=False)
    latest_data = serializers.CharField(read_only=True)
    last_update = serializers.DateTimeField(read_only=True)
    #interval = serializers.IntegerField()

    def create(self, validated_data):
        return Sensor(**validated_data)


