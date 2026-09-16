import { Link } from 'react-router-dom';

export default function NoAutorizado() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}>
      <h2>Acceso no autorizado</h2>
      <p>Tu rol no tiene permiso para ver esta sección.</p>
      <Link to="/login">Volver al inicio</Link>
    </div>
  );
}