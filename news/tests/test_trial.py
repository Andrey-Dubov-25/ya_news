from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


@skip('Пример из теории')
class TestNews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testUser')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

