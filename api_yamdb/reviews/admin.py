from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'description', 'category')
    search_fields = ('name',)
    list_filter = ('name',)
    list_editable = ('name', 'year', 'description', 'category')


@admin.register(Category, Genre)
class CGAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('slug',)
    list_filter = ('name',)
    list_editable = ('name', 'slug')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'pub_date', 'author', 'title', 'score')
    search_fields = ('author', 'title')
    list_filter = ('title',)
    list_editable = ('text', 'author', 'title', 'score')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'pub_date', 'author', 'review')
    search_fields = ('author', 'review')
    list_filter = ('review',)
    list_editable = ('text', 'author', 'review')
