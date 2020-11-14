from django.contrib.gis.geos import Point
from django.urls import reverse
from logging import getLogger
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from pmessages.models import ProxyMessage
from ..utils.geo import get_point_from_ip

message_url = reverse("pmessages:api-message")
messages_url = reverse("pmessages:api-messages")
position_url = reverse("pmessages:api-position")
user_url = reverse("pmessages:api-user")
radius_url = reverse("pmessages:api-radius")
register_url = reverse("pmessages:api-register")

logger = getLogger(__name__)

SRID = 4326

class UserTests(APITestCase):

    def setUp(self):
        self.pos_data = {
            "location": {
                "latitude": 42,
                "longitude": 127
            }
        }
        self.pos_param = self.pos_data["location"]

    def test_get_user(self):

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
        response = self.client.get(
            messages_url,
            {"longitude": self.pos2.x,
             "latitude": self.pos2.y}
        )
        logger.debug("Response data: %s", response.data)
        response_messages = [msg["uuid"] for msg in response.data]
        expected_messages = [str(self.msg2.uuid)]
        self.assertEqual(response_messages, expected_messages)
        self.assertEqual(len(response.data), 1)

class MessageTestsWithLoginAndPosition(APITestCase):
    def setUp(self):
        self.message_content = {"message": "plop le monde"}
        self.pos1 = Point(127, 42, srid=SRID)
        self.pos1_param = {"latitude": self.pos1.y, "longitude": self.pos1.x}
        self.pos1_data = {"location": self.pos1_param}
        self.message_data = {**self.message_content, **self.pos1_data}

        self.pos2 = Point(42, 127, srid=SRID)
        self.client.post(position_url, self.pos1_data, format="json")

        data = {"username": "toto", **self.pos1_data}
        response = self.client.post(register_url, data, format="json")
        print(response.json())
        self.token = response.json()["token"]

        self.msg1 = ProxyMessage(username="titi", message="blah",
            address="127.0.0.1", location=self.pos1)
        self.msg1.save()

        self.msg2 = ProxyMessage(username="tutu", message="bloh",
            address="127.0.0.1", location=self.pos2)
        self.msg2.save()

    def tearDown(self):
        self.client.post(logout_url)

    def test_post_message_without_location(self):
        response = self.client.post(
            message_url, self.message_content, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_message_success(self):
        response = self.client.post(
            message_url, self.message_data, format="json"
        )
        self.assertEqual(response.data, {"message": "plop le monde"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_get_messages_success(self):
        response = self.client.get(messages_url, self.pos1_param)
        self.assertEqual(response.data[0]["uuid"], str(self.msg1.uuid))
        self.assertEqual(len(response.data), 1)

    def test_delete_message(self):
        self.client.post(
            message_url, self.message_data, format="json"
        )
        response = self.client.get(messages_url, self.pos1_param)
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
        pos_param = {"latitude": self.pos2.y, "longitude": self.pos2.x}
        pos_data = {"location": pos_param}
        self.client.post(position_url, pos_data, format="json")
        response = self.client.get(messages_url, pos_param)
        logger.debug("Response data: %s", response.data)
        response_messages = sorted([msg["uuid"] for msg in response.data])
        expected_messages = sorted([str(self.msg2.uuid)])
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


class RegisterTest(APITestCase):

    def setUp(self):
        self.pos_data = {
            "location": {
                "latitude": 42,
                "longitude": 127
            }
        }
        self.pos_param = self.pos_data["location"]

    def test_register_invalid(self):
        data = {"username": "toto"}
        response = self.client.post(register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(register_url, self.pos_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register(self):
        data = {"username": "toto", **self.pos_data}
        response = self.client.post(
            register_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "token")
        self.assertContains(response, "user_id")

    def test_register_duplicate(self):
        data = {"username": "toto", **self.pos_data}
        self.client.post(
            register_url, data, format="json"
        )
        response = self.client.post(
            register_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
