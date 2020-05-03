from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAG_URL = reverse('recipe:tag-list')


class PulicTagApiTest(TestCase):
    """Test public tag api endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for tags"""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPiTest(TestCase):
    """Test tags private api endpoints"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@app.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_user(self):
        """Test tags are limited to current user"""
        user2 = get_user_model().objects.create_user(
            'otheruser@app.com',
            'othpass'
        )
        Tag.objects.create(user=user2, name='Vegan')
        tag = Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAG_URL, payload)

        exist = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exist)

    def test_create_tag_invalid(self):
        """Test creating tag iwth invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tag_assigned_only(self):
        """Test tag returns assigned only if specified"""
        recipe = Recipe.objects.create(
            title='Chicken Tikka',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        tag1 = Tag.objects.create(user=self.user, name='Non Veg')
        tag2 = Tag.objects.create(user=self.user, name='Veg')
        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertNotIn(serializer2.data, res.data)
        self.assertIn(serializer1.data, res.data)

    def test_tag_unique(self):
        """Test tag returns are unique"""
        recipe1 = Recipe.objects.create(
            title='Chicken Tikka',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Chicken Masala',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        tag1 = Tag.objects.create(user=self.user, name='Non Veg')
        Tag.objects.create(user=self.user, name='Veg')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)

        self.assertEqual(len(res.data), 1)
        self.assertIn(serializer1.data, res.data)
