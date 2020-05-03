from core import models
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


def sample_user(email='user@app.com', password='userpass'):
    """Create sample user"""
    return get_user_model().objects.create_user(
        email=email,
        password=password
    )


class ModelTestCase(TestCase):

    def test_create_user_email_success(self):
        """Test creae user with email is successful"""
        email = "test@app.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_email_normalizer(self):
        """Test user email id is normalized"""
        email = "user@aPP.com"
        user = get_user_model().objects.create_user(
            email=email, password="passw"
            )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test invalid email trhows error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            "testadmin@app.com",
            "adminpass"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string repr"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingrediants_str(self):
        """Test tag intgrediants repr"""
        intgrediants = models.Ingredient.objects.create(
            user=sample_user(),
            name='Beef'
        )
        self.assertEqual(str(intgrediants), intgrediants.name)

    def test_recipe_str(self):
        """Test recipe intgrediants repr"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and Sauce',
            price=25.00,
            time_minutes=4,
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_image_upload_file_name(self, uuid_mock):
        uuid_ = 'test-image-name'
        uuid_mock.return_value = uuid_
        uuid_filename = models.get_image_url_path(None, 'image.jpg')

        expected = f'uploads/recipe/{uuid_}.jpg'
        self.assertEqual(expected, uuid_filename)
