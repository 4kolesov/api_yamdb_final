import csv

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'загружает данные в БД из csv.'

    def handle(self, *args, **options):
        path = f'{settings.STATICFILES_DIRS}data/users.csv'
        with open(path, newline=',,,') as file:
            csvfile = csv.reader(file, delimiter=',')
            for row in csvfile:
                print(row)
