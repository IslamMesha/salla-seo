import os
import requests

from django.shortcuts import reverse

from rest_framework.serializers import Serializer

from app.exceptions import SallaOauthFailedException, SallaEndpointFailureException
from app.models import Account, ChatGPTLog, SallaUser
from app import utils
from app.enums import WebhookEvents


class SallaOAuth:
    def __init__(self, base_url:str=None) -> None:
        self.app_id = os.environ.get('SALLA_APP_ID')
        self.oauth_client_id = os.environ.get('SALLA_OAUTH_CLIENT_ID')
        self.oauth_client_secret = os.environ.get('SALLA_OAUTH_CLIENT_SECRET')
        self.base_url = base_url

    @property
    def redirect_uri(self):
        if self.base_url is None:
            uri = os.environ.get('SALLA_OAUTH_CLIENT_REDIRECT_URI')
        else:
            uri = self.base_url.rstrip('/') + reverse('app:oauth_callback')

        return uri

    def get_installation_url(self):
        return f'https://s.salla.sa/apps/install/{self.app_id}'

    def __get_body(self) -> dict:
        return {
            'client_id': self.oauth_client_id,
            'client_secret': self.oauth_client_secret,
            'redirect_uri': self.redirect_uri
        }

    def __get_headers(self) -> dict:
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def get_access_token(self, code: str) -> dict:
        url = 'https://accounts.salla.sa/oauth2/token'
        body = self.__get_body()
        headers = self.__get_headers()
        
        body.update({
            'grant_type': 'authorization_code',
            'code': code,
            'scope': 'offline_access',
        })

        response = requests.post(url, data=body, headers=headers)

        if response.status_code != 200:
            raise SallaOauthFailedException()

        return response.json()

    def refresh_access_token(self, refresh_token: str) -> dict:
        url = 'https://accounts.salla.sa/oauth2/token'
        body = self.__get_body()
        headers = self.__get_headers()
        
        body.update({
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        })

        response = requests.post(url, data=body, headers=headers)

        if response.status_code != 200:
            raise SallaOauthFailedException()

        return response.json()


class SallaBaseReader:
    """Base class for Salla API readers
    because there there are endpoints 
    read about merchant
    others read about settings
    """
    def __init__(self, account: Account) -> None:
        self.access_token = account.access_token
        self.base_url = os.getenv('SALLA_BASE_URL')

    def get_headers(self) -> dict:
        return { 'Authorization': f'Bearer {self.access_token}' }

    def get_params(self, serializer: Serializer, params: dict) -> dict:
        """validate and return params"""
        if params is None:
            return 

        return utils.serialize_data_recursively(serializer, params, default={})

    def __get_response_data(self, response: dict) -> dict:
        """get data from response"""
        return (
            response 
            if type(response.get('data')) is list 
            else response['data']
        )

    def get(self, endpoint: str, params: dict = None) -> dict:
        """send get request to api, handle errors and return data"""

        headers = self.get_headers()
        url = f'{self.base_url}{endpoint}'
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f'\n\nError: {response.status_code} {response.text}, \n\n')
            raise SallaEndpointFailureException()

        return self.__get_response_data(response.json())


class SallaMerchantReader(SallaBaseReader):
    """Class to read data from salla merchant api"""
    def get_user(self) -> dict:
        endpoint = '/oauth2/user/info'
        return self.get(endpoint)

    def get_store(self) -> dict:
        endpoint = '/store/info'
        return self.get(endpoint)

    def get_products(self, params: dict = None) -> dict:
        from app.serializers import ProductEndpointParamsSerializer

        endpoint = '/products'
        params = self.get_params(ProductEndpointParamsSerializer, params)

        return self.get(endpoint, params)

    def get_product(self, product_id: str) -> dict:
        endpoint = f'/products/{product_id}'
        return self.get(endpoint)


class SallaAppSettingsReader(SallaBaseReader):
    APP_ID = os.getenv('SALLA_APP_ID')

    def get_subscription(self) -> dict:
        """get the subscription plan that user chose"""

        endpoint = f'/apps/{self.APP_ID}/subscriptions'
        return self.get(endpoint)

    def get_settings(self) -> dict:
        """get the custom settings, user filled in forms that
        created earlier in salla dashboard"""

        endpoint = f'/apps/{self.APP_ID}/settings'
        return self.get(endpoint)


class SallaWriter:
    def __init__(self, account: Account) -> None:
        self.access_token = account.access_token
        self.base_url = os.getenv('SALLA_BASE_URL')

    def put(self, endpoint: str, body: dict) -> dict:
        headers = { 
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.base_url}{endpoint}'
        response = requests.put(url, headers=headers, json=body)

        if response.status_code != 201:
            print(f'\n\nError: {response.status_code} {response.text}, \n\n')
            raise SallaEndpointFailureException()

        return response.json()['data']

    def product_update(self, id: str, body: dict) -> dict:
        endpoint = f'/products/{id}'
        return self.put(endpoint, body)


class ChatGPT:
    def __init__(self) -> None:
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.openai = openai

    def __log_to_db(self, prompt: str, response: dict) -> ChatGPTLog:
        from app.serializers import ChatGPTResponseSerializer

        response.update({'prompt': prompt})

        serializer = ChatGPTResponseSerializer(data=response)
        serializer.is_valid(raise_exception=True)

        return serializer.save()

    def ask(self, prompt: str) -> ChatGPTLog:
        openai_model = os.getenv('OPENAI_MODEL', 'text-davinci-003')
        openai_max_token = int(os.getenv('OPENAI_MAX_TOKEN', 512))

        response = self.openai.Completion.create(
            model=openai_model,
            prompt=prompt,
            temperature=0,
            max_tokens=openai_max_token,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        ).to_dict_recursive()
        
        instance = self.__log_to_db(prompt, response)
        return instance


class ChatGPTProductPromptGenerator:
    """Class to generate chatgpt valid prompt from the product data"""
        
    def __init__(self, data: dict) -> None:
        from SiteServe.models import ChatGPTPromptTemplate

        self.model = ChatGPTPromptTemplate

        self.language = utils.get_language(data['product_name'])
        self.template_name_format = self.model.NAME_FORMAT
        self.data = data
        self._type = data['prompt_type']

    def __get_template(self) -> str:
        template_name = (
            self.template_name_format
                .format(type=self._type, language=self.language)
                .upper()
        )
        template = self.model.get_template(template_name)

        assert template is not None, f'Template with name `{template_name}` not found.'
        return template

    def get_prompt(self) -> str:
        template = self.__get_template().format(**self.data)
        return template

    @classmethod
    def get_prompt_types(cls) -> list:
        types = [
            value
            for key, value in
            ChatGPTProductPromptGenerator.Types.__dict__.items()
            if key.isupper()
        ]

        return types

    class Types:
        TITLE = 'title'
        DESCRIPTION = 'description'
        SEO_TITLE = 'seo_title'
        SEO_DESCRIPTION = 'seo_description'


class SallaWebhook:
    def __init__(self, payload: dict) -> None:
        self.event = payload['event']
        self.merchant_id = payload['merchant']
        self.data = payload['data']

    def __setup(self) -> dict:
        self.salla_user = self.__get_salla_user()
        self.events_map = {
            WebhookEvents.AUTHORIZED.value: self.__authorized,
            WebhookEvents.SETTINGS_UPDATED.value: self.__settings_updated,
        }
        self.event_handler = self.events_map.get(self.event)
        assert self.event_handler is not None, f'Event `{self.event}` not found.'

    def __get_salla_user(self) -> Account:
        return SallaUser.objects.filter(merchant__id=self.merchant_id).first()

    def __authorized(self) -> dict:
        Account.store(self.data)
        return {'status': 'success'}

    def __settings_updated(self) -> dict:
        assert self.salla_user is not None, 'Salla user not found.'

        email = self.data.get('email')
        if email:
            self.salla_user.email = email
            self.salla_user.save()

        password = self.data.get('password')
        if password:
            self.salla_user.set_password(password)

        return {'status': 'success'}

    def __log_to_db(self, response: dict) -> None:
        from app.serializers import SallaWebhookLogSerializer

        serializer = SallaWebhookLogSerializer(data={
            'event': self.event,
            'merchant_id': self.merchant_id,
            'data': self.data,
            'response': response,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def process(self) -> None:
        try:
            self.__setup()
            response = self.event_handler()
            status_code = 200
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
            status_code = 400
        finally:
            self.__log_to_db(response)
        
        return response, status_code


