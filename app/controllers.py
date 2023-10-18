import os
import logging
import requests

from rest_framework.serializers import Serializer
from rest_framework.exceptions import ValidationError

from app.exceptions import SallaOauthFailedException, SallaEndpointFailureException, SallaWebhookFailureException
from app.models import Account, ChatGPTResponse, SallaUser
from app import utils
from app.enums import WebhookEvents


logger = logging.getLogger('main')


class SallaOAuth:
    def __init__(self, base_url:str=None) -> None:
        self.app_id = os.environ.get('SALLA_APP_ID')
        self.oauth_client_id = os.environ.get('SALLA_OAUTH_CLIENT_ID')
        self.oauth_client_secret = os.environ.get('SALLA_OAUTH_CLIENT_SECRET')
        self.base_url = base_url

    @property
    def redirect_uri(self):
        # if self.base_url is None:
        #     uri = os.environ.get('SALLA_OAUTH_CLIENT_REDIRECT_URI')
        # else:
        #     uri = self.base_url.rstrip('/') + reverse('app:oauth_callback')

        # return uri
        if os.getenv('IS_LOCAL') == 'True':
            return 'http://127.0.0.1:8000/oauth/callback/'
        return 'https://tafaseel.io/oauth/callback/'

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

def handel_salla_response_status_code(response, instance):
    error_message = 'SallaError [{classname}]: ({status_code}) [{url}] {text}'.format(
        classname=instance.__class__.__name__, url=response.request.url,
        status_code=response.status_code, text=response.text
    )
    if response.status_code < 300:
        pass # success
    elif response.status_code == 401:
        instance.account.access_token = None
        instance.account.refresh_token = None
        instance.account.save()
        logger.error(error_message)
        raise SallaOauthFailedException()
    else:
        logger.error(error_message)
        raise SallaEndpointFailureException()


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

        handel_salla_response_status_code(response, self)
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

        handel_salla_response_status_code(response, self)
        return response.json()['data']

    def post(self, endpoint: str, body: dict) -> dict:
        headers = { 
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        url = f'{self.base_url}{endpoint}'
        response = requests.post(url, headers=headers, json=body)

        handel_salla_response_status_code(response, self)
        return response.json()['data']

    def product_update(self, id: str, body: dict) -> dict:
        endpoint = f'/products/{id}'
        return self.put(endpoint, body)

    def balance_update(self, body: dict) -> dict:
        endpoint = '/apps/balance'
        return self.post(endpoint, body)


class ChatGPT:
    def __init__(self, max_tokens:int=None) -> None:
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.openai = openai
        self.max_tokens = max_tokens or int(os.getenv('OPENAI_MAX_TOKEN', 512))

    def __log_to_db(self, prompt: str, response: dict) -> ChatGPTResponse:
        from app.serializers import ChatGPTResponseSerializer

        response.update({'prompt': prompt})

        serializer = ChatGPTResponseSerializer(data=response)
        serializer.is_valid(raise_exception=True)

        return serializer.save()

    def ask(self, prompt: str) -> ChatGPTResponse:
        openai_model = os.getenv('OPENAI_MODEL', 'text-davinci-003')

        response = self.openai.Completion.create(
            model=openai_model,
            prompt=prompt,
            temperature=0,
            max_tokens=self.max_tokens,
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

    def get_constraints(self):
        return {
            self.Types.SEO_TITLE: {
                'max_tokens': 70,
            },
            self.Types.SEO_DESCRIPTION: {
                'max_tokens': 140,
            }
        }.get(self._type, {})

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
        self.event_handler = {
            WebhookEvents.AUTHORIZED.value: self.__authorized,
            WebhookEvents.SETTINGS_UPDATED.value: self.__settings_updated,

            WebhookEvents.TRIAL_STARTED.value: self.__trial_started,
            WebhookEvents.TRIAL_EXPIRED.value: self.__trial_expired,
            WebhookEvents.SUBSCRIPTION_STARTED.value: self.__subscription_started,
            WebhookEvents.SUBSCRIPTION_EXPIRED.value: self.__subscription_expired,
            WebhookEvents.SUBSCRIPTION_CANCELLED.value: self.__subscription_cancelled,

            WebhookEvents.APP_UNINSTALLED.value: self.__subscription_cancelled,
        }.get(self.event)

        if self.event_handler is None:
            raise  SallaWebhookFailureException(f'Event {self.event} not found.')

    def __get_salla_user(self) -> Account:
        # return SallaUser.objects.filter(merchant__id=self.merchant_id).first()
        user = SallaUser.objects.filter(store__salla_id=self.merchant_id).first()
        if user is None and self.event != WebhookEvents.AUTHORIZED.value:
            raise SallaWebhookFailureException('User not found')
        return user

    def __authorized(self) -> dict:
        Account.store(self.data)
        return {'status': 'success'}

    def __settings_updated(self) -> dict:
        assert self.salla_user is not None, 'Salla user not found.'

        settings = self.data.get('settings')

        email = settings.get('email')
        if email:
            self.salla_user.email = email

        password = settings.get('password')
        if password:
            self.salla_user.password = password

        self.salla_user.save()
        return {'status': 'success'}

    def __get_subscription_payload(self) -> dict:
        from app.serializers import SallaUserSubscriptionPayloadSerializer

        serializer = SallaUserSubscriptionPayloadSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)

        return serializer.data

    def __stop_subscriptions(self) -> None:
        payload = self.__get_subscription_payload()

        # self.salla_user.subscriptions.filter(
        #     plan_name__iexact=payload['plan_name']
        # ).update(is_active=False)
        self.salla_user.subscriptions.all().update(is_active=False)

    def __start_subscriptions(self, is_trial: bool = False):
        from app.models import SallaUserSubscription

        payload = self.__get_subscription_payload()
        subscription = SallaUserSubscription(
            user=self.salla_user,
            payload=self.data,
            is_trial=is_trial,
            **payload
        )
        subscription.save()
        return subscription

    def __trial_started(self) -> dict:        
        self.__stop_subscriptions()
        self.__start_subscriptions(is_trial=True)

        return {'status': 'success'}

    def __trial_expired(self) -> dict:
        self.__stop_subscriptions()
        return {'status': 'success'}

    def __subscription_started(self) -> dict:
        self.__stop_subscriptions()
        self.__start_subscriptions(is_trial=False)

        return {'status': 'success'}

    def __subscription_expired(self) -> dict:
        self.__stop_subscriptions()
        return {'status': 'success'}

    def __subscription_cancelled(self) -> dict:
        self.__stop_subscriptions()
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
        except SallaWebhookFailureException as e:
            response = {'status': str(e)}
            status_code = 200
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
            status_code = 400
        finally:
            self.__log_to_db(response)
        
        return response, status_code


