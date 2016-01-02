from django.contrib.gis.geoip import GeoIP
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

class GeoUtils:
    def __init__(self):
        self.g = GeoIP()
        
    def get_point_from_ip(self, ip):
        # Return geo point corresponding to ip
        return self.g.geos(ip)

    def get_user_location_address(self, request):
        # get user possible ip address list and return first associated location found and associated address
        address = self._get_user_address_list(request)
        last_address = None
        for ip in address:
            loc = self.get_point_from_ip(ip)
            last_address = ip
            if loc:
                return (loc, ip)
        error('Cannot locate user from adress %s, last address is %s', 
                address, last_address)
        return (None, last_address)
        
    def _get_user_address_list(self, request):
        # get a list of possible user ip address from request
        forwarded_header = 'HTTP_X_FORWARDED_FOR'
        remote_header = 'REMOTE_ADDR'
        if forwarded_header in request.META:
            ip = request.META[forwarded_header]
            ip = ip.split(",")
            adresses = [x.strip() for x in ip]
        else:
            adresses = [request.META[remote_header]]
        debug('geoip addresses: %s', adresses)
        return adresses
