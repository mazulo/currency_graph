from django.core.urlresolvers import reverse_lazy as r
from django.test import TestCase


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
