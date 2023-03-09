from django.utils.translation import gettext_lazy as _

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from app.models import Account


class TokenAuthSupportCookie(TokenAuthentication):
    """
    Extend the TokenAuthentication class to support cookie based authentication
    """
    model = Account

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(public_token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate(self, request):
        is_auth_by_header = 'HTTP_AUTHORIZATION' in request.META
        is_auth_by_cookie = 'auth_token' in request.COOKIES

        result = None
        if is_auth_by_header:
            result = super().authenticate(request)
        if is_auth_by_cookie:
            token = request.COOKIES.get('auth_token')
            result = self.authenticate_credentials(token)

        return result
