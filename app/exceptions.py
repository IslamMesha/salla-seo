
from rest_framework.exceptions import APIException
from rest_framework import status


class SallaOauthFailedException(APIException):
    default_detail = 'Salla Oauth Failed.'
    default_code = 'error'
    status_code = status.HTTP_401_UNAUTHORIZED


class SallaEndpointFailureException(APIException):
    default_detail = 'Salla Endpoint not going right.'
    default_code = 'error'
    status_code = status.HTTP_424_FAILED_DEPENDENCY


class SallaWebhookFailureException(APIException):
    default_detail = 'Webhook Failure.'
    default_code = 'error'
    status_code = status.HTTP_400_BAD_REQUEST
