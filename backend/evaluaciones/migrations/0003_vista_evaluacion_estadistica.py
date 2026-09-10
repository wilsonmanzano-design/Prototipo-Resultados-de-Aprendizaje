from django.db import migrations

SQL_CREAR_VISTA = """
CREATE VIEW vw_evaluacion_estadistica AS
SELECT
    er.id AS evaluacion_rac_id,
    er.oferta_id,
    er.rac_id,
    er.corte_id,
    COUNT(DISTINCT m.estudiante_id) FILTER (WHERE m.estado = 'matriculado') AS matriculados,
    COUNT(DISTINCT re.estudiante_id) AS participantes,
    ROUND(
        COUNT(DISTINCT re.estudiante_id)::numeric
        / NULLIF(COUNT(DISTINCT m.estudiante_id) FILTER (WHERE m.estado = 'matriculado'), 0) * 100, 2
    ) AS porcentaje_participacion,
    COUNT(*) FILTER (WHERE re.valoracion_final >= 3.0) AS competentes,
    COUNT(*) FILTER (WHERE re.valoracion_final < 3.0) AS no_competentes,
    ROUND(AVG(re.valoracion_final)::numeric, 2) AS media,
    ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY re.valoracion_final))::numeric, 2) AS mediana,
    ROUND(STDDEV_SAMP(re.valoracion_final)::numeric, 2) AS desviacion_estandar,
    MAX(re.valoracion_final) AS valor_mayor,
    MIN(re.valoracion_final) AS valor_menor
FROM evaluacion_rac er
LEFT JOIN matricula m ON m.oferta_id = er.oferta_id AND m.corte_id = er.corte_id
LEFT JOIN rubrica_estudiante re ON re.evaluacion_rac_id = er.id
GROUP BY er.id, er.oferta_id, er.rac_id, er.corte_id;
"""

SQL_ELIMINAR_VISTA = "DROP VIEW IF EXISTS vw_evaluacion_estadistica;"


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0002_trigger_valoracion_final'),  # ajusta al nombre real generado en el paso anterior
    ]

    operations = [
        migrations.RunSQL(sql=SQL_CREAR_VISTA, reverse_sql=SQL_ELIMINAR_VISTA),
    ]