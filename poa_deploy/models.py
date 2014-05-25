from django.db import models
from django import forms

# Create your models here.

class Method(models.Model):
    method_name = models.CharField(max_length=200)
    request_xml_string = models.CharField(max_length=2000)

class Installation(models.Model):
    installation_name = models.CharField(max_length=200)
    api_access_point = models.CharField(max_length=200)
    login = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=200, blank=True)
    
class Application(models.Model):
    app_name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    aps_version = models.CharField(max_length=3)
    package_version = models.CharField(max_length=10)

    def get_url(self):
        return self.url

class Instance(models.Model):
    READY = 0
    PROVISIONING = 1
    UNPROVISIONING = 2
    UNKNOWN = 3
    STATUS_CHOICES = (
        (READY, 'Ready'),
        (PROVISIONING, 'Provisioning'),
        (UNPROVISIONING, 'Unprovisioning'),
        (UNKNOWN, 'Unknown')
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNKNOWN)
    application = models.ForeignKey(Application)
    poa_instance_id = models.IntegerField()
    
    def is_ready(self):
        return self.status == self.READY

    

    
