import os

from django.shortcuts import render, redirect
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response

from app.controllers import SallaOAuth
from app.exceptions import SallaOauthFailedException
from app.models import Account
from app.utils import set_cookie


def index(request):
    app_id = os.environ.get('SALLA_APP_ID')
    context = {
        'installation_url': f'https://s.salla.sa/apps/install/{app_id}',
    }
    print(Account.objects.filter(public_token=request.COOKIES.get('auth_token')))
    return render(request, 'index.html', context=context)


def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        messages.success(request, 'Login Success.')
        data = SallaOAuth().get_access_token(code)
        account = Account.store(data)
        response = redirect('app:index')
        
        set_cookie(response, 'auth_token', account.public_token, max_age=60 * 60 * 24 * 14)
    else:
        raise SallaOauthFailedException()

    return response

class Test(APIView):
    def get(self, request):
        return Response({'message': 'Hello World!'})

