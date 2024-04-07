#fairs/tests/test_locations.views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from fairs.models import Location

User = get_user_model()

class LocationCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test data, if needed
        pass

    def setUp(self):
        # Create a test user with necessary permissions
        self.user = User.objects.create(username='f.dagg@example.com', email='f.dagg@example.com', first_name= 'Fred',
                                              last_name= 'Dagg', phone='0272441253')
        self.user.set_password('12345')
        self.user.save()

        # Get the content type for the Location model
        content_type = ContentType.objects.get_for_model(Location)

        # Get the permission object
        add_permission = Permission.objects.get(content_type=content_type, codename='add_location')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_location')

        # Add the permission to the user
        self.user.user_permissions.add(add_permission)
        self.user.user_permissions.add(view_permission)

        self.client = Client()

    def test_location_create_submit(self):
        # Log in the test user`
        self.client.login(username='f.dagg@example.com', email='f.dagg@example.com', password='12345')

        # Now try accessing the create location page again
        self.response = self.client.get(reverse('fair:location-create'))
        self.assertEqual(self.response.status_code, 200)

        # Submit the form
        data = {'location_name': 'Test Location'}
        self.response = self.client.post(reverse('fair:location-create'), data)
        self.assertEqual(self.response.status_code, 302)  # Redirect status
        self.assertRedirects(self.response, reverse('fair:location-list'))
        self.assertTrue(Location.objects.filter(location_name='Test Location').exists())

    def test_permission_required(self):
        # Logout and test access
        self.unauthorised_user = User.objects.create(username='J.Doe@example.com', email='J.Doe@example.com',
                                                  first_name= 'Joe', last_name= 'Doe', phone='0272441000')
        self.unauthorised_user.set_password('54321')
        self.unauthorised_user.save()
        self.client.login(username='J.Doe@example.com', email='J.Doe@example.com', password='54321')
        self.response = self.client.get(reverse('fair:location-create'))
        self.assertEqual(self.response.status_code, 403)  # Forbidden status


