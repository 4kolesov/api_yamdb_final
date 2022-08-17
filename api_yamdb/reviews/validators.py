from rest_framework.validators import ValidationError
from datetime import date


class MaxYear:
    """Проверка года не выше текущего."""
    message = 'Год выпуска не может быть больше текущего'

    def __init__(self, field, message=None):
        self.field = field
        self.message = message or self.message

    def __call__(self, value):
        if value[self.field] > date.today().year:
            raise ValidationError({self.field: self.message})
