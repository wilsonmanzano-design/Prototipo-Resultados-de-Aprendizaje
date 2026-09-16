import axios from 'axios';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true, // envía y recibe las cookies de sesión de Django
  headers: { 'Content-Type': 'application/json' },
});

// Lee el valor de una cookie del navegador por nombre
function leerCookie(nombre) {
  const valor = `; ${document.cookie}`;
  const partes = valor.split(`; ${nombre}=`);
  if (partes.length === 2) return partes.pop().split(';').shift();
  return null;
}

// Interceptor: adjunta el token CSRF en toda petición que modifique datos
client.interceptors.request.use((config) => {
  const metodosInseguros = ['post', 'put', 'patch', 'delete'];
  if (metodosInseguros.includes(config.method)) {
    const csrfToken = leerCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }
  return config;
});

// Llamar una sola vez al arrancar la app para que Django emita la cookie csrftoken
export async function inicializarCsrf() {
  await client.get('/auth/csrf/');
}

export default client;