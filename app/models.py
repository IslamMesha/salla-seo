import time

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import check_password

from app import utils
from app import managers


class SallaUser(AbstractBaseUser):
    # TODO in callback check if user exists using the salla_id
    salla_id = models.CharField(max_length=64, unique=True, db_index=True)

    name = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    mobile = models.CharField(max_length=32, blank=True, null=True)
    role = models.CharField(max_length=16, default='user')

    is_active = models.BooleanField(default=True)
    is_merchant = models.BooleanField(default=False)

    merchant = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'salla_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.salla_id

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.is_merchant = self.salla_id == self.merchant.get('id')

        return super().save(*args, **kwargs)

    @classmethod
    def authenticate(cls, email, password):
        try:
            user = cls.objects.get(email=email)

            is_right_password = check_password(password, user.password)
            user = user if is_right_password else None

        except cls.DoesNotExist:
            user = None

        return user

class Account(models.Model):
    # Send to frontend to authenticate with
    public_token = models.CharField(
        max_length=256, unique=True, editable=False, 
        db_index=True, default=utils.generate_token
    )
    user = models.OneToOneField(
        'app.SallaUser', on_delete=models.CASCADE, related_name='account',
        # because account is created before user
        blank=True, null=True
    )

    # Comes from Salla
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    expires_in = models.PositiveSmallIntegerField(default=utils.next_two_weeks)
    scope = models.CharField(max_length=1024)
    token_type = models.CharField(max_length=16)

    # Times
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # before get the account check if it's alive
    objects = managers.AccountManager()

    def save(self, *args, **kwargs):
        if self.token_type:
            self.token_type = self.token_type.title()

        return super().save(*args, **kwargs)

    @classmethod
    def store(cls, data, instance=None):
        data.pop('expires_in', None) # its not accurate

        if instance:
            instance.access_token = data.get('access_token')
            instance.refresh_token = data.get('refresh_token')
            instance.scope = data.get('scope')
            instance.token_type = data.get('token_type')
            instance.expires_in = utils.next_two_weeks()
        else:
            instance = cls(**data)

        instance.save()
        return instance

    @property
    def is_alive(self) -> bool:
        return self.expires_in > int(time.time())

    def refresh_access_token(self) -> bool:
        from app.controllers import SallaOAuth

        data = SallaOAuth().refresh_access_token(self.refresh_token)
        self.store(data, self)

        return True

    def get_homepage_context(self, params: dict ={}) -> dict:
        from app.controllers import SallaMerchantReader
        from SiteServe.models import StaticPage

        products = SallaMerchantReader(self).get_products(params)
        context = {
            'user': self.user,
            'products': products['data'],
            'pagination': products['pagination'],
            'is_authenticated': True,
            'nav_pages': StaticPage.get_nav_pages()
        }

        return context

    def __str__(self):
        return self.public_token


class SallaStore(models.Model):
    user = models.OneToOneField(SallaUser, on_delete=models.CASCADE, related_name='store')
    salla_id = models.CharField(max_length=64, unique=True)

    name = models.CharField(max_length=128, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    avatar = models.URLField(max_length=512, blank=True, null=True)
    plan = models.CharField(max_length=32, blank=True, null=True)
    status = models.CharField(max_length=32, blank=True, null=True)
    verified = models.BooleanField(default=True)
    currency = models.CharField(max_length=16, blank=True, null=True)
    domain = models.URLField(max_length=512, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    licenses = models.JSONField(default=dict)
    social = models.JSONField(default=dict)

    # Times
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.salla_id


class ChatGPTLog(models.Model):
    prompt = models.CharField(max_length=512)
    total_tokens = models.PositiveSmallIntegerField(default=0)
    answer = models.TextField()

    full_response = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.prompt


class UserPrompt(models.Model):
    user = models.ForeignKey(
        SallaUser, on_delete=models.CASCADE, related_name='prompts'
    )
    chat_gpt_log = models.OneToOneField(
        'app.ChatGPTLog', on_delete=models.CASCADE, related_name='user_prompt'
    )
    # it may contain data about the product user asked about
    meta = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user }: {self.chat_gpt_log.prompt}'


class SallaWebhookLog(models.Model):
    event = models.CharField(max_length=128)
    merchant_id = models.CharField(max_length=64)
    data = models.JSONField(default=dict)
    response = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = self.response.get('status', 'unknown')
        emoji = '✅' if status == 'success' else '❌'
        return f'{emoji} {self.event} - {self.merchant_id}'



