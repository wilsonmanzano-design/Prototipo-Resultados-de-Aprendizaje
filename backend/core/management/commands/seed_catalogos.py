from django.core.management.base import BaseCommand
from core.models import Corte
from evaluaciones.models import RubricaCriterio, RubricaNivel
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = (
        'Puebla los catálogos fijos del sistema (cortes y criterios de rúbrica). '
        'Es idempotente: se puede correr varias veces sin duplicar datos.'
    )

    def handle(self, *args, **options):
        grupos = ['Administrador', 'Docente']
        for nombre_grupo in grupos:
                grupo, created = Group.objects.get_or_create(name=nombre_grupo)
                self.stdout.write(self._msg(grupo, created, 'Grupo'))
        cortes = [
            ('Primer Corte', 1),
            ('Segundo Corte', 2),
            ('Tercer Corte', 3),
        ]
        for nombre, orden in cortes:
            obj, created = Corte.objects.get_or_create(nombre=nombre, defaults={'orden': orden})
            self.stdout.write(self._msg(obj, created, 'Corte'))

        criterios = [
            'Dominio del Tema',
            'Habilidades de Comunicación',
            'Participación y Colaboración',
            'Calidad del Trabajo',
        ]
        niveles_base = [
            ('Excelente', 4.5, 5.0),
            ('Satisfactorio', 3.5, 4.49),
            ('Mejorable', 3.0, 3.49),
            ('Insuficiente', 0.0, 2.99),
        ]
        for nombre_criterio in criterios:
            criterio, created = RubricaCriterio.objects.get_or_create(nombre=nombre_criterio)
            self.stdout.write(self._msg(criterio, created, 'Criterio'))
            for nombre_nivel, vmin, vmax in niveles_base:
                nivel, created = RubricaNivel.objects.get_or_create(
                    criterio=criterio,
                    nombre=nombre_nivel,
                    defaults={
                        'descripcion': f'Descripción pendiente de ajustar para "{nombre_criterio} - {nombre_nivel}".',
                        'valor_min': vmin,
                        'valor_max': vmax,
                    }
                )
                self.stdout.write(self._msg(nivel, created, 'Nivel'))

        self.stdout.write(self.style.SUCCESS('Catálogos poblados correctamente.'))

    def _msg(self, obj, created, tipo):
        estado = 'creado' if created else 'ya existía'
        return f'{tipo} "{obj}" -> {estado}'