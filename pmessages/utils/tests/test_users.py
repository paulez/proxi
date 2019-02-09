from datetime import timedelta

from django.test import TestCase
from django.contrib.gis.geos import Point
from django.utils import timezone

from pmessages.utils import users
from pmessages.utils.users import SessionUser, ExpiredUser, UserDoesNotExist
from pmessages.models import ProxyUser

class UserUtilsTest(TestCase):

    def setUp(self):
        self.pos1 = Point(-127, 42)
        self.name1 = "toto"
        ProxyUser.register_user(username=self.name1, pos=self.pos1)

    def test_get_user(self):
        session_user = SessionUser(id=42, name=self.name1, expiration=None)
        user = users.get_user(session_user)
        self.assertEqual(user.name, self.name1)

    def test_expired_user(self):
        session_user = SessionUser(
            id=42, name=self.name1,
            expiration=timezone.now() - timedelta(days=100)
        )
        with self.assertRaises(ExpiredUser):
            users.get_user(session_user)

    def non_existing_user(self):
        session_user = SessionUser(
            id=42, name=self.name1,
            expiration=timezone.now() - timedelta(hours=1)
        )
        with self.assertRaises(UserDoesNotExist):
            users.get_user(session_user)