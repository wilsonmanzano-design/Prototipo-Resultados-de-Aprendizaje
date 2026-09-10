import django_filters
from .models import Curso, Rac


class CursoFilter(django_filters.FilterSet):
    programa = django_filters.NumberFilter(field_name='programa_id')
    activo = django_filters.BooleanFilter(field_name='activo')

    class Meta:
        model = Curso
        fields = ['programa', 'activo']


class RacFilter(django_filters.FilterSet):
    rap = django_filters.NumberFilter(field_name='rap_id')

    class Meta:
        model = Rac
        fields = ['rap']