from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from user.models import CustomUser
from user.serializers import CustomUserShortSerializer


def create_user(username, password, is_staff=False):
    user = CustomUser.objects.create_user(username=username, password=password, is_staff=is_staff)
    return user


def get_user_token(user):
    return user.auth_token.key


def authenticate_client(client, token):
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)


class CalendarTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user_data = {
            "username": "test_user",
            "password": "test_password"
        }
        self.test_user = create_user(self.test_user_data["username"], self.test_user_data["password"])

    def test_register(self):
        new_user = {
            "username": "test-username",
            "password": "test-password"
        }
        self.assertEquals(CustomUser.objects.filter(username=new_user["username"]).count(), 0)
        response = self.client.post(reverse('users-list'), data=new_user, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(CustomUser.objects.filter(username=new_user["username"]).count(), 1)
        self.assertEquals(response.data, {"token": get_user_token(CustomUser.objects.get(username=new_user["username"]))})

    def test_login(self):
        response = self.client.post(reverse('api-login'), data=self.test_user_data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {"token": get_user_token(self.test_user)})

    def test_logout(self):
        authenticate_client(self.client, get_user_token(self.test_user))
        self.assertEquals(Token.objects.filter(key=get_user_token(self.test_user)).count(), 1)
        response = self.client.post(reverse('api-logout'), format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Token.objects.filter(key=get_user_token(self.test_user)).count(), 0)

    def test_list_not_logged_in(self):
        response = self.client.get(reverse('users-list'))
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_logged_in(self):
        authenticate_client(self.client, get_user_token(self.test_user))
        create_user("test1", "test")
        user = CustomUser.objects.get(username="test1")
        users = CustomUserShortSerializer([self.test_user, user], many=True).data
        response = self.client.get(reverse('users-list'))
        self.assertEquals(response.data, users)
