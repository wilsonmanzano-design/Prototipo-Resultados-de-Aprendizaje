from django.contrib import admin
from .models import (
    OfertaAcademica, OfertaGrupo, Matricula, EvaluacionRac,
    AnalisisEvaluacion, RubricaCriterio, RubricaNivel,
    RubricaEstudiante, RubricaRespuesta
)


class OfertaGrupoInline(admin.TabularInline):
    model = OfertaGrupo
    extra = 1


@admin.register(OfertaAcademica)
class OfertaAcademicaAdmin(admin.ModelAdmin):
    list_display = ('curso', 'docente', 'periodo', 'modalidad', 'lugar_desarrollo')
    list_filter = ('periodo', 'modalidad', 'lugar_desarrollo')
    inlines = [OfertaGrupoInline]


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'oferta', 'corte', 'estado')
    list_filter = ('corte', 'estado')
    search_fields = ('estudiante__codigo', 'estudiante__apellidos')


@admin.register(EvaluacionRac)
class EvaluacionRacAdmin(admin.ModelAdmin):
    list_display = ('oferta', 'rac', 'corte', 'metodo_evaluacion')
    list_filter = ('corte', 'rac')


admin.site.register(AnalisisEvaluacion)
admin.site.register(RubricaCriterio)
admin.site.register(RubricaNivel)
admin.site.register(RubricaEstudiante)
admin.site.register(RubricaRespuesta)