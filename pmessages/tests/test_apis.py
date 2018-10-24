from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class UserTests(APITestCase):

    def test_login_without_position(self):
        data = {"username": "toto"}
        response = self.client.post(reverse("pmessages:api-login"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_logout(self):
        data = {"latitude": 42, "longitude": 127}
        response = self.client.post(
            reverse("pmessages:api-position"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        data = {"username": "toto"}
        response = self.client.post(
            reverse("pmessages:api-login"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        response = self.client.get(reverse("pmessages:api-user"))
        self.assertEqual(response.data, {"username": "toto"})

        response = self.client.post(
            reverse("pmessages:api-logout"))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # can't logout twice
        response = self.client.post(
            reverse("pmessages:api-logout"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

