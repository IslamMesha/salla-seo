from django.db.models import Manager

class AccountManager(Manager):
    def get(self, *args, **kwargs):
        obj = super().get(*args, **kwargs)

        if not obj.is_alive:
            obj.refresh_access_token()

        return obj

