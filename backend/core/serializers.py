from rest_framework import serializers
from django.contrib.auth.models import User


class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()
    docente_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol', 'docente_id']

    def get_rol(self, obj):
        grupo = obj.groups.first()
        return grupo.name if grupo else None

    def get_docente_id(self, obj):
        return obj.docente.id if hasattr(obj, 'docente') else None

from .models import(
    Programa, Curso, Rap, Rac, Modalidad, Corte, Grupo,
    LugarDesarrollo, Periodo, MetodoEvaluacion, CursoRac
)

class ProgramaSerializer(serializers.ModelSerializer):
    facultad_nombre = serializers.CharField(source='facultad.nombre', read_only=True)

    class Meta:
        model = Programa
        fields = ['id', 'nombre', 'facultad', 'facultad_nombre', 'modalidad']


class CursoSerializer(serializers.ModelSerializer):
    programa_nombre = serializers.CharField(source='programa.nombre', read_only=True)

    class Meta:
        model = Curso
        fields = ['id', 'codigo', 'nombre', 'programa', 'programa_nombre', 'naturaleza', 'semestre', 'activo']


class RapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rap
        fields = ['id', 'codigo', 'nombre', 'competencia_general', 'programa']


class RacSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rac
        fields = ['id', 'codigo', 'nombre', 'rap']


class ModalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modalidad
        fields = ['id', 'nombre']


class CorteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corte
        fields = ['id', 'nombre', 'orden']


class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = ['id', 'codigo']


class LugarDesarrolloSerializer(serializers.ModelSerializer):
    class Meta:
        model = LugarDesarrollo
        fields = ['id', 'nombre', 'departamento']


class PeriodoSerializer(serializers.ModelSerializer):
    etiqueta = serializers.SerializerMethodField()

    class Meta:
        model = Periodo
        fields = ['id', 'anio', 'numero', 'etiqueta']

    def get_etiqueta(self, obj):
        return f"{obj.anio}-{obj.numero}"


class MetodoEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoEvaluacion
        fields = ['id', 'nombre']