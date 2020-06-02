from django.contrib.gis.geos import Point
from django.urls import reverse
from logging import getLogger
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from pmessages.models import ProxyMessage
from ..utils.geo import get_point_from_ip

login_url = reverse("pmessages:api-login")
logout_url = reverse("pmessages:api-logout")
message_url = reverse("pmessages:api-message")
messages_url = reverse("pmessages:api-messages")
position_url = reverse("pmessages:api-position")
user_url = reverse("pmessages:api-user")
radius_url = reverse("pmessages:api-radius")

logger = getLogger(__name__)

SRID = 4326

class UserTests(APITestCase):

    def test_login_without_position(self):
        data = {"username": "toto"}
        response = self.client.post(login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_logout(self):
        data = {"latitude": 42, "longitude": 127}
        response = self.client.post(
            position_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(user_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = {"username": "toto"}
        response = self.client.post(
            login_url, data, format="json")
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # login twice
        response = self.client.post(
            login_url, data, format="json")
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(user_url)
        self.assertEqual(response.data, {"username": "toto"})

        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # can't logout twice
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_logout_login(self):
        data = {"latitude": 42, "longitude": 127}
        response = self.client.post(
            position_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # first login
        data = {"username": "toto"}
        response = self.client.post(
            login_url, data, format="json")
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(radius_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        # login out
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # login back
        response = self.client.post(
            login_url, data, format="json")
        self.assertEqual(response.data, data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_login_conflict(self):
        position_data = {"latitude": 42, "longitude": 127}
        response = self.client.post(
            position_url, position_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(user_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        login_data = {"username": "toto"}
        response = self.client.post(
            login_url, login_data, format="json")
        self.assertEqual(response.data, login_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # second client

        client2 = APIClient()

        # login twice
        response = client2.post(
            login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = client2.post(
            position_url, position_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = client2.post(
            login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        login_data2 = {"username": "toto2"}
        response = client2.post(
            login_url, login_data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # login out
        response = client2.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_expired_user(self):
        data = {"latitude": 42, "longitude": 127}
        response = self.client.post(
            position_url, data, format="json")
        data = {"username": "toto"}
        response = self.client.post(
            login_url, data, format="json")

        response = self.client.get(user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with self.settings(PROXY_USER_EXPIRATION=0):
            response = self.client.get(user_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class MessageTests(APITestCase):

    def setUp(self):
        self.message_data = {"message": "plop le monde"}

        self.test_ip = "68.141.147.38"
        self.pos1 = get_point_from_ip(self.test_ip)
        self.pos2 = Point(42, 127, srid=SRID)

        self.msg1 = ProxyMessage(username="titi", message="blah",
            address="127.0.0.1", location=self.pos1)
        self.msg1.save()

        self.msg2 = ProxyMessage(username="tutu", message="bloh",
            address="127.0.0.1", location=self.pos2)
        self.msg2.save()

    def test_post_message_without_login(self):
        response = self.client.post(
            message_url, self.message_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_messages_no_position(self):
        response = self.client.get(messages_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get(messages_url, REMOTE_ADDR=self.test_ip)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_messages_change_position(self):
        self.client.get(messages_url, REMOTE_ADDR=self.test_ip)
        data = {"latitude": self.pos2.y, "longitude": self.pos2.x}
        self.client.post(position_url, data, format="json")
        response = self.client.get(messages_url, longitude=self.pos2.x,
                                   latitude=self.pos2.y)
        logger.debug("Response data: %s", response.data)
        response_messages = [msg["uuid"] for msg in response.data]
        expected_messages = [str(self.msg2.uuid)]
        self.assertEqual(response_messages, expected_messages)
        self.assertEqual(len(response.data), 1)

class MessageTestsWithLoginAndPosition(APITestCase):
    def setUp(self):
        self.message_data = {"message": "plop le monde"}
        self.pos1 = Point(127, 42, srid=SRID)
        data = {"latitude": self.pos1.y, "longitude": self.pos1.x}

        self.pos2 = Point(42, 127, srid=SRID)
        self.client.post(position_url, data, format="json")

        data = {"username": "toto"}
        self.client.post(login_url, data, format="json")

        self.msg1 = ProxyMessage(username="titi", message="blah",
            address="127.0.0.1", location=self.pos1)
        self.msg1.save()

        self.msg2 = ProxyMessage(username="tutu", message="bloh",
            address="127.0.0.1", location=self.pos2)
        self.msg2.save()

    def tearDown(self):
        self.client.post(logout_url)

    def test_post_message_success(self):
        response = self.client.post(
            message_url, self.message_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_messages_success(self):
        response = self.client.get(messages_url)
        self.assertEqual(response.data[0]["uuid"], str(self.msg1.uuid))
        self.assertEqual(len(response.data), 1)

    def test_delete_message(self):
        self.client.post(
            message_url, self.message_data, format="json"
        )
        response = self.client.get(messages_url)
        message_uuid = response.data[0]["uuid"]
        response = self.client.delete(
            "{url}/{uuid}".format(
                url=message_url,
                uuid=message_uuid
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # deleting the same message twice shouldn't cause an error
        response = self.client.delete(
            "{url}/{uuid}".format(
                url=message_url,
                uuid=message_uuid
            ),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_messages_change_position(self):
        self.client.get(messages_url)
        data = {"latitude": self.pos2.y, "longitude": self.pos2.x}
        self.client.post(position_url, data, format="json")
        response = self.client.get(messages_url)
        logger.debug("Response data: %s", response.data)
        response_messages = sorted([msg["uuid"] for msg in response.data])
        expected_messages = sorted([str(self.msg1.uuid), str(self.msg2.uuid)])
        self.assertEqual(response_messages, expected_messages)
        self.assertEqual(len(response.data), 1)

    def test_get_messages_logout(self):
        """
        Ensure messages are not deleted after user logout.
        """
        response = self.client.post(message_url, self.message_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(messages_url)
        self.assertEqual(len(response.data), 2)

class RadiusTests(APITestCase):

    def setUp(self):
        self.test_ip = "68.141.147.38"

    def test_get_radius_no_session(self):
        response = self.client.get(radius_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_radius_with_ip(self):
        response = self.client.get(radius_url, REMOTE_ADDR=self.test_ip)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
