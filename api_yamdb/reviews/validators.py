from datetime import date

from rest_framework.validators import ValidationError


class MaxYear:
    """Проверка года не выше текущего."""
    message = 'Год выпуска не может быть больше текущего'

    def __init__(self, field, message=None):
        self.field = field
        self.message = message or self.message

    def __call__(self, value):
        year = value.get(self.field)
        if year and (year > date.today().year):
            raise ValidationError({self.field: self.message})
