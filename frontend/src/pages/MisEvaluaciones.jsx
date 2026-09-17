import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { obtenerMisOfertas } from '../api/evaluaciones';

export default function MisEvaluaciones() {
  const [ofertas, setOfertas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function cargar() {
      try {
        const datos = await obtenerMisOfertas();
        setOfertas(datos);
      } catch {
        setError('No se pudieron cargar tus ofertas académicas.');
      } finally {
        setCargando(false);
      }
    }
    cargar();
  }, []);

  if (cargando) return <p>Cargando ofertas...</p>;
  if (error) return <p style={{ color: '#a00' }}>{error}</p>;
  if (ofertas.length === 0) {
    return <p>No tienes ofertas académicas asignadas todavía. Contacta al Administrador.</p>;
  }

  return (
    <div>
      <h2>Mis Evaluaciones</h2>
      <p style={{ color: '#666' }}>Selecciona una oferta académica para diligenciar una evaluación de RAC.</p>

      <div style={{ display: 'grid', gap: '0.75rem', maxWidth: 640 }}>
        {ofertas.map((oferta) => (
          <button
            key={oferta.id}
            onClick={() => navigate(`/diligenciar/${oferta.id}`)}
            style={{
              textAlign: 'left', padding: '1rem', border: '1px solid #ddd',
              borderRadius: 6, cursor: 'pointer', background: 'white',
            }}
          >
            <strong>{oferta.curso_codigo} - {oferta.curso_nombre}</strong>
            <div style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.25rem' }}>
              Periodo {oferta.periodo_etiqueta} · Grupo(s) {oferta.grupos.join(', ') || 'sin grupo'}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}