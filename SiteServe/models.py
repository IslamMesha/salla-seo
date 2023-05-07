from markdown import markdown
import re

from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.shortcuts import reverse


def NAV_ORDERING_CALCULATOR():
    return (StaticPage.objects.filter(is_nav=True).count() + 1) * 10

def CHATGPT_PROMPT_TYPES():
    from app.controllers import ChatGPTProductPromptGenerator
    from app.utils import list_to_choices

    types = ChatGPTProductPromptGenerator.get_prompt_types()
    return list_to_choices(types)

def CHATGPT_PROMPT_LANGUAGES():
    from app.utils import list_to_choices
    return list_to_choices(['ar', 'en',])

def ALLOWED_TEMPLATE_LABELS():
    from app.utils import readable_list
    labels = [
        '{product_name}',
        '{product_description}',
        '{product_seo_title}',
        '{keywords}',
        '{brand_name}',
    ]
    return readable_list(labels, 'or')


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


class ChatGPTPromptTemplate(models.Model):
    NAME_FORMAT = 'product_{type}_{language}'

    template = models.TextField(f'Allowed labels are {ALLOWED_TEMPLATE_LABELS()} || Keep in mind the DEPENDENCIES when choose the labels.')
    type = models.CharField(max_length=32, choices=CHATGPT_PROMPT_TYPES())
    language = models.CharField(max_length=2, choices=CHATGPT_PROMPT_LANGUAGES())
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs) -> None:
        is_created = self.pk is None
        if is_created:
            qs = self.same_type_qs
            # is there is no active make this one active
            if qs.exists() and self.is_active:
                qs.update(is_active=False)
            # else make sure there is only one active
            elif not qs.exists():
                self.is_active = True

        if self.template:
            labels = re.findall(r'{(.*?)}', self.template)
            check_label = lambda label: label in ALLOWED_TEMPLATE_LABELS()
            is_all_labels_valid = all(map(check_label, labels))
            if is_all_labels_valid is False:
                raise ValidationError('One or more labels are not allowed')

        return super().save(*args, **kwargs)

    @property
    def same_type_qs(self):
        return self.__class__.objects.filter(type=self.type, language=self.language)

    @property
    def name(self):
        return self.NAME_FORMAT.format(
            type=self.type, language=self.language
        ).upper()

    @classmethod
    def get_prompts(cls) -> dict:
        DEFAULT_PROMPTS = {
            'PRODUCT_DESCRIPTION_EN': 'write a brief about product {product_name}, using these keywords: {keywords}',
            'PRODUCT_DESCRIPTION_AR': 'اكتب ملخصاً قصير عن منتج أسمه: {product_name}, باستخدام تلك الكلمات المفتاحية: {keywords}',
        }

        db_prompts = {
            prompt.name: prompt.template
            for prompt in cls.objects.filter(is_active=True)
        }

        return db_prompts or DEFAULT_PROMPTS

    @classmethod
    def get_template(cls, template_name: str) -> str:
        return cls.get_prompts().get(template_name)

    def __str__(self):
        return self.name




