import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const { iniciarSesion } = useAuth();
  const navigate = useNavigate();

  async function manejarSubmit(evento) {
    evento.preventDefault();
    setError('');
    setEnviando(true);
    try {
      const usuario = await iniciarSesion(username, password);
      navigate(usuario.rol === 'Administrador' ? '/dashboard' : '/mis-evaluaciones', { replace: true });
    } catch (err) {
      setError(
        err.response?.status === 401
          ? 'Usuario o contraseña incorrectos.'
          : 'No se pudo conectar con el servidor. Intenta de nuevo.'
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: '4rem auto', fontFamily: 'system-ui, sans-serif' }}>
      <h1 style={{ fontSize: '1.4rem' }}>Resultados de Aprendizaje</h1>
      <p style={{ color: '#666', marginTop: 0 }}>Inicia sesión para continuar</p>

      <form onSubmit={manejarSubmit}>
        <label style={{ display: 'block', marginBottom: '0.75rem' }}>
          Usuario
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
          />
        </label>

        <label style={{ display: 'block', marginBottom: '1rem' }}>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '0.5rem', marginTop: '0.25rem' }}
          />
        </label>

        {error && (
          <div style={{ background: '#fee', color: '#a00', padding: '0.5rem', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={enviando}
          style={{ width: '100%', padding: '0.6rem', cursor: enviando ? 'wait' : 'pointer' }}
        >
          {enviando ? 'Ingresando...' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
}