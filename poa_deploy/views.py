from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from poa_deploy.models import Method, Application, Installation
from poa_deploy.models import Instance
from poa_deploy.classes import Api
import poa_deploy.utils as utils
import poa_deploy.poa_manage as poamngmnt
from poa_deploy.exc import AppExists, ApiError
import json


def index(request):
    application_list = Application.objects.order_by('id')
    installation_list = Installation.objects.order_by('id')
    return render(request, 'poa_deploy/index.html', {'application_list': application_list,
                                                     'installation_list': installation_list,
                                                     'pagetitle': 'Main'})

def add_poa_installation(request):
    """ Adds POA MN to Django database"""
    if request.is_ajax():
        mn_ip = request.POST['mn_ip']
        try:
            poamngmnt.add_new_installation(mn_ip)
            response = {'status': 0}
        except Exception as e:
            response = {'status': 1, 'Error': str(e)}
    return HttpResponse(json.dumps(response), content_type='application/json')

def add_application_to_database(request):
    """ Adds app info only to Django database """

    if request.is_ajax() and utils.application_url_correct(request.POST['aps_url']):
        url = request.POST['aps_url']
        app_meta_url = utils.get_appmeta_url(url)
        app_meta_parsed = utils.get_app_meta_parsed(app_meta_url)
        app_attributes = utils.get_application_attributes(app_meta_parsed)
        if app_attributes is not None and not Application.objects.filter(**app_attributes).exists():
            app_attributes.update({'url': url})
            response = {'status': 0, 'result': 'Application added successfully'}
            Application.objects.create(**app_attributes)
        else:
            response = {'status': 1, 'result': 'Application cannot be added'}
    else:
        response = {'status': 1, 'result': 'Application cannot be added'}
    return HttpResponse(json.dumps(response), content_type='application/json')

def install_application(request):
    if request.is_ajax():
        mn_ip = request.POST['mn_ip']
        app_id = request.POST['app_id']
        connection = utils.connect_via_rpc(mn_ip)
        application = Application.objects.get(pk=app_id)
        if connection is not None and application is not None:
            txn_id = connection.txn.Begin()['result']['txn_id']
            try:
                api = Api(connection, txn_id)
                instance_params = utils.fully_provide_application(application, api)
                connection.txn.Commit({'txn_id': txn_id})
                instance = Instance.objects.create(**instance_params)
                response = {'status': 0, 'result': 'Application id is ' + str(instance.instance_id)}
            except Exception as e:
                connection.txn.Rollback({'txn_id': txn_id})
                response = {'status': 1, 'result': 'Error ' + str(e) + ' , action rolled back'}
        else:
            return None
    return HttpResponse(json.dumps(response), content_type='application/json')

def get_applications(request):
    if request.method == 'POST' and request.is_ajax():
        applications = Application.objects.order_by('id')
        json_response = serializers.serialize('json', applications)
        return HttpResponse(json_response, content_type='application/json')
    else:
        return HttpResponse('Request is invalid')
