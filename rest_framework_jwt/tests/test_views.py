from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.compat import patterns
from rest_framework.test import APIClient

from rest_framework_jwt import utils
from rest_framework_jwt.runtests.models import CustomUser

urlpatterns = patterns(
    '',
    (r'^auth-token/$', 'rest_framework_jwt.views.obtain_jwt_token'),
)


class ObtainJSONWebTokenTests(TestCase):
    urls = 'rest_framework_jwt.tests.test_views'

    def setUp(self):
        self.email = 'jpueblo@example.com'
        self.username = 'jpueblo'
        self.password = 'password'
        self.user = User.objects.create_user(
            self.username, self.email, self.password)

        self.data = {
            'username': self.username,
            'password': self.password
        }

    def test_jwt_login_json(self):
        """
        Ensure JWT login view using JSON POST works.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/auth-token/', self.data, format='json')

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['username'], self.username)

    def test_jwt_login_json_bad_creds(self):
        """
        Ensure JWT login view using JSON POST fails
        if bad credentials are used.
        """
        client = APIClient(enforce_csrf_checks=True)

        self.data['password'] = 'wrong'
        response = client.post('/auth-token/', self.data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_json_missing_fields(self):
        """
        Ensure JWT login view using JSON POST fails if missing fields.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/auth-token/',
                               {'username': self.username}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_form(self):
        """
        Ensure JWT login view using form POST works.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/auth-token/', self.data)

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['username'], self.username)

    def test_jwt_login_with_expired_token(self):
        """
        Ensure JWT login view works even if expired token is provided
        """
        payload = utils.jwt_payload_handler(self.user)
        payload['exp'] = 1
        token = utils.jwt_encode_handler(payload)

        auth = 'JWT {0}'.format(token)
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(
            '/auth-token/', self.data,
            HTTP_AUTHORIZATION=auth, format='json')

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['username'], self.username)


class CustomUserObtainJSONWebTokenTests(TestCase):
    """JSON Web Token Authentication"""
    urls = 'rest_framework_jwt.tests.test_views'

    def setUp(self):
        # set custom user model
        self.ORIG_AUTH_USER_MODEL = settings.AUTH_USER_MODEL
        settings.AUTH_USER_MODEL = 'runtests.CustomUser'

        self.email = 'jpueblo@example.com'
        self.password = 'password'
        user = CustomUser.objects.create(email=self.email)
        user.set_password(self.password)
        user.save()
        self.user = user

        self.data = {
            'email': self.email,
            'password': self.password
        }

    def test_jwt_login_json(self):
        """
        Ensure JWT login view using JSON POST works.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/auth-token/', self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        decoded_payload = utils.jwt_decode_handler(response.data['token'])
        self.assertEqual(decoded_payload['username'], self.email)

    def test_jwt_login_json_bad_creds(self):
        """
        Ensure JWT login view using JSON POST fails
        if bad credentials are used.
        """
        client = APIClient(enforce_csrf_checks=True)

        self.data['password'] = 'wrong'
        response = client.post('/auth-token/', self.data, format='json')

        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        settings.AUTH_USER_MODEL = self.ORIG_AUTH_USER_MODEL
