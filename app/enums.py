from enum import Enum

class CookieKeys(Enum):
    # hold names of the cookies
    AUTH_TOKEN = 'auth_token'


class ChatGPTPromptTemplates(Enum):
    # hold templates for asking chatgpt
    PRODUCT_DESCRIPTION_EN = 'write a brief about product {product_name}'
    PRODUCT_DESCRIPTION_AR = 'اكتب ملخصاً عن المنتج {product_name}'


