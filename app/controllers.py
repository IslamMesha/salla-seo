import os
import requests

from rest_framework.serializers import Serializer

from app.exceptions import SallaOauthFailedException, SallaEndpointFailureException
from app.models import Account, ChatGPTLog
from app.serializers import ProductEndpointParamsSerializer, ChatGPTResponseSerializer
from app import utils


class SallaOAuth:
    def __init__(self) -> None:
        self.app_id = os.environ.get('SALLA_APP_ID')
        self.oauth_client_id = os.environ.get('SALLA_OAUTH_CLIENT_ID')
        self.oauth_client_secret = os.environ.get('SALLA_OAUTH_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('SALLA_OAUTH_CLIENT_REDIRECT_URI')

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
        endpoint = '/products'
        params = self.get_params(ProductEndpointParamsSerializer, params)

        return self.get(endpoint, params)

    # TODO delete this method later
    # because product will be cached
    def get_product(self, id: str) -> dict:
        endpoint = '/products/{id}}'
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


class ChatGPT:
    def __init__(self) -> None:
        import openai
        openai.api_key = os.getenv('OPENAI_API_KEY')

        self.openai = openai

    def __log_to_db(self, prompt: str, response: dict) -> ChatGPTLog:
        response.update({'prompt': prompt})

        serializer = ChatGPTResponseSerializer(data=response)
        serializer.is_valid(raise_exception=True)

        return serializer.save()

    def ask(self, prompt: str) -> ChatGPTLog:
        openai_model = os.getenv('OPENAI_MODEL', 'text-davinci-003')
        openai_max_token = int(os.getenv('OPENAI_MAX_TOKEN', 256))

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
        self.language = utils.get_language(data['product_name'])
        self.template_name_format = 'product_{type}_{self.language}'
        self.data = data

    def __get_template(self, t_type: str) -> str:
        template_name = (
            self.template_name_format
                .format(type=t_type, self=self)
                .upper()
        )
        template = getattr(self.ChatGPTPromptTemplates, template_name, None)
        assert template is not None, f'No template found for {template_name}'

        return template

    def __get_prompt(self, t_type: str) -> str:
        # TODO translate template labels into valid python
        # formatted according to data sent to the class
        template = self.__get_template(t_type)
        return template.format(**self.data)

    def ask_for_description(self) -> str:
        _type = self.Types.DESCRIPTION
        return self.__get_prompt(_type)


    class Types:
        DESCRIPTION = 'description'
        SEO_TITLE = 'seo_title'

    class ChatGPTPromptTemplates:
        # hold templates for asking chatgpt
        # NOTE every type should have many languages
        # NOTE name must follow this format: product_{type}_{language}
        PRODUCT_DESCRIPTION_EN = 'write a brief about product {product_name}'
        PRODUCT_DESCRIPTION_AR = 'اكتب ملخصاً قصير عن منتج أسمه: {product_name}'


        

