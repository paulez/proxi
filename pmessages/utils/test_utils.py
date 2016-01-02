from django.test import TestCase, RequestFactory

from .geoutils import GeoUtils

class GeoUtilsTest(TestCase):
    def setUp(self):
        self.utils = GeoUtils()
        self.factory = RequestFactory()

    def test_http_forwarded(self):
        """
        HTTP_X_FORWARDED_FOR set. We expect the first ip which can be 
        localized to be returned.
        The returned position should be set too.
        """
        request = self.factory.get('/',
                HTTP_X_FORWARDED_FOR='10.0.0.2, 73.254.66.16, 212.27.60.48',
                REMOTE_ADDR='195.154.231.43')
        (pos, address) = self.utils.get_user_location_address(request)
        assert address == '73.254.66.16'
        assert pos is not None

    def test_http_remote(self):
        """
        REMOTE_ADDR is set, with a localisable address.
        This address should be returned, and the position should be set.
        """
        request = self.factory.get('/', REMOTE_ADDR='195.154.231.43')
        (pos, address) = self.utils.get_user_location_address(request)
        assert address == '195.154.231.43'
        assert pos is not None

    def test_http_local(self):
        """
        REMOTE_ADDR is set with a local address.
        This address should be returned, but the position sould be None.
        """
        request = self.factory.get('/', REMOTE_ADDR='10.0.0.2')
        (pos, address) = self.utils.get_user_location_address(request)
        assert address == '10.0.0.2'
        assert pos is None

