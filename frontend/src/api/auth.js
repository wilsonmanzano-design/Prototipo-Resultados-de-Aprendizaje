import client from './client';

export async function login(username, password) {
  const { data } = await client.post('/auth/login/', { username, password });
  return data;
}

export async function logout() {
  await client.post('/auth/logout/');
}

export async function obtenerUsuarioActual() {
  const { data } = await client.get('/auth/me/');
  return data;
}