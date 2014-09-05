from django.db import models
from django.core.urlresolvers import reverse

from bitcash.settings import BASE_URL

from utils import uri_to_url


class BlogPost(models.Model):
    title = models.CharField(max_length=100, unique=True, blank=False, null=False, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, blank=False, null=False, db_index=True)
    body = models.TextField(blank=False, null=False)
    posted_at = models.DateField(db_index=True, auto_now_add=True)
    category = models.ForeignKey('blog.Category', blank=True, null=True)

    def __unicode__(self):
        return '%s' % self.title

    def get_uri(self):
        return reverse('view_blog_post', None, {self.slug})

    def get_url(self):
        return uri_to_url(BASE_URL, self.get_uri())


class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    def __unicode__(self):
        return '%s' % self.title

    def get_uri(self):
        return reverse('view_blog_category', None, {self.slug})

    def get_url(self):
        return uri_to_url(BASE_URL, self.get_uri())
