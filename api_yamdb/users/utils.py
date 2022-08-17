import re
from random import randint


def generate_confirmation_code():
    return randint(10001, 99999)


def regex_test(value):
    if re.match('^[a-zA-Z0-9.@+-]+$', value):
        return True
