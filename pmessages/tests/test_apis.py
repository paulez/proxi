from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

login_url = reverse("pmessages:api-login")
logout_url = reverse("pmessages:api-logout")
message_url = reverse("pmessages:api-message")
messages_url = reverse("pmessages:api-messages")
position_url = reverse("pmessages:api-position")

class UserTests(APITestCase):

    def test_login_without_position(self):
        data = {"username": "toto"}
        response = self.client.post(login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_logout(self):
        data = {"latitude": 42, "longitude": 127}
        response = self.client.post(
            reverse("pmessages:api-position"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(reverse("pmessages:api-user"))
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

        response = self.client.get(reverse("pmessages:api-user"))
        self.assertEqual(response.data, {"username": "toto"})

        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # can't logout twice
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MessageTests(APITestCase):
    
    def setUp(self):
        self.message_data = {"message": "plop le monde"}

    def test_post_message_without_login(self):
        response = self.client.post(
            message_url, self.message_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_messages_no_position(self):
        response = self.client.get(messages_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class MessageTestsWithLoginAndPosition(APITestCase):
    def setUp(self):
        self.message_data = {"message": "plop le monde"}

        data = {"latitude": 42, "longitude": 127}
        response = self.client.post(position_url, data, format="json")

        data = {"username": "toto"}
        self.client.post(login_url, data, format="json")
        
    def tearDown(self):
        self.client.post(logout_url)

    def test_post_message_success(self): 
        response = self.client.post(
            message_url, self.message_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
