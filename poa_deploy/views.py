from django.shortcuts import render, get_object_or_404
from django.core import serializers
from django.http import HttpResponse
from poa_deploy.models import Method, Application
import poa_deploy.utils as utils
from poa_deploy.exceptions import AppExists, ApiError
import json


def index(request):
    application_list = Application.objects.order_by('id')
    return render(request, 'poa_deploy/index.html', {'application_list': application_list, 'pagetitle': 'Main'})

def add_application_to_database(request):
    """ Adds app info only to django database """

    if request.is_ajax() and utils.application_url_correct(request.POST['aps_url']):
        url = request.POST['aps_url']
        app_meta_url = utils.get_appmeta_url(url)
        app_attributes = utils.get_application_attributes(app_meta_url)
        if app_attributes is not None and not Application.objects.filter(**app_attributes).exists():
            app_attributes.update({'url': url})
            response = {'status': 0}
            application = Application(**app_attributes)
            response.update({'app_url': application.get_url()})
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
                txn_id = connection.txn.Begin()['result']['txn_id']
                import_response = utils.import_app_to_poa(application, connection, txn_id)
                rt_response = utils.create_rt_for_app(import_response['application_id'], application, connection, txn_id)
                st_id = utils.create_service_template(rt_response['resource_type_id'], application, connection, txn_id)
            except ApiError as e:
                response = {'status': 1, 'Error': str(e)}
        else:
            return None
        response = {'status': 0}

    return HttpResponse(json.dumps(response), content_type='application/json')
