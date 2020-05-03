"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import timedelta

from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import Point

from pmessages.models import ProxyIndex, ProxyMessage, ProxyUser

SRID=4326

class ProxyModelTests(TestCase):
    def setUp(self):
        self.position = Point(-127, 42, srid=SRID)
        self.username = "toto"
        self.address = "127.0.0.1"

class ProxyUserTests(ProxyModelTests):
    def test_register_user(self):
        """
        Test that a single user cannot be registered twice.
        """
        ProxyUser.register_user(self.username, self.position)
        second_user = ProxyUser.register_user(self.username, self.position)
        self.assertFalse(second_user)

class ProxyMessageTests(ProxyModelTests):
    def test_create_message(self):
        message = ProxyMessage(username=self.username, message="blah",
                address=self.address, location=self.position)
        message.save()
        self.assertEqual(message.location, self.position)

    def test_near_radius(self):
        self.assertEqual(ProxyMessage.near_radius(self.position, self.username),
                settings.PROXY_RADIUS_MAX)
        # Messages created by same username don't change the radius
        for __ in range(10):
            message = ProxyMessage(username=self.username, message="blah",
                    address=self.address, location=self.position)
            message.save()
        self.assertEqual(ProxyMessage.near_radius(self.position, self.username),
                settings.PROXY_RADIUS_MAX)
        self.assertEqual(ProxyMessage.near_radius(self.position, None),
                settings.PROXY_RADIUS_MIN)
        for __ in range(10):
            message = ProxyMessage(username="roger", message="blah",
                    address=self.address, location=self.position)
            message.save()
        self.assertEqual(ProxyMessage.near_radius(self.position, self.username),
                settings.PROXY_RADIUS_MIN)

class ProxyIndexTests(ProxyModelTests):
    def test_create_index(self):
        radius = 42
        ProxyIndex.create_index(self.position, radius)
        near_index = ProxyIndex.indexed_radius(
                self.position, self.username, interval=timedelta(minutes=10))
        self.assertEqual(near_index, radius)
        near_index = ProxyIndex.indexed_radius(
                self.position, self.username, interval=timedelta(minutes=0))
        self.assertEqual(near_index, settings.PROXY_RADIUS_MAX)
