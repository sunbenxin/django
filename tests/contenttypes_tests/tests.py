from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.loading import BaseAppCache
from django.test import TestCase

from .models import Author, Article


class ContentTypesViewsTests(TestCase):
    fixtures = ['testdata.json']
    urls = 'contenttypes_tests.urls'

    def test_shortcut_with_absolute_url(self):
        "Can view a shortcut for an Author object that has a get_absolute_url method"
        for obj in Author.objects.all():
            short_url = '/shortcut/%s/%s/' % (ContentType.objects.get_for_model(Author).id, obj.pk)
            response = self.client.get(short_url)
            self.assertRedirects(response, 'http://testserver%s' % obj.get_absolute_url(),
                                 status_code=302, target_status_code=404)

    def test_shortcut_no_absolute_url(self):
        "Shortcuts for an object that has no get_absolute_url method raises 404"
        for obj in Article.objects.all():
            short_url = '/shortcut/%s/%s/' % (ContentType.objects.get_for_model(Article).id, obj.pk)
            response = self.client.get(short_url)
            self.assertEqual(response.status_code, 404)

    def test_wrong_type_pk(self):
        short_url = '/shortcut/%s/%s/' % (ContentType.objects.get_for_model(Author).id, 'nobody/expects')
        response = self.client.get(short_url)
        self.assertEqual(response.status_code, 404)

    def test_shortcut_bad_pk(self):
        short_url = '/shortcut/%s/%s/' % (ContentType.objects.get_for_model(Author).id, '42424242')
        response = self.client.get(short_url)
        self.assertEqual(response.status_code, 404)

    def test_nonint_content_type(self):
        an_author = Author.objects.all()[0]
        short_url = '/shortcut/%s/%s/' % ('spam', an_author.pk)
        response = self.client.get(short_url)
        self.assertEqual(response.status_code, 404)

    def test_bad_content_type(self):
        an_author = Author.objects.all()[0]
        short_url = '/shortcut/%s/%s/' % (42424242, an_author.pk)
        response = self.client.get(short_url)
        self.assertEqual(response.status_code, 404)

    def test_create_contenttype_on_the_spot(self):
        """
        Make sure ContentTypeManager.get_for_model creates the corresponding
        content type if it doesn't exist in the database (for some reason).
        """

        class ModelCreatedOnTheFly(models.Model):
            name = models.CharField()

            class Meta:
                verbose_name = 'a model created on the fly'
                app_label = 'my_great_app'
                app_cache = BaseAppCache()

        ct = ContentType.objects.get_for_model(ModelCreatedOnTheFly)
        self.assertEqual(ct.app_label, 'my_great_app')
        self.assertEqual(ct.model, 'modelcreatedonthefly')
        self.assertEqual(ct.name, 'a model created on the fly')
