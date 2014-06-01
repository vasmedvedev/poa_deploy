import re
import xmlrpclib
import socket
import urllib2
import xml.etree.ElementTree as ET
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
        attributes = {}
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
    random_value = '1qazXSW@'
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
    domain_name = app_name + '-autotest.com'
    params = {'subscription_name': app_name + "-autotest",
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
