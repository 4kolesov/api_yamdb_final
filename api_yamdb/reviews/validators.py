import collections
from datetime import date

from rest_framework.validators import ValidationError


def max_year(value):
    message = 'Год выпуска не может быть больше текущего'
    if isinstance(value, collections.OrderedDict):
        if value.get('year'):
            value = value['year']
        else:
            return True
    if value > date.today().year:
        raise ValidationError({'year': message})
    return True
