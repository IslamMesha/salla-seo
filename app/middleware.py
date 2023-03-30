from django.http import HttpResponse
from django.shortcuts import redirect

from rest_framework.exceptions import AuthenticationFailed

from app.enums import CookieKeys


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except AuthenticationFailed as e:
            response = redirect('app:index')
            response.delete_cookie(CookieKeys.AUTH_TOKEN.value)

        return response
