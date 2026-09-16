import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RutaPrivada({ children, rolRequerido = null }) {
  const { usuario, cargando } = useAuth();

  if (cargando) {
    return <div style={{ padding: '2rem' }}>Verificando sesión...</div>;
  }

  if (!usuario) {
    return <Navigate to="/login" replace />;
  }

  if (rolRequerido && usuario.rol !== rolRequerido) {
    return <Navigate to="/no-autorizado" replace />;
  }

  return children;
}