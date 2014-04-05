from django.test import TestCase
from django.test.client import RequestFactory
from bambu.buffer.views import auth

class AuthorisationTestCase(TestCase):
    def setUp(self):
        self.client = RequestFactory()

    def test_authorisation(self):
        request = self.client.get('/buffer/auth/')
        response = auth(request)
        response
