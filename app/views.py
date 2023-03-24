import os
import json

from django.shortcuts import render, redirect
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes

from app.controllers import SallaOAuth, SallaMerchantReader, ChatGPT, ChatGPTProductPromptGenerator
from app.exceptions import SallaOauthFailedException
from app.models import Account, UserPrompt, ChatGPTLog, SallaUser
from app.utils import set_cookie
from app.enums import CookieKeys
from app.authentication import TokenAuthSupportCookie
from app.serializers import ProductGetDescriptionPOSTBodySerializer


def get_products() -> list:
    with open('./debug/3-products-list.json', encoding='utf8') as f:
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


class ProductGetDescriptionAPI(APIView):
    post_body_serializer = ProductGetDescriptionPOSTBodySerializer
    prompt_type = ChatGPTProductPromptGenerator.Types.DESCRIPTION

    def get_data(self, request) -> dict:
        serializer = self.post_body_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        # it will be useful for differentiating between different prompts
        data.update({'prompt_type': self.prompt_type})
        return data

    def ask_chat_gpt(self, data: dict) -> ChatGPTLog:
        prompt_generator = ChatGPTProductPromptGenerator(data)
        description_prompt = prompt_generator.ask_for_description()

        chat_gpt = ChatGPT().ask(description_prompt)
        return chat_gpt

    def check_in_database(self, user: SallaUser, data: dict) -> ChatGPTLog:
        user_prompts_qs = user.prompts.filter(
            meta__product_id=data['product_id'],
            meta__prompt_type=data['prompt_type'],
        )

        chat_gpt = None
        if user_prompts_qs.exists():
            chat_gpt = user_prompts_qs.first().chat_gpt_log

        return chat_gpt

    def post(self, request):
        # check if user already asked for this product
        data = self.get_data(request)
        chat_gpt = self.ask_chat_gpt(data)
        UserPrompt.objects.create(user=request.user, chat_gpt_log=chat_gpt, meta=data)

        return  Response({'description': chat_gpt.answer})

