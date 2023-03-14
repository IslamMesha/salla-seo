import os
import requests

from rest_framework.serializers import Serializer

from app.exceptions import SallaOauthFailedException, SallaEndpointFailureException
from app.models import Account
from app.serializers import ProductEndpointParamsSerializer
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


