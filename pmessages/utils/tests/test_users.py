from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.urls import reverse

from pmessages.utils import users, session
from pmessages.utils.users import SessionUser, ExpiredUser, UserDoesNotExist
from pmessages.models import ProxyUser

user_url = reverse("pmessages:api-user")

class UserUtilsTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get(user_url)
        self.request.session = {}
        self.request.query_params = {}

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

    def test_non_existing_user(self):
        session_user = SessionUser(
            id=42, name=self.name1,
            expiration=timezone.now() - timedelta(hours=1)
        )
        with self.assertRaises(UserDoesNotExist):
            users.get_user(session_user)

    def test_get_user_from_request(self):
        self.request.session = {
            session.SLOCATION: self.pos1,
            session.SUSERNAME: self.name1,
            session.SUSER_ID: self.user_id,
            session.SUSER_EXPIRATION: timezone.now()
        }
        user = users.get_user_from_request(self.request)
        self.assertEqual(user.name, self.name1)

    def test_get_user_from_request_refresh(self):
        delta = timedelta(minutes=settings.PROXY_USER_REFRESH + 1)
        self.request.session = {
            session.SLOCATION: self.pos1,
            session.SUSERNAME: self.name1,
            session.SUSER_ID: self.user_id,
            session.SUSER_EXPIRATION: timezone.now() - delta
        }
        user = users.get_user_from_request(self.request)
        self.assertLess(
                timezone.now() - timedelta(seconds=10), 
                user.expiration
        )
        self.assertLess(
                timezone.now() - timedelta(seconds=10), 
                self.request.session[session.SUSER_EXPIRATION]
        )
