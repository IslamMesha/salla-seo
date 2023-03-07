
from rest_framework.exceptions import APIException
from rest_framework import status


class SallaOauthFailedException(APIException):
    default_detail = 'Salla Oauth Failed.'
    default_code = 'error'
    status_code = status.HTTP_401_UNAUTHORIZED

