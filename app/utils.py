import time
import string, random

def next_two_weeks():
    return int(time.time()) + 60 * 60 * 24 * 14

def generate_token(length=64):
    space = string.ascii_letters + string.digits
    return random.choices(space, k=length)

