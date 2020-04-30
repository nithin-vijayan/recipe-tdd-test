from core import models
from django.test import TestCase
from django.contrib.auth import get_user_model


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
