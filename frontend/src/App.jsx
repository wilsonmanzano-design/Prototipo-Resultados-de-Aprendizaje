import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import RutaPrivada from './components/RutaPrivada';
import Layout from './components/Layout';
import Login from './pages/Login';
import MisEvaluaciones from './pages/MisEvaluaciones';
import Dashboard from './pages/Dashboard';
import NoAutorizado from './pages/NoAutorizado';

function RedireccionInicial() {
  const { usuario, cargando } = useAuth();
  if (cargando) return <div style={{ padding: '2rem' }}>Cargando...</div>;
  if (!usuario) return <Navigate to="/login" replace />;
  return <Navigate to={usuario.rol === 'Administrador' ? '/dashboard' : '/mis-evaluaciones'} replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/no-autorizado" element={<NoAutorizado />} />

          <Route element={<Layout />}>
            <Route
              path="/mis-evaluaciones"
              element={
                <RutaPrivada rolRequerido="Docente">
                  <MisEvaluaciones />
                </RutaPrivada>
              }
            />
            <Route
              path="/dashboard"
              element={
                <RutaPrivada rolRequerido="Administrador">
                  <Dashboard />
                </RutaPrivada>
              }
            />
          </Route>

          <Route path="/" element={<RedireccionInicial />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}