import json

from django.conf import settings
from django.core import serializers
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


class CurrenciesCreate(TestCase):

    def setUp(self):

        self.base = 'USD'
        self.symbol_target = 'BRL'
        self.list_api_response = {
            'responses': [
                {
                    'base': 'USD',
                    'date': '2016-11-23',
                    'rates': {
                        'BRL': 3.4548
                    }
                },
                {
                    'base': 'USD',
                    'date': '2016-11-24',
                    'rates': {
                        'BRL': 3.4748
                    }
                },
                {
                    'base': 'USD',
                    'date': '2016-11-25',
                    'rates': {
                        'BRL': 3.3048
                    }
                },
                {
                    'base': 'USD',
                    'date': '2016-11-26',
                    'rates': {
                        'BRL': 3.5048
                    }
                },
                {
                    'base': 'USD',
                    'date': '2016-11-27',
                    'rates': {
                        'BRL': 3.6048
                    }
                },
                {
                    'base': 'USD',
                    'date': '2016-11-28',
                    'rates': {
                        'BRL': 3.5648
                    }
                },
                {
                    'base': 'USD',
                    'date': '2016-11-29',
                    'rates': {
                        'BRL': 3.7048
                    }
                },
            ],
        }

    def _validate_output(self, to_serialize):
        try:
            json.dumps(to_serialize)
        except Exception:
            return False
        else:
            return True

    def _create_currencies(self):
        currencies = []

        for response in self.list_api_response['responses']:
            currencies.append(
                Currency(
                    date=response['date'],
                    base=self.base,
                    symbol_target=self.symbol_target,
                    value=response['rates']['BRL'],
                )
            )
        return Currency.objects.bulk_create(currencies)

    def test_create_currencies(self):
        currencies = self._create_currencies()

        self.assertEqual(len(currencies), 7)

    def test_serialize_currencies(self):
        self._create_currencies()

        to_serialize = serializers.serialize(
            'json',
            Currency.objects.all(),
            fields=('date', 'value'),
        )

        self.assertTrue(self._validate_output(to_serialize))
