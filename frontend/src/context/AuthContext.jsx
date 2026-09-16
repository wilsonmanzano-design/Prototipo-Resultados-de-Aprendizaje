import { createContext, useContext, useState, useEffect } from 'react';
import { inicializarCsrf } from '../api/client';
import * as authApi from '../api/auth';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  // Al montar la app: pedir cookie CSRF y verificar si ya hay sesión activa
  useEffect(() => {
    async function inicializar() {
      try {
        await inicializarCsrf();
        const datosUsuario = await authApi.obtenerUsuarioActual();
        setUsuario(datosUsuario);
      } catch {
        setUsuario(null); // no hay sesión activa, es un caso normal
      } finally {
        setCargando(false);
      }
    }
    inicializar();
  }, []);

  async function iniciarSesion(username, password) {
    const datosUsuario = await authApi.login(username, password);
    setUsuario(datosUsuario);
    return datosUsuario;
  }

  async function cerrarSesion() {
    try {
      await authApi.logout();
    } finally {
      setUsuario(null);
    }
  }

  const esAdministrador = usuario?.rol === 'Administrador';
  const esDocente = usuario?.rol === 'Docente';

  return (
    <AuthContext.Provider
      value={{ usuario, cargando, iniciarSesion, cerrarSesion, esAdministrador, esDocente }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (contexto === null) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return contexto;
}