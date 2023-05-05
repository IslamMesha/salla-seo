import os
from django.db.models import Manager


class AccountManager(Manager):
    def get(self, *args, **kwargs):
        obj = super().get(*args, **kwargs)

        is_local = os.getenv('IS_LOCAL', False) == 'True'
        is_production = not is_local

        if is_production and not obj.is_alive:
            obj.refresh_access_token()

        return obj

