import time
import string, random

def next_two_weeks():
    return int(time.time()) + 60 * 60 * 24 * 14

def generate_token(length=64):
    space = string.ascii_letters + string.digits
    return ''.join(random.choices(space, k=length))

def generate_random_username():
    space = string.ascii_lowercase
    length = random.randint(5, 16)
    return ''.join(random.choices(space, k=length))

