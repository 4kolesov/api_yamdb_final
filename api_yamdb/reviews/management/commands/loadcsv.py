import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from rest_framework.utils.model_meta import get_field_info

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class Command(BaseCommand):
    help = (f'Загружает данные в БД из csv.'
            f'csv файлы должны находиться в дериктории: '
            f'{settings.STATICFILES_DIRS[0]}')

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear_base',
            action='store_true',
            help = 'Очищает таблицы моделей перед заполнением.'
        )
        parser.add_argument(
            '--only_err_msg',
            action='store_true',
            help = 'Выводит только основную информацию и сообщения об ошибках.'
        )

    def clear_tables(self, models, err_msg=False):
        print('Начинается очистка таблиц.')
        for model in models:
            if not err_msg:
                print(
                    f'Удаление записей из таблицы модели: {model.__name__}'
                )
            try:
                model.objects.all().delete()
            except Exception as err:
                print(f'Ошибка при попытке удалить записи из {model.__name__}:'
                      f' {err}')
        print('Очистка таблиц завершена.')

    def handle(self, *args, **options):
        CATEGORY = 'data/category.csv'
        GENRE = 'data/genre.csv'
        USER = 'data/users.csv'
        TITLE = 'data/titles.csv'
        REVIEW = 'data/review.csv'
        COMMENT = 'data/comments.csv'
        GENRE_TITLE = 'data/genre_title.csv'
        MODELS = [Category, Genre, User, Title, Review, Comment]
        FILE_MODEL = {
            CATEGORY: Category,
            GENRE: Genre,
            USER: User,
            TITLE: Title,
            REVIEW: Review,
            COMMENT: Comment,
            GENRE_TITLE: Title
        }
        if options['clear_base']:
            self.clear_tables(MODELS, options['only_err_msg'])

        for url, model in FILE_MODEL.items():
            path = f'{settings.STATICFILES_DIRS[0]}{url}'
            print(f'Начинается загрузка из {url}')
            try:
                with open(path, newline='', encoding='utf-8') as file:
                    csvfile = csv.DictReader(file, delimiter=',')
                    relations = get_field_info(model).forward_relations
                    rel_fields = {}
                    for field in csvfile.fieldnames:
                        if (field in relations and
                                not relations[field].to_many):
                            rel_fields[field] = relations[field].related_model
                    for row in csvfile:
                        try:
                            if url == GENRE_TITLE:
                                genre = Genre.objects.get(
                                    id=row.pop('genre_id'))
                                title = Title.objects.get(
                                    id=row.pop('title_id'))
                                title.genre.add(genre)
                                title.save()
                            else:
                                for field, r_model in rel_fields.items():
                                    row[field] = r_model.objects.get(
                                        id=row.get(field))
                                model.objects.create(**row)
                            if not options['only_err_msg']:
                                print(f'Запись {row["id"]} добавлена')
                        except Exception as err:
                            print(f'Какая то ошибка...{err}')
                print(f'Загрузка из {url} завершена.')
            except FileNotFoundError as err:
                print(f'Нет файла {url} в нужной дериктории: {err}')
