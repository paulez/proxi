from django.test import TestCase
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from pmessages.utils import users
from pmessages.models import ProxyUser

user_url = reverse("pmessages:api-user")

SRID = 4326


class UserUtilsTest(TestCase):
    def setUp(self):
        self.pos1 = Point(-127, 42, srid=SRID)
        self.name1 = "toto"
        self.user = ProxyUser.register_user(username=self.name1, pos=self.pos1)
        self.token = users.create_token(self.user)

    def test_get_user_from_request(self):
        factory = APIRequestFactory()
        request = factory.get(user_url)
        force_authenticate(request=request, user=self.user, token=self.token)
        # workaround as force_authenticate doesn't set request.user
        request.user = self.user
        user = users.get_user_from_request(request)
        self.assertEqual(user, self.user)
