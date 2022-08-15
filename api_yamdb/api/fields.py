from rest_framework import serializers
from django.shortcuts import get_object_or_404


class GenreTitleField(serializers.ManyRelatedField):
    """Поле отображения категорий в произведениях."""
    def to_internal_value(self, data):
        return [get_object_or_404(Genre, slug=slug) for slug in data]


class toSerializerinSlugRelatedField(serializers.SlugRelatedField):
    """Поле отображения категорий в произведениях."""
    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
        super(toSerializerinSlugRelatedField, self).__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer(value).data
