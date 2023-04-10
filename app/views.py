import os

from django.shortcuts import render, redirect
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler as drf_exception_handler

from app.controllers import SallaOAuth, SallaMerchantReader, ChatGPT, ChatGPTProductPromptGenerator, SallaWriter
from app.exceptions import SallaOauthFailedException, SallaEndpointFailureException
from app.models import Account, UserPrompt, ChatGPTLog, SallaUser
from app.utils import set_cookie
from app.enums import CookieKeys
from app import serializers



class Index(APIView):
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        app_id = os.environ.get('SALLA_APP_ID')
        context = {
            'installation_url': f'https://s.salla.sa/apps/install/{app_id}',
            'is_authenticated': False,
        }

        if request.user.is_authenticated and hasattr(request.user, 'account'):
            context = request.user.account.get_homepage_context(request.GET)

        return Response(context, template_name='index.html')


def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        messages.success(request, 'Login Success.')
        data = SallaOAuth().get_access_token(code)
        account = Account.store(data)
        response = render(request, 'index.html', account.get_homepage_context())

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
    post_body_serializer = serializers.ProductGetDescriptionPOSTBodySerializer
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

        return Response({'description': chat_gpt.answer})


class ProductUpdateAPI(APIView):
    post_body_serializer = serializers.ProductUpdatePOSTBodySerializer

    def get_data(self, request) -> dict:
        serializer = self.post_body_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return data

    def post(self, request, product_id):
        account = request.user.account
        body = self.get_data(request)

        writer = SallaWriter(account)
        response_data = writer.product_update(product_id, body)

        return Response(response_data)


class ProductListDescriptionsAPI(ListAPIView):
    prompt_type = ChatGPTProductPromptGenerator.Types.DESCRIPTION
    serializer_class = serializers.UserPromptSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return (
            self.request.user
                .prompts
                .filter(
                    meta__prompt_type=self.prompt_type,
                    meta__product_id=product_id,
                )
                .order_by('-id')
        )


def exception_handler(exc, context):
    auth_exceptions = (
        SallaOauthFailedException, SallaEndpointFailureException,
        AuthenticationFailed
    )

    if any([isinstance(exc, e) for e in auth_exceptions]):
        response = redirect('app:index')
        response.delete_cookie(CookieKeys.AUTH_TOKEN.value)
    else:
        response = drf_exception_handler(exc, context)

    return response