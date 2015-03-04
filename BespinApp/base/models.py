import binascii
import os

from django.contrib.auth.models import User
from django.db import models

#class Datum(models.Model):
#    nodeid = models.IntegerField()
#    sensorid = models.IntegerField()
#    #sensorid = models.ForeignKey(Sensor)
#    message_type = models.IntegerField()
#    sub_type = models.IntegerField()
#    payload = models.TextField()
#    created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return "ID: %s - Data: %s;%s;%s;%s;%s - Created: %s" % \
#                (self.pk,
#                 self.nodeid,
#                 self.sensorid,
#                 self.message_type,
#                 self.sub_type,
#                 self.payload,
#                 self.created)
#
#    class Meta:
#        ordering = ('created',)
#        get_latest_by = "created"


class Controller(models.Model):
    user = models.ForeignKey(User)
    controller_id = models.CharField(max_length=40, verbose_name="ID")
    name = models.CharField(max_length=250)
    location = models.TextField()

    def __str__(self):
        return "%s (%s)" % (self.name, self.location)

    class Meta:
        unique_together = (("user", "name"))

    def save(self, *args, **kwargs):
        if not self.controller_id:
            self.controller_id = self.generate_id()
        return super(Controller, self).save(*args, **kwargs)

    def generate_id(self):
        return binascii.hexlify(os.urandom(20)).decode()

class Node(models.Model):
    controller = models.ForeignKey(Controller)
    name = models.CharField(max_length=250)
    node_id = models.IntegerField()

    def __str__(self):
        return "%s - [%s] %s" % (self.controller, self.node_id, self.name)

    class Meta:
        unique_together = (("controller", "node_id"))

class Sensor(models.Model):
    node = models.ForeignKey(Node)
    name = models.CharField(max_length=250)
    sensor_id = models.IntegerField()
    sensor_type = models.CharField(max_length=250)

    def __str__(self):
        return "%s - [%s] %s" % (self.node, self.sensor_id, self.name)

    class Meta:
        unique_together = (("node", "sensor_id"))

class Data(models.Model):
    sensor = models.ForeignKey(Sensor)
    payload = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "created"
        verbose_name_plural = "Data"
