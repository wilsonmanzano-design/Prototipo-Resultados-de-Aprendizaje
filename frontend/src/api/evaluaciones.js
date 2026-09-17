import client from './client';

export async function obtenerMisOfertas() {
  const { data } = await client.get('/ofertas/');
  return data;
}

export async function obtenerOferta(ofertaId) {
  const { data } = await client.get(`/ofertas/${ofertaId}/`);
  return data;
}

export async function obtenerRacsDeCurso(cursoId) {
  const { data } = await client.get(`/cursos/${cursoId}/racs/`);
  return data;
}

export async function obtenerCortes() {
  const { data } = await client.get('/cortes/');
  return data;
}

export async function obtenerMetodosEvaluacion() {
  const { data } = await client.get('/metodos-evaluacion/');
  return data;
}

export async function obtenerRubricaCriterios() {
  const { data } = await client.get('/rubrica-criterios/');
  return data;
}

export async function obtenerMatriculados(ofertaId, corteId) {
  const { data } = await client.get(`/ofertas/${ofertaId}/matriculados/`, {
    params: { corte: corteId },
  });
  return data;
}

export async function importarEstudiantesExcel(archivo, ofertaId, corteId) {
  const formData = new FormData();
  formData.append('archivo', archivo);
  formData.append('oferta_id', ofertaId);
  formData.append('corte_id', corteId);
  // No fijamos Content-Type a mano: axios detecta FormData y arma el boundary correcto solo.
  const { data } = await client.post('/matricula/importar-excel/', formData);
  return data;
}

export async function diligenciarEvaluacion(payload) {
  const { data } = await client.post('/evaluaciones-rac/diligenciar/', payload);
  return data;
}

export async function obtenerEstadisticasEvaluacion(evaluacionId) {
  const { data } = await client.get(`/evaluaciones-rac/${evaluacionId}/estadisticas/`);
  return data;
}