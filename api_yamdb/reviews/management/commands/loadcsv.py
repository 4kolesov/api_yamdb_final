import csv

from django.core.management.base import BaseCommand
from django.conf import settings

from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment


class Command(BaseCommand):
    help = 'загружает данные в БД из csv.'

    def handle(self, *args, **options):
        FILES = {
            'data/category.csv': Category,
            'data/genre.csv': Genre,
            'data/users.csv': User,
            'data/titles.csv': Title,
            'data/review.csv': Review,
            'data/comments.csv': Comment,
            'data/genre_title.csv': Title
        }
        for url, model in FILES.items():
            path = f'{settings.STATICFILES_DIRS[0]}{url}'
            print(f'Начинается загрузка из {url}')
            with open(path, newline='', encoding='utf-8') as file:
                csvfile = csv.DictReader(file, delimiter=',')
                for row in csvfile:
                    try:
                        if url == 'data/titles.csv':
                            cat = Category.objects.get(id=row.pop('category'))
                            model.objects.create(**row, category=cat)
                        elif url == 'data/review.csv':
                            title = Title.objects.get(id=row.pop('title_id'))
                            author = User.objects.get(id=row.pop('author'))
                            model.objects.create(
                                **row, title=title, author=author
                            )
                        elif url == 'data/comments.csv':
                            review = Review.objects.get(
                                id=row.pop('review_id')
                            )
                            author = User.objects.get(id=row.pop('author'))
                            model.objects.create(
                                **row, review=review, author=author
                            )
                        elif url == 'data/genre_title.csv':
                            genre = Genre.objects.get(id=row.pop('genre_id'))
                            title = Title.objects.get(id=row.pop('title_id'))
                            title.genre.add(genre)
                            title.save()
                        else:
                            model.objects.create(**row)
                        print(f'Запись {row["id"]} добавлена')
                    except Exception as err:
                        print(f'Какая то ошибка...{err}')
            print('Готово вроде бы')
        print('Теперь точно готово!')
