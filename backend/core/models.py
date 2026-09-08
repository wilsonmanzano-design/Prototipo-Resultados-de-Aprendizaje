from django.db import models
from django.contrib.auth.models import User


class Facultad(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = 'facultad'

    def __str__(self):
        return self.nombre


class Modalidad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'modalidad'

    def __str__(self):
        return self.nombre


class Programa(models.Model):
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT, related_name='programas')
    nombre = models.CharField(max_length=200)
    modalidad = models.ForeignKey(Modalidad, on_delete=models.PROTECT, related_name='programas', null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programa'
        unique_together = ('nombre', 'modalidad')

    def __str__(self):
        return f"{self.nombre} ({self.modalidad})"


class ComponenteFormacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'componente_formacion'

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    programa = models.ForeignKey(Programa, on_delete=models.PROTECT, related_name='cursos')
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    naturaleza = models.CharField(max_length=50, blank=True)
    semestre = models.CharField(max_length=30, blank=True)
    componente_formacion = models.ForeignKey(ComponenteFormacion, on_delete=models.PROTECT, related_name='cursos', null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'curso'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CompetenciaGeneral(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.TextField()
    programa = models.ForeignKey(Programa, on_delete=models.SET_NULL, related_name='competencias_generales', null=True, blank=True)

    class Meta:
        db_table = 'competencia_general'

    def __str__(self):
        return self.codigo


class Rap(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.TextField()
    competencia_general = models.ForeignKey(CompetenciaGeneral, on_delete=models.PROTECT, related_name='raps')
    programa = models.ForeignKey(Programa, on_delete=models.PROTECT, related_name='raps')

    class Meta:
        db_table = 'rap'

    def __str__(self):
        return self.codigo


class Rac(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.TextField()
    rap = models.ForeignKey(Rap, on_delete=models.PROTECT, related_name='racs')

    class Meta:
        db_table = 'rac'

    def __str__(self):
        return self.codigo


class CursoRac(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    rac = models.ForeignKey(Rac, on_delete=models.CASCADE)

    class Meta:
        db_table = 'curso_rac'
        unique_together = ('curso', 'rac')

    def __str__(self):
        return f"{self.curso.codigo} -> {self.rac.codigo}"


class LugarDesarrollo(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)

    class Meta:
        db_table = 'lugar_desarrollo'
        unique_together = ('nombre', 'departamento')

    def __str__(self):
        return f"{self.nombre} ({self.departamento})"


class Periodo(models.Model):
    anio = models.SmallIntegerField()
    numero = models.SmallIntegerField(choices=[(1, '1'), (2, '2')])

    class Meta:
        db_table = 'periodo'
        unique_together = ('anio', 'numero')

    def __str__(self):
        return f"{self.anio}-{self.numero}"


class Corte(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    orden = models.SmallIntegerField(unique=True)

    class Meta:
        db_table = 'corte'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Grupo(models.Model):
    codigo = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'grupo'

    def __str__(self):
        return self.codigo


class MetodoEvaluacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'metodo_evaluacion'

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)

    class Meta:
        db_table = 'estudiante'

    def __str__(self):
        return f"{self.codigo} - {self.apellidos} {self.nombres}"


class Docente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='docente')
    identificacion = models.CharField(max_length=30, unique=True)
    nombre_completo = models.CharField(max_length=200)

    class Meta:
        db_table = 'docente'

    def __str__(self):
        return self.nombre_completo