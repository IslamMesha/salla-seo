import time, string, random, langdetect
from typing import Any, List

from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def next_two_weeks():
    return int(time.time()) + 60 * 60 * 24 * 12

def generate_token(length=64):
    space = string.ascii_letters + string.digits
    return ''.join(random.choices(space, k=length))

def generate_random_username():
    space = string.ascii_lowercase
    length = random.randint(5, 16)
    return ''.join(random.choices(space, k=length))

def set_cookie(response, key, value, max_age=None):
    response.set_cookie(key, value, max_age=max_age, httponly=True, samesite='Strict')

def create_by_serializer(Serializer, data):
    s = Serializer(data=data)
    s.is_valid(raise_exception=True)
    instance = s.save()

    return instance

def serialize_data_recursively(Serializer, data:dict, default:dict=None):
    """If not serializable, return serialized version of the default value"""
    s = Serializer(data=data)

    if s.is_valid():
        data = s.data
    elif default is not None:
        data = serialize_data_recursively(Serializer, default)
    else:
        data = default # which is None

    return data

def get_language(text: str) -> str:
    """Return the language of the text"""
    lang = langdetect.detect(text)
    space = ['en', 'ar']

    if lang not in space:
        # determine the language by the first character
        garbage = string.whitespace + string.punctuation + string.digits
        cleaned_text = text.strip(garbage) or 'Empty text'

        lang = 'en' if cleaned_text[0] in string.ascii_letters else 'ar'
    return lang

def list_to_choices(choices: list) -> list:
    """Convert a list to a list of choices"""
    return [(c, c) for c in choices]

def readable_list(seq: List[Any], combinator='and') -> str:
    """Return a grammatically correct human readable string (with an Oxford comma)."""
    # Ref: https://stackoverflow.com/a/53981846/
    seq = list(map(str, seq))

    if len(seq) < 3:
        result = f' {combinator} '.join(seq)
    else:
        result = ', '.join(seq[:-1]) + f', {combinator} ' + seq[-1]

    return result

def validate_email_and_password(email: str, password: str) -> bool:
    is_valid = True
    try:
        validate_email(email)
        validate_password(password)
    except ValidationError:
        is_valid = False

    return is_valid

def get_static_products():
    import json
    with open('./debug/3-products-list.json', 'r') as f:
        json_data = json.loads(f.read())

    return {
        'products': json_data['data'][:3],
        'pagination': json_data['pagination'],
    }

def chars_to_token_calculator(length: int) -> int:
    """It return a valid token number for chatgpt answer length"""
    return int(length / 5.7)

