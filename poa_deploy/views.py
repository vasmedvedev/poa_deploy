from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from poa_deploy.models import Method, Application, Installation
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
            response = {'status': 0}
            application = Application(**app_attributes)
            response.update({'app_url': application.url})
            application.save()
        else:
            response = {'status': 1}
    else:
        response = {'status': 1}
    return HttpResponse(json.dumps(response), content_type='application/json')

def install_application(request):
    if request.is_ajax():
        mn_ip = request.POST['mn_ip']
        app_id = request.POST['app_id']
        connection = utils.connect_via_rpc(mn_ip)
        application = Application.objects.get(pk=app_id)
        if connection is not None and application is not None:
            try:
                app_name = application.app_name
                app_url = application.url
                app_meta_url = utils.get_appmeta_url(app_url)
                app_meta_parsed = utils.get_app_meta_parsed(app_meta_url)
                application_settings = utils.get_application_mandatory_settings(app_meta_parsed)
                txn_id = connection.txn.Begin()['result']['txn_id']
                api = Api(connection, txn_id)
                #import_response = utils.import_app_to_poa(app_url, api)
                #rt_response = utils.create_rt_for_app(import_response['application_id'], app_name, api)
                rt_response = utils.create_rt_for_app(198, app_name, api)
                st_id = utils.create_service_template(rt_response['resource_type_id'], app_name, api)
                subscr_response = utils.create_subscription(st_id, app_name, api)
                instance_response = utils.provide_application_instance(subscr_response['subscription_id'],
                                                                        rt_response['resource_type_id'],
                                                                        subscr_response['domain_name'],
                                                                        api,
                                                                        application_settings)
                connection.txn.Commit({'txn_id': txn_id})
                response = {'status': 0}
            except Exception as e:
                connection.txn.Rollback({'txn_id': txn_id})
                response = {'status': 1, 'Error': str(e) + ' , action rolled back'}
        else:
            return None
        
    return HttpResponse(json.dumps(response), content_type='application/json')
