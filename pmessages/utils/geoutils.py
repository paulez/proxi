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
        address = self.get_user_address_list(request)
        for ip in address:
            loc = self.get_point_from_ip(ip)
            if loc:
                return (loc, ip)
        error('Cannot locate user from adress %s.', address)
        return (None, None)
        
    def get_user_address_list(self, request):
        # get a list of possible user ip address from request
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
            ip = ip.split(",")
            return [x.strip() for x in ip]
            
        except KeyError:
            return [request.META['REMOTE_ADDR']]    
