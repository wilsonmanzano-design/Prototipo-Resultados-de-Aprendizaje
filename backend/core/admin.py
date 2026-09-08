from django.contrib import admin
from .models import (
    Facultad, Modalidad, Programa, ComponenteFormacion, Curso,
    CompetenciaGeneral, Rap, Rac, CursoRac, LugarDesarrollo,
    Periodo, Corte, Grupo, MetodoEvaluacion, Estudiante, Docente
)


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'facultad', 'modalidad')
    list_filter = ('facultad', 'modalidad')
    search_fields = ('nombre',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'programa', 'semestre', 'activo')
    list_filter = ('programa', 'componente_formacion', 'activo')
    search_fields = ('codigo', 'nombre')


@admin.register(CompetenciaGeneral)
class CompetenciaGeneralAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'programa')
    search_fields = ('codigo',)


@admin.register(Rap)
class RapAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'programa', 'competencia_general')
    list_filter = ('programa',)
    search_fields = ('codigo',)


class CursoRacInline(admin.TabularInline):
    model = CursoRac
    extra = 1


@admin.register(Rac)
class RacAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'rap')
    list_filter = ('rap',)
    search_fields = ('codigo',)
    inlines = [CursoRacInline]


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres')
    search_fields = ('codigo', 'apellidos', 'nombres')


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'identificacion', 'usuario')
    search_fields = ('nombre_completo', 'identificacion')


admin.site.register(Modalidad)
admin.site.register(ComponenteFormacion)
admin.site.register(LugarDesarrollo)
admin.site.register(Periodo)
admin.site.register(Corte)
admin.site.register(Grupo)
admin.site.register(MetodoEvaluacion)