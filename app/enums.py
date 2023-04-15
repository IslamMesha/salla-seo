from enum import Enum

class CookieKeys(Enum):
    # hold names of the cookies
    AUTH_TOKEN = 'auth_token'


class WebhookEvents(Enum):
    # hold names of the webhook events
    AUTHORIZED = 'app.store.authorize'
    SETTINGS_UPDATED = 'app.settings.updated'

