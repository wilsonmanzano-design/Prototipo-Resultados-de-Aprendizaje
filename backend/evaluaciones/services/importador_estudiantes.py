from openpyxl import load_workbook
from django.db import transaction
from core.models import Estudiante
from evaluaciones.models import Matricula

COLUMNAS_ESPERADAS = ['codigo', 'nombres', 'apellidos']


def _normalizar(texto):
    return str(texto).strip().lower().replace('ó', 'o').replace('í', 'i') if texto is not None else ''


def importar_estudiantes_desde_excel(archivo, oferta_id, corte_id):
    """Lee un .xlsx con columnas Codigo/Nombres/Apellidos y matricula a los estudiantes
    en la oferta y corte indicados. Devuelve un resumen detallado fila por fila.

    Nunca lanza excepcion por una fila mala: la reporta y continua con las demas.
    """
    resumen = {
        'estudiantes_creados': 0,
        'estudiantes_existentes': 0,
        'matriculas_creadas': 0,
        'matriculas_existentes': 0,
        'errores': [],
        'total_filas_procesadas': 0,
    }

    try:
        wb = load_workbook(archivo, data_only=True, read_only=True)
    except Exception as exc:
        resumen['errores'].append({'fila': None, 'detalle': f'No se pudo leer el archivo: {exc}'})
        return resumen

    ws = wb.active

    # Localizar encabezados en la primera fila
    filas = ws.iter_rows(values_only=True)
    try:
        encabezados_raw = next(filas)
    except StopIteration:
        resumen['errores'].append({'fila': None, 'detalle': 'El archivo esta vacio.'})
        return resumen

    encabezados = [_normalizar(c) for c in encabezados_raw]
    indices = {}
    for col in COLUMNAS_ESPERADAS:
        if col not in encabezados:
            resumen['errores'].append({
                'fila': 1,
                'detalle': f'Falta la columna obligatoria "{col}". Encabezados encontrados: {encabezados}'
            })
            return resumen
        indices[col] = encabezados.index(col)

    for numero_fila, fila in enumerate(filas, start=2):
        # Saltar filas completamente vacias sin reportarlas como error
        if fila is None or all(c is None or str(c).strip() == '' for c in fila):
            continue

        resumen['total_filas_procesadas'] += 1

        try:
            codigo = str(fila[indices['codigo']]).strip() if fila[indices['codigo']] is not None else ''
            nombres = str(fila[indices['nombres']]).strip() if fila[indices['nombres']] is not None else ''
            apellidos = str(fila[indices['apellidos']]).strip() if fila[indices['apellidos']] is not None else ''

            if not codigo:
                resumen['errores'].append({'fila': numero_fila, 'detalle': 'El codigo del estudiante esta vacio.'})
                continue
            if not nombres or not apellidos:
                resumen['errores'].append({'fila': numero_fila, 'detalle': f'Codigo {codigo}: nombres o apellidos vacios.'})
                continue

            with transaction.atomic():
                estudiante, creado = Estudiante.objects.get_or_create(
                    codigo=codigo,
                    defaults={'nombres': nombres, 'apellidos': apellidos},
                )
                if creado:
                    resumen['estudiantes_creados'] += 1
                else:
                    resumen['estudiantes_existentes'] += 1

                _, matricula_creada = Matricula.objects.get_or_create(
                    oferta_id=oferta_id,
                    estudiante=estudiante,
                    corte_id=corte_id,
                    defaults={'estado': 'matriculado'},
                )
                if matricula_creada:
                    resumen['matriculas_creadas'] += 1
                else:
                    resumen['matriculas_existentes'] += 1

        except Exception as exc:
            resumen['errores'].append({'fila': numero_fila, 'detalle': f'Error inesperado: {exc}'})
            continue

    wb.close()
    return resumen