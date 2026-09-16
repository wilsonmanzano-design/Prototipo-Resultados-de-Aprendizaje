import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout() {
  const { usuario, cerrarSesion, esAdministrador, esDocente } = useAuth();
  const navigate = useNavigate();

  async function manejarLogout() {
    await cerrarSesion();
    navigate('/login', { replace: true });
  }

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif' }}>
      <nav
        style={{
          display: 'flex', alignItems: 'center', gap: '1.25rem',
          padding: '0.75rem 1.5rem', borderBottom: '1px solid #ddd', background: '#fafafa',
        }}
      >
        <strong>Resultados de Aprendizaje</strong>

        {esDocente && <Link to="/mis-evaluaciones">Mis Evaluaciones</Link>}

        {esAdministrador && (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <a href="http://localhost:8000/admin/" target="_blank" rel="noreferrer">
              Administración
            </a>
          </>
        )}

        <span style={{ marginLeft: 'auto', color: '#666', fontSize: '0.9rem' }}>
          {usuario?.username} ({usuario?.rol})
        </span>
        <button onClick={manejarLogout}>Salir</button>
      </nav>

      <main style={{ padding: '1.5rem' }}>
        <Outlet />
      </main>
    </div>
  );
}