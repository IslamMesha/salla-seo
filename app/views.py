import os
import logging

from django.shortcuts import render, redirect
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import MethodNotAllowed

from app.controllers import SallaOAuth, SallaMerchantReader, ChatGPT, ChatGPTProductPromptGenerator, SallaWriter, SallaWebhook
from app.exceptions import SallaOauthFailedException, SallaEndpointFailureException
from app.models import Account, UserPrompt, ChatGPTLog, SallaUser
from app.utils import set_cookie, validate_email_and_password
from app.enums import CookieKeys
from app import serializers

logger = logging.getLogger('main')


class Index(APIView):
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        from SiteServe.models import StaticPage

        app_id = os.environ.get('SALLA_APP_ID')
        context = {
            'installation_url': f'https://s.salla.sa/apps/install/{app_id}',
            'is_authenticated': False,
            'nav_pages': StaticPage.get_nav_pages()
        }

        if request.user.is_authenticated and hasattr(request.user, 'account'):
            context = request.user.account.get_homepage_context(request.GET)

        return Response(context, template_name='index.html')


class Login(APIView):
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    post_body_serializer = serializers.LoginPOSTBodySerializer

    def get_data(self, request) -> dict:
        serializer = self.post_body_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return data

    def post(self, request):
        data = self.get_data(request)
        user = SallaUser.authenticate(**data)

        if user:
            response = redirect('app:index')

            month = 60 * 60 * 24 * 30
            set_cookie(response, CookieKeys.AUTH_TOKEN.value, user.account.public_token, max_age=month)

        else:
            messages.error(request, 'Invalid email or password.')
            response = redirect('app:index')
            response.delete_cookie(CookieKeys.AUTH_TOKEN.value)

        return response


class Logout(APIView):
    permission_classes = []
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        response = redirect('app:index')
        response.delete_cookie(CookieKeys.AUTH_TOKEN.value)

        return response


def oauth_callback(request):
    code = request.GET.get('code')
    if code:
        messages.success(request, 'Login Success.')

        base_url = request.build_absolute_uri('/')
        data = SallaOAuth(base_url).get_access_token(code)
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


class AskGPTAboutProductAPI(APIView):
    post_body_serializer = serializers.ProductGetDescriptionPOSTBodySerializer

    def get_data(self, request) -> dict:
        serializer = self.post_body_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return data

    def ask_chat_gpt(self, data: dict) -> ChatGPTLog:
        prompt_generator = ChatGPTProductPromptGenerator(data)
        chat_gpt = ChatGPT().ask(prompt_generator.get_prompt())
        return chat_gpt

    def post(self, request):
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


class ProductListHistoryAPI(ListAPIView):
    serializer_class = serializers.UserPromptSerializer
    post_body_serializer = serializers.ProductListHistoryPOSTBodySerializer

    def get_data(self, request) -> dict:
        serializer = self.post_body_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        return data

    def get_queryset(self):
        data = self.get_data(self.request)
        product_id = data['product_id']
        prompt_type = data['prompt_type']

        qs = (
            self.request.user.prompts
                .filter(meta__prompt_type=prompt_type, meta__product_id=product_id)
        )
        return qs.order_by('-id')

    def get(self, request):
        raise MethodNotAllowed('GET')

    def post(self, request):
        return self.list(request)


class WebhookAPI(APIView):
    permission_classes = []

    def post(self, request):
        response, status_code = SallaWebhook(request.data).process()
        return Response(response, status=status_code)


from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password


class SettingsValidationAPI(APIView):
    permission_classes = []

    def extract_data(self, payload) -> dict:
        data = payload.get('data') or payload
        settings = data.get('settings') or data

        return settings.get('email'), settings.get('password')

    def post(self, request):
        email, password = self.extract_data(request.data)

        if email is None or password is None:
            logger.error(f'[SETTINGS_VALIDATION]: {request.data}')
            raise ValidationError({'error': 'Email and password are required.'})

        is_valid = validate_email_and_password(email, password)

        status, status_code = ('success', 200) if is_valid else ('error', 400)
        response = {'status': status}

        return Response(response, status=status_code)


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

