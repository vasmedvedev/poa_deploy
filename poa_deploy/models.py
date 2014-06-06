from django.db import models
from django import forms

# Create your models here.

class Method(models.Model):
    method_name = models.CharField(max_length=200)
    request_xml_string = models.CharField(max_length=2000)

class Installation(models.Model):
    installation_name = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=200)
    status = models.BooleanField()
    login = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=200, blank=True)
    
class Application(models.Model):
    app_name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    aps_version = models.CharField(max_length=3)
    package_version = models.CharField(max_length=10)

class Instance(models.Model):
    st_id = models.IntegerField()
    rt_id = models.IntegerField()
    sub_id = models.IntegerField()
    instance_id = models.IntegerField()
    poa_app_id = models.IntegerField()
    domain_name = models.CharField(max_length=200)

    

    
