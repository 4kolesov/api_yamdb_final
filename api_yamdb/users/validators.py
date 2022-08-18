import re

from django.conf import settings
from rest_framework.validators import ValidationError


def regex_test(value):
    if re.match('^[a-zA-Z0-9.@+-_]+$', value):
        return True
    return False


class CorrectUsernameAndNotMe:
    """Проверка username на корректность и несоответствие "me"."""
    message = 'Можно использовать латиницу, цифры, @ + -. Нельзя — "me"!'

    def __init__(self, field, message=None):
        self.field = field
        self.message = message or self.message

    def __call__(self, value):
        if (value == settings.NO_REGISTER_USERNAME
                or not regex_test(value=value)):
            raise ValidationError({self.field: self.message})
