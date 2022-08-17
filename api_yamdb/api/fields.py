from rest_framework import serializers


class ToSerializerInSlugManyRelatedField(serializers.ManyRelatedField):
    """Поле отображения сериализатором, получение полем slug для M2M."""
    def __init__(self, queryset, slug_field, **kwargs):
        self.queryset = queryset
        self.slug_field = slug_field
        super(ToSerializerInSlugManyRelatedField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        return [
            serializers.SlugRelatedField(
                slug_field=self.slug_field, queryset=self.queryset
            ).to_internal_value(slug) for slug in data
        ]


class ToSerializerInSlugRelatedField(serializers.SlugRelatedField):
    """Поле отображения сериализатором, получение полем slug."""
    def __init__(self, serializer, **kwargs):
        self.serializer = serializer
        super(ToSerializerInSlugRelatedField, self).__init__(**kwargs)

    def to_representation(self, value):
        return self.serializer(value).data
