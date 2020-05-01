from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Intgredient
from recipe.serializers import IntgredientSerializer


INTGREDIENT_URL = reverse('recipe:intgredient-list')


class PublicIntgredientsApiTest(TestCase):
    """Test Intgrediant public api endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to list"""
        res = self.client.get(INTGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIntgredientsApiTest(TestCase):
    """Test intgredients can be retrived bu aiuth user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@app.com',
            'userpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_intgredients_list(self):
        """Test retrieving a list of intgredients"""
        Intgredient.objects.create(user=self.user, name='Kale')
        Intgredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INTGREDIENT_URL)

        intgredients = Intgredient.objects.all().order_by('-name')
        serializer = IntgredientSerializer(intgredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_intgredients_auth_user(self):
        """Test intgredients can be retireved for auth user"""
        user2 = get_user_model().objects.create_user(
            'test2@app.com',
            'userpass2'
        )
        Intgredient.objects.create(user=user2, name='Kale')
        intgredient = Intgredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INTGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], intgredient.name)

    def test_create_intgredient_success(self):
        """Test creating intgredient is success with a valid payload"""
        payload = {'name': 'Broccoli'}
        self.client.post(INTGREDIENT_URL, payload)

        exists = Intgredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_intgredient_invalid(self):
        """Test creating intgredient is fails with a invalid payload"""
        payload = {'name': ''}
        self.client.post(INTGREDIENT_URL, payload)
        res = self.client.post(INTGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
