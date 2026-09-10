from django.db import migrations

SQL_CREAR_FUNCION_Y_TRIGGER = """
CREATE OR REPLACE FUNCTION fn_recalcular_valoracion_final() RETURNS TRIGGER AS $$
BEGIN
    UPDATE rubrica_estudiante
    SET valoracion_final = (
        SELECT ROUND(AVG(valor_asignado), 2)
        FROM rubrica_respuesta
        WHERE rubrica_estudiante_id = COALESCE(NEW.rubrica_estudiante_id, OLD.rubrica_estudiante_id)
    )
    WHERE id = COALESCE(NEW.rubrica_estudiante_id, OLD.rubrica_estudiante_id);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_recalcular_valoracion
AFTER INSERT OR UPDATE OR DELETE ON rubrica_respuesta
FOR EACH ROW EXECUTE FUNCTION fn_recalcular_valoracion_final();
"""

SQL_ELIMINAR_FUNCION_Y_TRIGGER = """
DROP TRIGGER IF EXISTS trg_recalcular_valoracion ON rubrica_respuesta;
DROP FUNCTION IF EXISTS fn_recalcular_valoracion_final();
"""


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0001_initial'),  # ajusta este numero al de tu ultima migracion real
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_CREAR_FUNCION_Y_TRIGGER,
            reverse_sql=SQL_ELIMINAR_FUNCION_Y_TRIGGER,
        ),
    ]