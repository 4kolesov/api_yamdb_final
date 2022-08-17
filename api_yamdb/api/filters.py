from django_filters import CharFilter, FilterSet, NumberFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='startswith')
    year = NumberFilter(field_name='year')
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')
