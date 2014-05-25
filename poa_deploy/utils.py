import re
import xmlrpclib
import socket
import urllib2
import xml.etree.ElementTree as ET
import logging
from exceptions import ApiError


def application_url_correct(url):
	app_url_regex = '^https:\/\/apscatalog\.com\/storage.*app\.zip$'
	return True if re.match(app_url_regex, url) is not None else False

def get_appmeta_url(url):
	return '/'.join(url.split('/')[:-1]) + '/resources/APP-META.xml'

def get_application_attributes(app_meta_url):
	app_meta_url_regex = '^https:\/\/apscatalog\.com\/storage.*APP-META.xml$'
	if re.match(app_meta_url_regex, app_meta_url) is not None:
		attributes = {}
		request = urllib2.Request(app_meta_url, headers={"Accept" : "application/xml"})
		try:			
			response = urllib2.urlopen(request)
		except urllib2.HTTPError, e:
			return None
		tree = ET.parse(response)
		root = tree.getroot()
		attributes['aps_version'] = '1.0' if not root.attrib else root.attrib['version']
		if attributes['aps_version'] == '2.0':
			attributes['package_version'] = '-'.join([root.find('{http://aps-standard.org/ns/2}version').text,
													  root.find('{http://aps-standard.org/ns/2}release').text])
			attributes['app_name'] = root.find('{http://aps-standard.org/ns/2}name').text
		else:
			attributes['package_version'] = '-'.join([root.find('{http://apstandard.com/ns/1}version').text,
													  root.find('{http://apstandard.com/ns/1}release').text])
			attributes['app_name'] = root.find('{http://apstandard.com/ns/1}name').text
		return attributes
	else:
		return None

def connect_via_rpc(mn_ip):
	"""	Let's try if API is accessible """

	api_url = 'http://' + mn_ip + ':8440/RPC2'
	connection = xmlrpclib.ServerProxy(api_url)
	try:
		connection._()
	except xmlrpclib.Fault:
		pass
	except socket.error:
		return None
	return connection

def create_rt_for_app(poa_application_id, application, api_connection, txn_id):
	response = api_connection.pem.addResourceType({'resclass_name': 'siteapps',
										'name': application.app_name,
										'act_params':[{'var_name': 'app_id', 'var_value': str(poa_application_id)}],
										'txn_id': txn_id
										})
	if response['status'] != 0:
		raise ApiError('Method pem.addResourceType returned %s' % str(response['status']))
	else:
		return response['result']

def import_app_to_poa(application, api_connection, txn_id):
	""" Add to app vault and return dict with package version and id """

	response = api_connection.pem.APS.importPackage({'package_url': application.get_url(), 'txn_id': txn_id})
	if response['status'] != 0:
		raise ApiError('Method pem.APS.importPackage returned %s' % str(response['status']))
	else:
		return response['result']

def create_service_template(rt_id, application, api_connection, txn_id):
	"""Let's clone st_id = 4, Apache with MySQL,
		and activate it
	"""

	clone_response = api_connection.pem.cloneServiceTemplate({'service_template_id': 4, 'name': application.app_name, 'txn_id': txn_id})
	if clone_response['status'] != 0:
		raise ApiError('Method pem.cloneServiceTemplate %s' % str(clone_response['status']))
	cloned_st_id = clone_response['result']['st_id']
	api_connection.pem.addResourceTypeToServiceTemplate({'owner_id': 1, 'st_id': cloned_st_id, 'rt_id': rt_id, 'txn_id': txn_id})
	api_connection.pem.setSTRTLimits({'st_id': cloned_st_id, 'limits':[{'resource_id': rt_id, 'resource_limit': -1}], 'txn_id': txn_id})
	api_connection.pem.activateST({'st_id': cloned_st_id, 'txn_id': txn_id})
	return cloned_st_id