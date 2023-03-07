import os
import requests

from app.exceptions import SallaOauthFailedException


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

    def get_access_token(self, code) -> dict:
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

    def refresh_access_token(self, refresh_token):
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


class SallaEndpoint:
    def __init__(self, account) -> None:
        # TODO account is database record that contain oauth data

        self.access_token = account.get('access_token')
        self.refresh_token = account.get('refresh_token')

        self.base_url = 'https://accounts.salla.sa/oauth2'
        self.rate_limit = 0

    def __get_headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.access_token}',
        }

    def get_user(self):
        url = f'{self.base_url}/user/info'
        headers = self.__get_headers()

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise SallaOauthFailedException()

        return response.json()
        

