import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment


class Command(BaseCommand):
    help = (f'Загружает данные в БД из csv.'
            f'csv файлы должны находиться в дериктории: '
            f'{settings.STATICFILES_DIRS[0]}')

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear_base',
            action='store_true',
            help = 'Очищает базу перед заполнением.'
        )

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
        for model in MODELS:
            if options['clear_base']:
                print(
                    f'Удаление записей из таблицы модели: {model.__name__}'
                )
                model.objects.all().delete()

        for url, model in FILE_MODEL.items():
            path = f'{settings.STATICFILES_DIRS[0]}{url}'
            print(f'Начинается загрузка из {url}')
            try:
                with open(path, newline='', encoding='utf-8') as file:
                    csvfile = csv.DictReader(file, delimiter=',')
                    for row in csvfile:
                        try:
                            if url == TITLE:
                                cat = Category.objects.get(
                                    id=row.pop('category'))
                                model.objects.create(**row, category=cat)
                            elif url == REVIEW:
                                title = Title.objects.get(
                                    id=row.pop('title_id'))
                                author = User.objects.get(id=row.pop('author'))
                                model.objects.create(
                                    **row, title=title, author=author
                                )
                            elif url == COMMENT:
                                review = Review.objects.get(
                                    id=row.pop('review_id')
                                )
                                author = User.objects.get(id=row.pop('author'))
                                model.objects.create(
                                    **row, review=review, author=author
                                )
                            elif url == GENRE_TITLE:
                                genre = Genre.objects.get(
                                    id=row.pop('genre_id'))
                                title = Title.objects.get(
                                    id=row.pop('title_id'))
                                title.genre.add(genre)
                                title.save()
                            else:
                                model.objects.create(**row)
                            print(f'Запись {row["id"]} добавлена')
                        except Exception as err:
                            print(f'Какая то ошибка...{err}')
                print(f'Загрузка из {url} завершена.')
            except FileNotFoundError as err:
                print(f'Нет файла {url} в нужной дериктории: {err}')
        print('Загрузка завершена.')
