from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Intgredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=(recipe_id,))


def sample_tag(user, name='sampletag'):
    return Tag.objects.create(user=user, name=name)


def sample_intgredient(user, name='Salt'):
    return Intgredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sampel recipe"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPiTest(TestCase):
    """Test unauth recipe api access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for requests"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test authenticated recipe access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@app.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_for_user(self):
        """Test retrieve works for specific user"""
        user2 = get_user_model().objects.create_user(
            'user2@app.com',
            'passw2'
        )
        sample_recipe(user=user2)
        recipe = sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.intgredients.add(sample_intgredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
