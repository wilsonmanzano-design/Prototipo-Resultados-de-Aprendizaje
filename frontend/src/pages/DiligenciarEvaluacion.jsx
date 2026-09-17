import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  obtenerOferta, obtenerRacsDeCurso, obtenerCortes, obtenerMetodosEvaluacion,
  obtenerRubricaCriterios, obtenerMatriculados, importarEstudiantesExcel,
  diligenciarEvaluacion, obtenerEstadisticasEvaluacion,
} from '../api/evaluaciones';

export default function DiligenciarEvaluacion() {
  const { ofertaId } = useParams();

  // Datos de catálogo, se cargan una sola vez al montar
  const [oferta, setOferta] = useState(null);
  const [racs, setRacs] = useState([]);
  const [cortes, setCortes] = useState([]);
  const [metodos, setMetodos] = useState([]);
  const [criterios, setCriterios] = useState([]);
  const [cargandoInicial, setCargandoInicial] = useState(true);
  const [errorInicial, setErrorInicial] = useState('');

  // Selección del docente
  const [racId, setRacId] = useState('');
  const [corteId, setCorteId] = useState('');
  const [metodoId, setMetodoId] = useState('');

  // Estudiantes matriculados y respuestas de rúbrica
  const [estudiantes, setEstudiantes] = useState([]);
  const [cargandoEstudiantes, setCargandoEstudiantes] = useState(false);
  const [respuestas, setRespuestas] = useState({});
  const [analisis, setAnalisis] = useState({
    elementos_permitieron: '', elementos_impidieron: '',
    elementos_medios_infra: '', propuesta_metodologia: '',
    propuesta_contenido: '', propuesta_situacion_curso: '',
  });

  // Importación de Excel
  const [archivoExcel, setArchivoExcel] = useState(null);
  const [importando, setImportando] = useState(false);
  const [resumenImportacion, setResumenImportacion] = useState(null);

  // Guardado
  const [guardando, setGuardando] = useState(false);
  const [erroresValidacion, setErroresValidacion] = useState([]);
  const [resultadoGuardado, setResultadoGuardado] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);

  useEffect(() => {
    async function cargarInicial() {
      try {
        const datosOferta = await obtenerOferta(ofertaId);
        const [racsData, cortesData, metodosData, criteriosData] = await Promise.all([
          obtenerRacsDeCurso(datosOferta.curso),
          obtenerCortes(),
          obtenerMetodosEvaluacion(),
          obtenerRubricaCriterios(),
        ]);
        setOferta(datosOferta);
        setRacs(racsData);
        setCortes(cortesData);
        setMetodos(metodosData);
        setCriterios(criteriosData);
      } catch {
        setErrorInicial('No se pudo cargar la información de esta oferta académica.');
      } finally {
        setCargandoInicial(false);
      }
    }
    cargarInicial();
  }, [ofertaId]);

  async function cargarEstudiantes() {
    if (!corteId) return;
    setCargandoEstudiantes(true);
    setResultadoGuardado(null);
    setEstadisticas(null);
    try {
      const datos = await obtenerMatriculados(ofertaId, corteId);
      setEstudiantes(datos);
      setRespuestas({});
    } catch {
      setErrorInicial('No se pudieron cargar los estudiantes matriculados.');
    } finally {
      setCargandoEstudiantes(false);
    }
  }

  async function manejarImportarExcel() {
    if (!archivoExcel || !corteId) return;
    setImportando(true);
    setResumenImportacion(null);
    try {
      const resumen = await importarEstudiantesExcel(archivoExcel, ofertaId, corteId);
      setResumenImportacion({ exito: true, datos: resumen });
      await cargarEstudiantes(); // refresca la tabla con los recién importados
    } catch (err) {
      setResumenImportacion({
        exito: false,
        mensaje: err.response?.data?.detail || 'Error al importar el archivo.',
      });
    } finally {
      setImportando(false);
    }
  }

  function seleccionarNivel(estudianteId, criterioId, nivelId) {
    setRespuestas((prev) => ({
      ...prev,
      [estudianteId]: { ...prev[estudianteId], [criterioId]: Number(nivelId) },
    }));
  }

  function manejarCambioAnalisis(campo, valor) {
    setAnalisis((prev) => ({ ...prev, [campo]: valor }));
  }

  async function manejarGuardar() {
    // Validación: cada estudiante debe tener los 4 criterios respondidos
    const faltantes = [];
    estudiantes.forEach((m) => {
      const respuestasEstudiante = respuestas[m.estudiante] || {};
      const criteriosSinResponder = criterios.filter((c) => !respuestasEstudiante[c.id]);
      if (criteriosSinResponder.length > 0) {
        faltantes.push(`${m.estudiante_nombre} (${criteriosSinResponder.length} criterio(s) sin calificar)`);
      }
    });

    if (!racId || !corteId || !metodoId) {
      setErroresValidacion(['Selecciona RAC, Corte y Método de evaluación antes de guardar.']);
      return;
    }
    if (estudiantes.length === 0) {
      setErroresValidacion(['No hay estudiantes cargados para evaluar.']);
      return;
    }
    if (faltantes.length > 0) {
      setErroresValidacion(faltantes);
      return;
    }

    setErroresValidacion([]);
    setGuardando(true);
    setResultadoGuardado(null);

    const payload = {
      oferta_id: Number(ofertaId),
      rac_id: Number(racId),
      corte_id: Number(corteId),
      metodo_evaluacion_id: Number(metodoId),
      estudiantes: estudiantes.map((m) => ({
        estudiante_id: m.estudiante,
        respuestas: criterios.map((c) => ({
          criterio_id: c.id,
          nivel_id: respuestas[m.estudiante][c.id],
        })),
      })),
      analisis,
    };

    try {
      const evaluacionGuardada = await diligenciarEvaluacion(payload);
      setResultadoGuardado({ exito: true, evaluacion: evaluacionGuardada });
      const stats = await obtenerEstadisticasEvaluacion(evaluacionGuardada.id);
      setEstadisticas(stats);
    } catch (err) {
      setResultadoGuardado({
        exito: false,
        mensaje: err.response?.data?.detail || 'No se pudo guardar la evaluación.',
      });
    } finally {
      setGuardando(false);
    }
  }

  if (cargandoInicial) return <p>Cargando...</p>;
  if (errorInicial) return <p style={{ color: '#a00' }}>{errorInicial}</p>;

  return (
    <div style={{ maxWidth: 900 }}>
      <Link to="/mis-evaluaciones">&larr; Volver a mis evaluaciones</Link>
      <h2>{oferta.curso_codigo} - {oferta.curso_nombre}</h2>
      <p style={{ color: '#666' }}>Periodo {oferta.periodo_etiqueta}</p>

      {/* --- Selección de RAC, Corte y Método --- */}
      <fieldset style={{ marginBottom: '1.5rem', padding: '1rem' }}>
        <legend>1. Selecciona el alcance de la evaluación</legend>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <label>
            RAC
            <select value={racId} onChange={(e) => setRacId(e.target.value)} style={{ display: 'block' }}>
              <option value="">-- Selecciona --</option>
              {racs.map((r) => (
                <option key={r.id} value={r.id}>{r.codigo}</option>
              ))}
            </select>
          </label>
          <label>
            Corte
            <select value={corteId} onChange={(e) => setCorteId(e.target.value)} style={{ display: 'block' }}>
              <option value="">-- Selecciona --</option>
              {cortes.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </label>
          <label>
            Método de evaluación
            <select value={metodoId} onChange={(e) => setMetodoId(e.target.value)} style={{ display: 'block' }}>
              <option value="">-- Selecciona --</option>
              {metodos.map((m) => (
                <option key={m.id} value={m.id}>{m.nombre}</option>
              ))}
            </select>
          </label>
        </div>
      </fieldset>

      {/* --- Importar y cargar estudiantes --- */}
      <fieldset style={{ marginBottom: '1.5rem', padding: '1rem' }}>
        <legend>2. Estudiantes matriculados</legend>

        <button onClick={cargarEstudiantes} disabled={!corteId || cargandoEstudiantes}>
          {cargandoEstudiantes ? 'Cargando...' : 'Cargar estudiantes matriculados en este corte'}
        </button>

        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px dashed #ccc' }}>
          <p style={{ margin: '0 0 0.5rem', color: '#666' }}>
            ¿Faltan estudiantes? Importa un Excel (columnas: Codigo, Nombres, Apellidos):
          </p>
          <input
            type="file"
            accept=".xlsx"
            onChange={(e) => setArchivoExcel(e.target.files[0])}
          />
          <button
            onClick={manejarImportarExcel}
            disabled={!archivoExcel || !corteId || importando}
            style={{ marginLeft: '0.5rem' }}
          >
            {importando ? 'Importando...' : 'Importar'}
          </button>

          {resumenImportacion && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.9rem' }}>
              {resumenImportacion.exito ? (
                <div style={{ background: '#eef9ee', padding: '0.5rem', borderRadius: 4 }}>
                  <div>
                    Creados: {resumenImportacion.datos.estudiantes_creados} · Ya existían: {resumenImportacion.datos.estudiantes_existentes} ·
                    Matrículas nuevas: {resumenImportacion.datos.matriculas_creadas}
                  </div>
                  {resumenImportacion.datos.errores.length > 0 && (
                    <ul style={{ color: '#a00', marginTop: '0.5rem' }}>
                      {resumenImportacion.datos.errores.map((e, i) => (
                        <li key={i}>Fila {e.fila}: {e.detalle}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : (
                <div style={{ color: '#a00' }}>{resumenImportacion.mensaje}</div>
              )}
            </div>
          )}
        </div>
      </fieldset>

      {/* Aquí sigue la tabla de rúbrica y el resto del formulario (Paso 8.4) */}
    </div>
  );
}