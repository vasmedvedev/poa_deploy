import socket
from poa_deploy.models import Installation


def add_new_installation(mn_ip):
    ip_regex = '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.\
               (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.\
               (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.\
               (25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ip_regex, mn_ip) is not None:
        if not Installation.objects.get(ip_address=mn_ip).exists():
            poa = Installation(ip_address=mn_ip, status=False)
            poa.save()
        else:
            raise Exception('This installation is added already')
    else:
        raise Exception('IP address is not valid IPV4 address')
    
def update_poa_status(poa_instance):
    s = socket.socket()
    port = 8352 #pleskd port hardcoded
    result = s.connect_ex((address, port))
    poa_instance.status = True if result == 0 else False
    poa_instance.save()