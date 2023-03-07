import os
import requests


class SallaOAuth:
    def __init__(self) -> None:
        self.app_id = os.environ.get('SALLA_APP_ID')
        self.oauth_client_id = os.environ.get('SALLA_OAUTH_CLIENT_ID')
        self.oauth_client_secret = os.environ.get('SALLA_OAUTH_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('SALLA_OAUTH_CLIENT_REDIRECT_URI')

    def get_installation_url(self):
        return f'https://s.salla.sa/apps/install/{self.app_id}'

    def __get_body(self, code) -> dict:
        return {
            'client_id': self.oauth_client_id,
            'client_secret': self.oauth_client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'scope': 'offline_access',
            'redirect_uri': self.redirect_uri
        }

    def __get_headers(self) -> dict:
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Accept': 'application/json'
        }

    def get_access_token(self, code) -> dict:
        body = self.__get_body(code)
        headers = self.__get_headers()
        response = requests.post(
            'https://accounts.salla.sa/oauth2/token',
            data=body,
            headers=headers
        )
        return response.json()
# data = {'access_token': 'ory_at_izDr2oTwm29ePBvnMzMYuG9pGpwqb3-kZgcqNjCNf_k.D4FUUaBl135hPeqEtJD7kc_CgMO6UVTgq-13GSZh6ic', 'expires_in': 1209599, 'refresh_token': 'ory_rt_eP0oWF_e41EJzOeffVnsl-GHuwp5-3piIaogNnAVfoA.YrD0EB5MLp072U5T9maKK7_N-5iL-fa_iM_m_RTE5q0', 'scope': 'settings.read customers.read_write orders.read_write carts.read branches.read_write categories.read_write brands.read_write products.read_write webhooks.read_write payments.read taxes.read_write specialoffers.read_write countries.read shippings.read_write marketing.read_write metadata.read_write offline_access', 'token_type': 'bearer'}


