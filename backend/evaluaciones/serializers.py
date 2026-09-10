from rest_framework import serializers
from django.db import transaction
from core.models import Estudiante
from .models import (
    OfertaAcademica, OfertaGrupo, Matricula, EvaluacionRac,
    AnalisisEvaluacion, RubricaCriterio, RubricaNivel,
    RubricaEstudiante, RubricaRespuesta, VwEvaluacionEstadistica
)


class RubricaNivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricaNivel
        fields = ['id', 'nombre', 'descripcion', 'valor_min', 'valor_max']


class RubricaCriterioSerializer(serializers.ModelSerializer):
    niveles = RubricaNivelSerializer(many=True, read_only=True)

    class Meta:
        model = RubricaCriterio
        fields = ['id', 'nombre', 'niveles']


class OfertaAcademicaSerializer(serializers.ModelSerializer):
    curso_codigo = serializers.CharField(source='curso.codigo', read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    docente_nombre = serializers.CharField(source='docente.nombre_completo', read_only=True)
    periodo_etiqueta = serializers.SerializerMethodField()
    grupos = serializers.SerializerMethodField()

    class Meta:
        model = OfertaAcademica
        fields = [
            'id', 'curso', 'curso_codigo', 'curso_nombre', 'docente', 'docente_nombre',
            'periodo', 'periodo_etiqueta', 'modalidad', 'lugar_desarrollo', 'grupos'
        ]

    def get_periodo_etiqueta(self, obj):
        return f"{obj.periodo.anio}-{obj.periodo.numero}"

    def get_grupos(self, obj):
        return [og.grupo.codigo for og in obj.grupos.select_related('grupo').all()]


class MatriculaSerializer(serializers.ModelSerializer):
    estudiante_codigo = serializers.CharField(source='estudiante.codigo', read_only=True)
    estudiante_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Matricula
        fields = ['id', 'oferta', 'estudiante', 'estudiante_codigo', 'estudiante_nombre', 'corte', 'estado', 'fecha_estado']

    def get_estudiante_nombre(self, obj):
        return f"{obj.estudiante.apellidos} {obj.estudiante.nombres}"


class EvaluacionRacSerializer(serializers.ModelSerializer):
    rac_codigo = serializers.CharField(source='rac.codigo', read_only=True)
    corte_nombre = serializers.CharField(source='corte.nombre', read_only=True)

    class Meta:
        model = EvaluacionRac
        fields = ['id', 'oferta', 'rac', 'rac_codigo', 'corte', 'corte_nombre', 'metodo_evaluacion', 'fecha_diligenciamiento']


class EstadisticaEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VwEvaluacionEstadistica
        fields = [
            'matriculados', 'participantes', 'porcentaje_participacion',
            'competentes', 'no_competentes', 'media', 'mediana',
            'desviacion_estandar', 'valor_mayor', 'valor_menor'
        ]


# ---------- Serializers de ENTRADA para el endpoint de diligenciamiento ----------

class RespuestaInputSerializer(serializers.Serializer):
    criterio_id = serializers.IntegerField()
    nivel_id = serializers.IntegerField()


class EstudianteRubricaInputSerializer(serializers.Serializer):
    estudiante_id = serializers.IntegerField()
    respuestas = RespuestaInputSerializer(many=True)


class AnalisisInputSerializer(serializers.Serializer):
    elementos_impidieron = serializers.CharField(allow_blank=True, required=False)
    elementos_permitieron = serializers.CharField(allow_blank=True, required=False)
    elementos_medios_infra = serializers.CharField(allow_blank=True, required=False)
    propuesta_metodologia = serializers.CharField(allow_blank=True, required=False)
    propuesta_contenido = serializers.CharField(allow_blank=True, required=False)
    propuesta_situacion_curso = serializers.CharField(allow_blank=True, required=False)


class DiligenciarEvaluacionRacSerializer(serializers.Serializer):
    """Valida y persiste TODO el formulario F-FOR-10 digital en una sola transaccion:
    crea/obtiene la evaluacion, guarda la rubrica de cada estudiante y el analisis."""

    oferta_id = serializers.IntegerField()
    rac_id = serializers.IntegerField()
    corte_id = serializers.IntegerField()
    metodo_evaluacion_id = serializers.IntegerField()
    estudiantes = EstudianteRubricaInputSerializer(many=True)
    analisis = AnalisisInputSerializer()

    def save(self, **kwargs):
        data = self.validated_data
        with transaction.atomic():
            evaluacion, _ = EvaluacionRac.objects.get_or_create(
                oferta_id=data['oferta_id'],
                rac_id=data['rac_id'],
                corte_id=data['corte_id'],
                defaults={'metodo_evaluacion_id': data['metodo_evaluacion_id']},
            )
            # si ya existia con otro metodo de evaluacion, lo actualizamos
            if evaluacion.metodo_evaluacion_id != data['metodo_evaluacion_id']:
                evaluacion.metodo_evaluacion_id = data['metodo_evaluacion_id']
                evaluacion.save(update_fields=['metodo_evaluacion_id'])

            niveles_cache = {n.id: n for n in RubricaNivel.objects.all()}

            for item in data['estudiantes']:
                rubrica_est, _ = RubricaEstudiante.objects.get_or_create(
                    evaluacion_rac=evaluacion,
                    estudiante_id=item['estudiante_id'],
                )
                for resp in item['respuestas']:
                    nivel = niveles_cache.get(resp['nivel_id'])
                    if nivel is None:
                        raise serializers.ValidationError(f"Nivel {resp['nivel_id']} no existe.")
                    valor_asignado = round((float(nivel.valor_min) + float(nivel.valor_max)) / 2, 2)
                    RubricaRespuesta.objects.update_or_create(
                        rubrica_estudiante=rubrica_est,
                        criterio_id=resp['criterio_id'],
                        defaults={'nivel_id': resp['nivel_id'], 'valor_asignado': valor_asignado},
                    )
                rubrica_est.refresh_from_db()  # trae el valoracion_final ya recalculado por el trigger

            AnalisisEvaluacion.objects.update_or_create(
                evaluacion_rac=evaluacion,
                defaults=data.get('analisis', {}),
            )

        return evaluacion