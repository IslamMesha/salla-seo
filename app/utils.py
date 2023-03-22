import time, string, random, langdetect


def next_two_weeks():
    return int(time.time()) + 60 * 60 * 24 * 14

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

