import time

from django.db import models
from django.contrib.auth.models import User

from app import utils
from app import managers
from app.controllers import SallaOAuth


class Account(models.Model):
    # Send to frontend to authenticate with
    public_token = models.CharField(
        max_length=256, unique=True, editable=False, 
        db_index=True, default=utils.generate_token
    )
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        User, related_name='auth_token', on_delete=models.CASCADE,
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

        # user so authentication works properly 
        if self.user is None:
            self.user = User.objects.create_user(
                username=utils.generate_random_username(),
            )

        return super().save(*args, **kwargs)

    @classmethod
    def store(cls, data, instance=None):
        data.pop('expires_in', None) # its not accurate

        if instance:
            instance.access_token = data.get('access_token')
            instance.refresh_token = data.get('refresh_token')
            instance.scope = data.get('scope')
            instance.token_type = data.get('token_type')
        else:
            instance = cls(**data)

        return instance.save()

    @property
    def is_alive(self):
        return self.expires_in > int(time.time())

    def refresh_access_token(self):
        data = SallaOAuth().refresh_access_token(self.refresh_token)
        self.store(data, self)

        return True

    def __str__(self):
        return self.public_token
