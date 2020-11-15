from django.test import TestCase, RequestFactory
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http.response import Http404
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from rest_framework.test import force_authenticate
import logging

from pmessages.utils import messages
from pmessages.utils import session
from pmessages.models import ProxyMessage, ProxyUser

messages_url = reverse("pmessages:api-messages")

logger = logging.getLogger(__name__)
debug = logger.debug

SRID = 4326


class MessageUtilsTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get(messages_url)
        self.request.session = {}
        self.request.query_params = {}

        self.pos1 = Point(-127, 42, srid=SRID)
        self.pos2 = Point(127, 42, srid=SRID)

        self.username = "toto"
        self.address = "127.0.0.1"
        self.user = ProxyUser.register_user(
            self.username, self.pos2
        )

        self.messages_1 = set()
        self.messages_2 = set()

        for __ in range(5):
            message = ProxyMessage(username=self.username, message="blah",
                                   address=self.address, location=self.pos1)
            message.save()
            self.messages_1.add(message)

        for __ in range(10):
            message = ProxyMessage(username=self.username, message="bloh",
                                   address=self.address, location=self.pos2,
                                   user=self.user)
            message.save()
            self.messages_2.add(message)

        old_date = timezone.now() - timedelta(days=365)
        old_message = ProxyMessage(
            username=self.username, message="vieux",
            address=self.address, location=self.pos2)
        old_message.date = old_date
        old_message.save()
        ProxyMessage(
            username=self.username, message="vieux",
            address=self.address, location=self.pos1)
        old_message.date = old_date
        old_message.save()

    def test_get_messages(self):
        distance = D(km=1)
        test_messages = messages.get_messages(self.pos1, distance)
        self.assertEqual(set(test_messages), self.messages_1)

        test_messages = messages.get_messages(self.pos2, distance)
        self.assertEqual(set(test_messages), self.messages_2)

    def test_search_messages(self):
        distance = D(km=10000)
        test_messages = messages.get_messages(self.pos1, distance,
                                              search_request="bl")
        self.assertEqual(
            set(test_messages),
            self.messages_2.union(self.messages_1))

        test_messages = messages.get_messages(self.pos1, distance,
                                              search_request="bloh")
        self.assertEqual(
            set(test_messages),
            self.messages_2)

    def test_get_messages_for_request_empty_session(self):
        with self.assertRaises(Http404):
            messages.get_messages_for_request(self.request, None)

    def test_get_messages_for_request_with_session(self):
        force_authenticate(self.request, user=self.user)
        test_messages = messages.get_messages_for_request(self.request,
                                                          self.pos1)
        self.assertFalse(not test_messages)
        for message in test_messages:
            debug(
                "Current user for message %s is %s for %s",
                message,
                message.username,
                message.current_user
            )
            self.assertFalse(message.current_user)

        # Get messages from a location for which messages had a user set.
        force_authenticate(self.request, user=self.user)
        test_messages = messages.get_messages_for_request(self.request,
                                                          self.pos2)
        for message in test_messages:
            self.assertTrue(message.current_user)

        # Get messages from location for which messages didn't have
        # a user set.
        # Clear message history
        self.request.session[session.SMESSAGE_HISTORY] = []
        test_messages = messages.get_messages_for_request(self.request,
                                                          self.pos1)
        for message in test_messages:
            self.assertFalse(message.current_user)
