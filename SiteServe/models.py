from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.shortcuts import reverse

from markdown import markdown


def NAV_ORDERING_CALCULATOR():
    return (StaticPage.objects.filter(is_nav=True).count() + 1) * 10


class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)

    md = models.TextField(blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    head = models.TextField(blank=True, null=True)
    custom_css = models.TextField(blank=True, null=True)
    custom_js = models.TextField(blank=True, null=True)

    is_nav = models.BooleanField(default=False)
    nav_name = models.CharField(max_length=200, blank=True, null=True)
    nav_ordering = models.PositiveSmallIntegerField(default=NAV_ORDERING_CALCULATOR)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.nav_name:
            self.nav_name = self.title

        if not self.slug:
            self.slug = slugify(self.title)

        if self.html is None and self.md is None:
            raise ValidationError('Either html or md must be set')

        super().save(*args, **kwargs)

    @property
    def body(self):
        html = self.html or markdown(self.md)
        return html

    @property
    def url(self):
        return reverse('site_serve:page', args=(self.slug,))

    @classmethod
    def get_nav_pages(cls):
        from SiteServe.serializers import StaticPageNavPagesSerializer

        qs = cls.objects.filter(is_nav=True)
        return StaticPageNavPagesSerializer(qs, many=True).data

    class Meta:
        ordering = ('nav_ordering', 'slug',)


