from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title

admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
