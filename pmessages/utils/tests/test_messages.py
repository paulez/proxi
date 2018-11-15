from django.test import TestCase
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from datetime import timedelta

from pmessages.utils import messages
from pmessages.models import ProxyMessage

class MessageUtilsTest(TestCase):
    def setUp(self):
        self.pos1 = Point(-127, 42)
        self.pos2 = Point(127, 42)
        self.username = "toto"
        self.address = "127.0.0.1"
        
        self.messages_1 = set()
        self.messages_2 = set()

        for __ in range(5):
            message = ProxyMessage(username=self.username, message="blah",
                address=self.address, location=self.pos1)
            message.save()
            self.messages_1.add(message)

        for __ in range(10):
            message = ProxyMessage(username=self.username, message="bloh",
                address=self.address, location=self.pos2)
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
        