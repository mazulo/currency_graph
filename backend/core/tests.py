from django.conf import settings
from django.core.urlresolvers import reverse_lazy as r
from django.utils import timezone
from django.test import TestCase

import requests
import requests_mock

from backend.core.models import Currency


class IndexTest(TestCase):

    def setUp(self):
        self.response = self.client.get(r('core:index'))

    def test_get(self):
        """GET / must return status code"""
        self.assertEqual(200, self.response.status_code)

    def test_template(self):
        """Must use index.html"""
        self.assertTemplateUsed(self.response, 'core/index.html')

    def test_speakers(self):
        """Must show keynote speakers"""
        contents = [
            'Currency graphs',
            'Dollar',
            'Euro',
        ]
        for expected in contents:
            with self.subTest():
                self.assertContains(self.response, expected)


class CurrentCurrencyCreate(TestCase):

    def setUp(self):

        self.current_date = timezone.datetime.now()
        self.base = 'USD'
        self.symbol_target = 'BRL'

        session = requests.Session()
        adapter = requests_mock.Adapter()
        response = {
            'base': 'USD',
            'date': '2016-11-29',
            'rates': {
                'BRL': 3.4048
            }
        }

        URL = settings.API_URL.format(
            base=self.base,
            date=self.current_date.isoformat()
        )

        session.mount('http://api.fixer.io/', adapter)

        adapter.register_uri('GET', URL, json=response, status_code=200)

        self.resp = session.get(URL)

    def test_api_status_code(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_create_currency(self):
        json_response = self.resp.json()

        Currency.objects.create(
            date=self.current_date,
            base=self.base,
            symbol_target=self.symbol_target,
            value=json_response['rates']['BRL']
        )

        self.assertTrue(Currency.objects.exists())
