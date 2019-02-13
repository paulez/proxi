from datetime import timedelta

from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone

from pmessages.utils import users
from pmessages.utils.users import SessionUser, ExpiredUser, UserDoesNotExist
from pmessages.models import ProxyUser

class UserUtilsTest(TestCase):

    def setUp(self):
        self.pos1 = Point(-127, 42)
        self.name1 = "toto"
        self.user_id = ProxyUser.register_user(username=self.name1, pos=self.pos1)

    def test_get_user(self):
        now = timezone.now()
        session_user = SessionUser(
                id=42,
                name=self.name1,
                expiration=now
        )
        user = users.get_user(session_user)
        self.assertEqual(user.name, self.name1)
        self.assertEqual(user.expiration, now)

    def test_get_user_refresh(self):
        delta = timedelta(minutes=settings.PROXY_USER_REFRESH + 1)
        session_user = SessionUser(
                id=self.user_id,
                name=self.name1,
                expiration=timezone.now() - delta
        )
        user = users.get_user(session_user)
        self.assertEqual(user.name, self.name1)
        self.assertLess(
                timezone.now() - timedelta(seconds=10), 
                user.expiration
        )

    def test_undefined_user(self):
        session_user = SessionUser(None, None, None)
        with self.assertRaises(UserDoesNotExist):
            users.get_user(session_user)
        
        session_user = SessionUser(
                id=42, name=self.name1, expiration=None
        )
        with self.assertRaises(ExpiredUser):
            users.get_user(session_user)

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
