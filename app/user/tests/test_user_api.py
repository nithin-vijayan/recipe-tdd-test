from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test public Users apis"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload"""
        payload = {
            'email': 'testuser@app.com',
            'password': 'userpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exist fails"""
        payload = {
            'email': 'testuser@app.com',
            'password': 'userpass',
            'name': 'Test name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test the password is more than 5 char"""
        payload = {
            'email': 'testuser@app.com',
            'password': 'pw',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exist)

    def test_create_toke_for_user(self):
        """Test token is created for user"""
        payload = {
            'email': 'testuser@app.com',
            'password': 'password',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_toke_invalid_credentials(self):
        """Test that token is not creatd if invalid creds are given"""
        payload = {
            'email': 'testuser@app.com',
            'password': 'password',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, {
            'email': 'testuser@app.com',
            'password': 'wrong',
        })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test create tolen deosnt work for non existing user"""
        payload = {
            'email': 'testuser@app.com',
            'password': 'password',
        }
        res = self.client.post(TOKEN_URL, **payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test create tolen deosnt work for non existing user"""
        res = self.client.post(TOKEN_URL, {
            'email': 'testuser@app.com',
            'password': '',
        })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
