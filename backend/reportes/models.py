from django.db import models
from django.contrib.auth.models import User


class PlantillaReporte(models.Model):
    TIPO_CHOICES = [('curso', 'Curso'), ('programa', 'Programa'), ('docente', 'Docente')]

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    contenido_plantilla = models.TextField()
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'plantilla_reporte'

    def __str__(self):
        return self.nombre


class ReporteGenerado(models.Model):
    plantilla = models.ForeignKey(PlantillaReporte, on_delete=models.PROTECT, related_name='reportes')
    alcance_tipo = models.CharField(max_length=30)
    alcance_id = models.IntegerField()
    contenido_generado = models.TextField()
    generado_en = models.DateTimeField(auto_now_add=True)
    generado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='reportes_generados')

    class Meta:
        db_table = 'reporte_generado'

    def __str__(self):
        return f"Reporte {self.id} - {self.plantilla.nombre}"