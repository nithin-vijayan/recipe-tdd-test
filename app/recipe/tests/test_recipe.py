from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
import tempfile
import os


RECIPE_URL = reverse('recipe:recipe-list')


def image_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=(recipe_id,))


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=(recipe_id,))


def sample_tag(user, name='sampletag'):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Salt'):
    return Ingredient.objects.create(user=user, name=name)


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
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Choclate Lava',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_withTags(self):
        """Test creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        payload = {
            'title': 'Choc cake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_withIngredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Salt')
        ingredient2 = sample_ingredient(user=self.user, name='Eggs')

        payload = {
            'title': 'Myonaisse',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 10,
            'price': 25.00
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)

        payload = {
            'title': 'Mint Lime',
            'tags': [tag.id]
        }
        self.client.patch(detail_url(recipe.id), payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(len(tags), 1)
        self.assertIn(tag, tags)

    def test_complete_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        recipe.tags.add(tag)

        payload = {
            'title': 'Juice',
            'price': 20.00,
            'time_minutes': 10,
        }

        self.client.put(detail_url(recipe.id), payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(len(tags), 0)


class ImageApiTest(TestCase):
    """Test image upload apis"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@email.com', 'password'
            )
        self.client.force_authenticate(user=self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_image_upload_valid(self):
        """Test imag upload with valid payload"""
        url = image_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as fil:
            img = Image.new('RGB', (10, 10))
            img.save(fil, format='JPEG')
            fil.seek(0)
            res = self.client.post(url, {'image': fil}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image(self):
        """Test image upload with invalid image"""
        url = image_url(self.recipe.id)
        res = self.client.post(url, {'image': 'none'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipe_by_tag(self):
        """Test recipe can be filtered by tags"""
        recipe1 = sample_recipe(user=self.user, title="Chicken Curry")
        recipe2 = sample_recipe(user=self.user, title="Chicken Tikka")
        recipe3 = sample_recipe(user=self.user)
        tag1 = sample_tag(user=self.user, name='Chicken')
        tag2 = sample_tag(user=self.user, name='Curry')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(RECIPE_URL, {'tags': f'{tag1.id},{tag2.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipe_by_ingredients(self):
        """Filter recipes by ingredients"""
        recipe1 = sample_recipe(user=self.user, title='Chicken Curry')
        recipe2 = sample_recipe(user=self.user, title='Chicken Tkikka')
        recipe3 = sample_recipe(user=self.user)
        ingredient1 = sample_ingredient(user=self.user, name='Chicken')
        ingredient2 = sample_ingredient(user=self.user, name='Masala')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
            )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
