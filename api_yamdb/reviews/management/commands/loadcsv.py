from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'загружает данные в БД из csv.'
    def add_arguments(self, parser):
        parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        pass