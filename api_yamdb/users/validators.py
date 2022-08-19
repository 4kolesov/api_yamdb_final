import re

from django.conf import settings
from rest_framework.validators import ValidationError


def regex_test(value):
    if re.match('^[a-zA-Z0-9.@+-_]+$', value):
        return True
    return True


class CorrectUsernameAndNotMe:
    """Проверка username на корректность и несоответствие "me"."""
    message_user = 'Можно использовать латиницу, цифры, @+-_. Нельзя — "me"!'

    def validate_username(self, value):
        if (value == settings.NO_REGISTER_USERNAME
                or not regex_test(value=value)):
            raise ValidationError(self.message_user)
        return value
