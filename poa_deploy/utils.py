import re
import xmlrpclib
import socket
import urllib2
import xml.etree.ElementTree as ET
from poa_deploy.models import Instance

#import logging


def application_url_correct(url):
    app_url_regex = '^https:\/\/apscatalog\.com\/storage.*app\.zip$'
    return True if re.match(app_url_regex, url) is not None else False

def get_appmeta_url(url):
    return '/'.join(url.split('/')[:-1]) + '/resources/APP-META.xml'

def get_app_meta_parsed(app_meta_url):
    """ Let's get ElementTree object from APP-META """

    app_meta_url_regex = '^https:\/\/apscatalog\.com\/storage.*APP-META.xml$'
    if re.match(app_meta_url_regex, app_meta_url) is not None:
        request = urllib2.Request(app_meta_url, headers={"Accept" : "application/xml"})
        try:            
            response = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            return None
        tree = ET.parse(response)
        return tree.getroot()
    else:
        return None

def get_application_attributes(app_meta_parsed):
        attributes = dict()
        attributes['aps_version'] = '1.0' if not app_meta_parsed.attrib else app_meta_parsed.attrib['version']
        if attributes['aps_version'] == '2.0':
            attributes['package_version'] = '-'.join([app_meta_parsed.find('{http://aps-standard.org/ns/2}version').text,
                                                      app_meta_parsed.find('{http://aps-standard.org/ns/2}release').text])
            attributes['app_name'] = app_meta_parsed.find('{http://aps-standard.org/ns/2}name').text
        else:
            attributes['package_version'] = '-'.join([app_meta_parsed.find('{http://apstandard.com/ns/1}version').text,
                                                      app_meta_parsed.find('{http://apstandard.com/ns/1}release').text])
            attributes['app_name'] = app_meta_parsed.find('{http://apstandard.com/ns/1}name').text
        return attributes
     

def get_application_mandatory_settings(app_meta_parsed):
    """ Let's define and return random values for autoprovisioning.
        Returns list of dicts.
    """

    mandatory_settings_ids_list = [setting.attrib['id'] for setting in app_meta_parsed.findall(".//{http://apstandard.com/ns/1}setting")
                                   if 'default-value' not in setting.attrib and 'min-length' in setting.attrib]
    random_value = 'ADMINPASSWORD4'
    return [{'name': setting_id, 'value': random_value} for setting_id in mandatory_settings_ids_list]

def connect_via_rpc(mn_ip):
    """ Let's try if API is accessible """

    api_url = 'http://' + mn_ip + ':8440/RPC2'
    connection = xmlrpclib.ServerProxy(api_url)
    try:
        connection._()
    except xmlrpclib.Fault:
        pass
    except socket.error:
        return None
    return connection

def create_rt_for_app(poa_application_id, app_name, api):
    params = {'resclass_name': 'siteapps',
              'name': app_name,
              'act_params':[{'var_name': 'app_id', 'var_value': str(poa_application_id)}],
                             'txn_id': api.txn_id}
    return api.execute('pem.addResourceType', **params)

def import_app_to_poa(app_url, api):
    params = {'package_url': app_url, 'txn_id': api.txn_id}
    return api.execute('pem.APS.importPackage', **params)

def create_service_template(rt_id, app_name, api):
    """ GET RID OF HARDCODED SHIT! """

    st_id = api.execute('pem.cloneServiceTemplate', **{'service_template_id': 4, 'name': app_name + '-autotest', 'txn_id': api.txn_id})['st_id']
    api.execute('pem.addResourceTypeToServiceTemplate', **{'owner_id': 1, 'st_id': st_id, 'rt_id': rt_id, 'txn_id': api.txn_id})
    api.execute('pem.setSTRTLimits', **{'st_id': st_id, 'limits':[{'resource_id': rt_id, 'resource_limit': -1}], 'txn_id': api.txn_id})
    api.execute('pem.activateST', **{'st_id': st_id, 'txn_id': api.txn_id})
    return st_id

def create_subscription(st_id, app_name, api):
    domain_name = app_name.replace(" ", "") + '-autotest.com'
    params = {'subscription_name': app_name.replace(" ", "") + "-autotest",
              'account_id': 5,
              'service_template_id': st_id,
              'parameters': [{'var_name': 'domain_name',
                              'var_value': domain_name }],
              'txn_id': api.txn_id }
    response = api.execute('pem.activateSubscription', **params)
    response.update({'domain_name': domain_name})
    return response

def provide_application_instance(sub_id, rt_id, domain_name, api, settings):
    params = {'subscription_id': sub_id,
              'rt_id': rt_id,
              'domain_name': domain_name,
              'settings': settings,
              'txn_id': api.txn_id }
    return api.execute('pem.APS.provideApplicationInstance', **params)

def fully_provide_application(application, api):
    app_name = application.app_name
    app_url = application.url
    app_meta_url = get_appmeta_url(app_url)
    app_meta_parsed = get_app_meta_parsed(app_meta_url)
    application_settings = get_application_mandatory_settings(app_meta_parsed)
    import_response = import_app_to_poa(app_url, api)
    poa_app_id = import_response.get('application_id')
    #poa_app_id = 204
    rt_response = create_rt_for_app(poa_app_id, app_name, api)
    rt_id = rt_response.get('resource_type_id')
    st_id = create_service_template(rt_id, app_name, api)
    subscr_response = create_subscription(st_id, app_name, api)
    sub_id = subscr_response.get('subscription_id')
    domain_name = subscr_response.get('domain_name')
    instance_response = provide_application_instance(sub_id, rt_id,
                             domain_name, api, application_settings)
    instance_id = instance_response.get('application_instance_id')
    instance_params = {'st_id': st_id,
                       'rt_id': rt_id,
                       'poa_app_id': poa_app_id,
                       'sub_id': sub_id,
                       'instance_id' : instance_id,
                       'domain_name': domain_name}
    return instance_params

def cleanup_instance(instance, api):
    remove_sub(instance.sub_id, api)
    remove_domain(instance.domain_name, api)
    remove_st(instance.st_id, api)
    remove_rt(instance.rt_id, api)
    remove_application_from_poa(instance.poa_app_id)

def remove_sub(sub_id, api):
    params = {'subscription_id': sub_id}
    api.execute('pem.removeSubscription', **params)
    
def remove_domain(domain_name, api, domain_id=None):
    params = {'domain_name': domain_name} if domain_name is None\
        else {'domain_id': domain_id}
    api.execute('pem.removeDomain', **params)

def remove_st(st_id, api):
    params = {'st_id': st_id}
    api.execute('pem.removeServiceTemplate', **params)

def remove_rt(rt_id, api):
    params = {'rt_id': rt_id}
    api.execute('pem.removeResourceType', **params)

def remove_application_from_poa(app_id, api):
    params = {'application_id': app_id}
    api.execute('pem.APS.removeApplication', **params)
