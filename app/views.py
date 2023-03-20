import os
import json

from django.shortcuts import render, redirect
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes

from app.controllers import SallaOAuth, SallaMerchantReader
from app.exceptions import SallaOauthFailedException
from app.models import Account
from app.utils import set_cookie
from app.enums import CookieKeys
from app.authentication import TokenAuthSupportCookie


def get_products() -> list:
    with open('./debug/3-products-list.json') as f:
        products = json.load(f)

    return products['data']

@authentication_classes([TokenAuthSupportCookie])
def index(request):
    app_id = os.environ.get('SALLA_APP_ID')
    context = {
        'installation_url': f'https://s.salla.sa/apps/install/{app_id}',
        'user': request.user,
        'products': get_products(),
    }

    print(request.user.is_authenticated and request.user)
    return render(request, 'index.html', context=context)


def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        messages.success(request, 'Login Success.')
        data = SallaOAuth().get_access_token(code)
        account = Account.store(data)
        response = redirect('app:index')
        
        month = 60 * 60 * 24 * 30
        set_cookie(response, CookieKeys.AUTH_TOKEN.value, account.public_token, max_age=month)
    else:
        raise SallaOauthFailedException()

    return response

class Test(APIView):
    def get(self, request):
        return Response({'message': 'Hello World!'})

class ProductsListAPI(ListAPIView):
    def get(self, request):
        params = request.GET

        account = request.user.account
        products = SallaMerchantReader(account).get_products(params)

        return Response(products)

