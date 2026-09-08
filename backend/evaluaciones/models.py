from django.db import models
from core.models import Curso, Docente, Periodo, Modalidad, LugarDesarrollo, Grupo, Estudiante, Corte, Rac, MetodoEvaluacion


class OfertaAcademica(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='ofertas')
    docente = models.ForeignKey(Docente, on_delete=models.PROTECT, related_name='ofertas')
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='ofertas')
    modalidad = models.ForeignKey(Modalidad, on_delete=models.PROTECT, related_name='ofertas')
    lugar_desarrollo = models.ForeignKey(LugarDesarrollo, on_delete=models.PROTECT, related_name='ofertas')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'oferta_academica'
        unique_together = ('curso', 'docente', 'periodo', 'lugar_desarrollo')

    def __str__(self):
        return f"{self.curso.codigo} - {self.docente} - {self.periodo}"


class OfertaGrupo(models.Model):
    oferta = models.ForeignKey(OfertaAcademica, on_delete=models.CASCADE, related_name='grupos')
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT)

    class Meta:
        db_table = 'oferta_grupo'
        unique_together = ('oferta', 'grupo')


class Matricula(models.Model):
    ESTADO_CHOICES = [('matriculado', 'Matriculado'), ('retirado', 'Retirado')]

    oferta = models.ForeignKey(OfertaAcademica, on_delete=models.CASCADE, related_name='matriculas')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name='matriculas')
    corte = models.ForeignKey(Corte, on_delete=models.PROTECT, related_name='matriculas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='matriculado')
    fecha_estado = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'matricula'
        unique_together = ('oferta', 'estudiante', 'corte')

    def __str__(self):
        return f"{self.estudiante} - {self.oferta} - {self.corte}"


class EvaluacionRac(models.Model):
    oferta = models.ForeignKey(OfertaAcademica, on_delete=models.CASCADE, related_name='evaluaciones')
    rac = models.ForeignKey(Rac, on_delete=models.PROTECT, related_name='evaluaciones')
    corte = models.ForeignKey(Corte, on_delete=models.PROTECT, related_name='evaluaciones')
    metodo_evaluacion = models.ForeignKey(MetodoEvaluacion, on_delete=models.PROTECT, related_name='evaluaciones')
    fecha_diligenciamiento = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'evaluacion_rac'
        unique_together = ('oferta', 'rac', 'corte')

    def __str__(self):
        return f"{self.oferta} - {self.rac.codigo} - {self.corte}"


class AnalisisEvaluacion(models.Model):
    evaluacion_rac = models.OneToOneField(EvaluacionRac, on_delete=models.CASCADE, primary_key=True, related_name='analisis')
    elementos_impidieron = models.TextField(blank=True)
    elementos_permitieron = models.TextField(blank=True)
    elementos_medios_infra = models.TextField(blank=True)
    propuesta_metodologia = models.TextField(blank=True)
    propuesta_contenido = models.TextField(blank=True)
    propuesta_situacion_curso = models.TextField(blank=True)

    class Meta:
        db_table = 'analisis_evaluacion'

    def __str__(self):
        return f"Análisis de {self.evaluacion_rac}"


class RubricaCriterio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'rubrica_criterio'

    def __str__(self):
        return self.nombre


class RubricaNivel(models.Model):
    criterio = models.ForeignKey(RubricaCriterio, on_delete=models.CASCADE, related_name='niveles')
    nombre = models.CharField(max_length=30)
    descripcion = models.TextField()
    valor_min = models.DecimalField(max_digits=3, decimal_places=2)
    valor_max = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table = 'rubrica_nivel'
        unique_together = ('criterio', 'nombre')

    def __str__(self):
        return f"{self.criterio.nombre} - {self.nombre}"


class RubricaEstudiante(models.Model):
    evaluacion_rac = models.ForeignKey(EvaluacionRac, on_delete=models.CASCADE, related_name='rubricas_estudiantes')
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name='rubricas')
    valoracion_final = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'rubrica_estudiante'
        unique_together = ('evaluacion_rac', 'estudiante')

    def __str__(self):
        return f"{self.estudiante} - {self.evaluacion_rac}"


class RubricaRespuesta(models.Model):
    rubrica_estudiante = models.ForeignKey(RubricaEstudiante, on_delete=models.CASCADE, related_name='respuestas')
    criterio = models.ForeignKey(RubricaCriterio, on_delete=models.PROTECT)
    nivel = models.ForeignKey(RubricaNivel, on_delete=models.PROTECT)
    valor_asignado = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        db_table = 'rubrica_respuesta'
        unique_together = ('rubrica_estudiante', 'criterio')