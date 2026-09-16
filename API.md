# API — Plataforma Resultados de Aprendizaje

Base URL local: `http://localhost:8000/api/`

**Autenticación:** todos los endpoints requieren sesión activa salvo los marcados como públicos.
El sistema usa **sesiones de Django con cookies** (no JWT).

**Flujo obligatorio desde el frontend:**
1. `GET /api/auth/csrf/` una vez al cargar la app (establece la cookie `csrftoken`).
2. `POST /api/auth/login/` enviando el header `X-CSRFToken`.
3. Todas las peticiones siguientes deben ir con `credentials: 'include'` (axios: `withCredentials: true`).
4. Todo POST/PUT/PATCH/DELETE debe incluir el header `X-CSRFToken`.

**Roles:** `Administrador` y `Docente` (grupos de Django). El rol viene en `/api/auth/me/`.

---

## 1. Autenticación

### `GET /api/auth/csrf/` — público
Establece la cookie `csrftoken`. Llamar una sola vez al iniciar el frontend.

**Respuesta 200**
```json
{ "detail": "Cookie CSRF establecida." }
```

---

### `POST /api/auth/login/` — público

**Body**
```json
{ "username": "docente_prueba", "password": "***" }
```

**Respuesta 200**
```json
{
  "id": 2,
  "username": "docente_prueba",
  "first_name": "",
  "last_name": "",
  "email": "",
  "rol": "Docente",
  "docente_id": 1
}
```
`rol` puede ser `"Administrador"`, `"Docente"` o `null`.
`docente_id` es `null` si el usuario no tiene perfil Docente asociado.

**Respuesta 401**
```json
{ "detail": "Credenciales invalidas." }
```

---

### `POST /api/auth/logout/` — autenticado
Cierra la sesión. Requiere header `X-CSRFToken`.

**Respuesta 200**
```json
{ "detail": "Sesion cerrada." }
```

---

### `GET /api/auth/me/` — autenticado
Devuelve el usuario de la sesión actual. Úsalo al montar la app para saber si hay sesión activa tras un refresco de página (F5).

**Respuesta 200:** mismo formato que `login`.
**Respuesta 403:** si no hay sesión activa.

---

### `GET /api/auth/solo-admin-ping/` — solo Administrador
Endpoint de prueba del permiso `EsAdministrador`. Sirve de plantilla para futuros endpoints solo-admin.

**200** si el usuario está en el grupo Administrador.
**403** `{ "detail": "Solo un Administrador puede realizar esta accion." }` en caso contrario.

---

## 2. Catálogo curricular (solo lectura)

> La **escritura** de estos catálogos se hace desde Django Admin (`/admin/`), no por API.
> Un `POST` a cualquiera de estos endpoints devuelve `405 Method Not Allowed`.

Todos soportan `GET /` (lista) y `GET /<id>/` (detalle).

| Endpoint | Filtros disponibles |
|---|---|
| `GET /api/programas/` | — |
| `GET /api/cursos/` | `?programa=<id>&activo=<true\|false>` |
| `GET /api/raps/` | — |
| `GET /api/racs/` | `?rap=<id>` |
| `GET /api/modalidades/` | — |
| `GET /api/cortes/` | — |
| `GET /api/grupos/` | — |
| `GET /api/lugares-desarrollo/` | — |
| `GET /api/periodos/` | — |
| `GET /api/metodos-evaluacion/` | — |

### `GET /api/cursos/<id>/racs/`
Devuelve los RAC asociados a ese curso mediante la matriz curricular `curso_rac`.
Es el endpoint que alimenta el selector de RAC en el formulario del docente.

**Respuesta 200**
```json
[
  { "id": 1, "codigo": "RAC1_REDES", "nombre": "...", "rap": 1 }
]
```

### Formatos de respuesta relevantes

**Programa**
```json
{ "id": 1, "nombre": "Ingenieria de Sistemas", "facultad": 1, "facultad_nombre": "Ingenierias", "modalidad": 1 }
```

**Curso**
```json
{
  "id": 1, "codigo": "IS-301", "nombre": "Redes de Computadores",
  "programa": 1, "programa_nombre": "Ingenieria de Sistemas",
  "naturaleza": "Teorico-Practico", "semestre": "III TERCERO", "activo": true
}
```

**Periodo** — incluye `etiqueta` ya formateada (`"2026-1"`)
```json
{ "id": 1, "anio": 2026, "numero": 1, "etiqueta": "2026-1" }
```

---

## 3. Operación académica

### `GET /api/ofertas/` — autenticado
Lista las ofertas académicas. **El alcance depende del rol**: un Administrador ve todas; un Docente ve únicamente las suyas.

**Respuesta 200**
```json
[
  {
    "id": 1,
    "curso": 1, "curso_codigo": "IS-301", "curso_nombre": "Redes de Computadores",
    "docente": 1, "docente_nombre": "Juan Perez",
    "periodo": 1, "periodo_etiqueta": "2026-1",
    "modalidad": 1, "lugar_desarrollo": 1,
    "grupos": ["A", "D"]
  }
]
```

También disponible: `GET /api/ofertas/<id>/`.

---

### `GET /api/ofertas/<oferta_id>/matriculados/?corte=<corte_id>` — autenticado + dueño de la oferta
Estudiantes matriculados (estado `matriculado`) de esa oferta en ese corte.
Es la lista base para construir la tabla de la rúbrica en el frontend.

**Parámetro `corte` obligatorio.**

**Respuesta 200**
```json
[
  {
    "id": 5, "oferta": 1, "estudiante": 3,
    "estudiante_codigo": "2024001", "estudiante_nombre": "Gomez Perez Ana Maria",
    "corte": 1, "estado": "matriculado", "fecha_estado": "2026-09-16"
  }
]
```

**400** si falta el parámetro `corte`.
**403** si el docente no es dueño de la oferta.

---

### `POST /api/matricula/importar-excel/` — autenticado + dueño de la oferta
Carga masiva de estudiantes desde un archivo `.xlsx`.

**Content-Type:** `multipart/form-data`

| Campo | Tipo | Descripción |
|---|---|---|
| `archivo` | file | `.xlsx`, máximo 5 MB |
| `oferta_id` | int | Oferta a la que se matricula |
| `corte_id` | int | Corte al que se matricula |

**Columnas esperadas en la primera fila del Excel:** `Codigo`, `Nombres`, `Apellidos`
(la detección no distingue mayúsculas ni tildes).

**Comportamiento:**
- Estudiantes ya existentes (mismo código) no se duplican: se reutilizan.
- Matrículas ya existentes no se duplican. **La operación es idempotente.**
- Las filas completamente vacías se ignoran en silencio.
- Un error en una fila **no detiene** el proceso: se reporta y continúa con las demás.

**Respuesta 200** (sin errores) o **207 Multi-Status** (éxito parcial)
```json
{
  "estudiantes_creados": 3,
  "estudiantes_existentes": 1,
  "matriculas_creadas": 3,
  "matriculas_existentes": 1,
  "errores": [
    { "fila": 4, "detalle": "El codigo del estudiante esta vacio." }
  ],
  "total_filas_procesadas": 5
}
```

**400** si falta el archivo, la extensión no es `.xlsx`, supera 5 MB, o faltan `oferta_id`/`corte_id`.
**403** si el docente no es dueño de la oferta.

---

## 4. Rúbrica y evaluación

### `GET /api/rubrica-criterios/` — autenticado
Catálogo de criterios de rúbrica con sus niveles anidados. Con esto el frontend pinta el formulario completo sin peticiones adicionales.

**Respuesta 200**
```json
[
  {
    "id": 1,
    "nombre": "Dominio del Tema",
    "niveles": [
      { "id": 1, "nombre": "Excelente", "descripcion": "...", "valor_min": "4.50", "valor_max": "5.00" },
      { "id": 2, "nombre": "Satisfactorio", "descripcion": "...", "valor_min": "3.50", "valor_max": "4.49" },
      { "id": 3, "nombre": "Mejorable", "descripcion": "...", "valor_min": "3.00", "valor_max": "3.49" },
      { "id": 4, "nombre": "Insuficiente", "descripcion": "...", "valor_min": "0.00", "valor_max": "2.99" }
    ]
  }
]
```

---

### `GET /api/evaluaciones-rac/` — autenticado
Evaluaciones de RAC ya diligenciadas. Alcance por rol: Administrador ve todas; Docente solo las de sus ofertas.

**Filtros:** `?oferta=<id>&rac=<id>&corte=<id>`

**Respuesta 200**
```json
[
  {
    "id": 1, "oferta": 1,
    "rac": 1, "rac_codigo": "RAC1_REDES",
    "corte": 1, "corte_nombre": "Primer Corte",
    "metodo_evaluacion": 1,
    "fecha_diligenciamiento": "2026-09-16"
  }
]
```

---

### `POST /api/evaluaciones-rac/diligenciar/` — autenticado + dueño de la oferta

**Endpoint central del sistema.** Guarda, en una sola transacción atómica: la evaluación de RAC, la rúbrica de todos los estudiantes, y el análisis cualitativo.

Es **idempotente**: reenviar el mismo payload actualiza los datos existentes en lugar de duplicarlos (usa `get_or_create` / `update_or_create`).

**Body**
```json
{
  "oferta_id": 1,
  "rac_id": 1,
  "corte_id": 1,
  "metodo_evaluacion_id": 1,
  "estudiantes": [
    {
      "estudiante_id": 3,
      "respuestas": [
        { "criterio_id": 1, "nivel_id": 1 },
        { "criterio_id": 2, "nivel_id": 5 },
        { "criterio_id": 3, "nivel_id": 9 },
        { "criterio_id": 4, "nivel_id": 13 }
      ]
    }
  ],
  "analisis": {
    "elementos_impidieron": "",
    "elementos_permitieron": "Buena disposicion del grupo",
    "elementos_medios_infra": "",
    "propuesta_metodologia": "",
    "propuesta_contenido": "",
    "propuesta_situacion_curso": ""
  }
}
```

**Notas importantes:**
- El frontend **no envía notas numéricas**, solo el `nivel_id` elegido por criterio. El backend traduce el nivel a `valor_asignado` (punto medio entre `valor_min` y `valor_max` del nivel).
- `valoracion_final` de cada estudiante la calcula automáticamente un **trigger de PostgreSQL** (`trg_recalcular_valoracion`) al guardar las respuestas. Django no la calcula.
- Todos los campos de `analisis` son opcionales y admiten cadena vacía.

**Respuesta 201**
```json
{
  "id": 1, "oferta": 1, "rac": 1, "rac_codigo": "RAC1_REDES",
  "corte": 1, "corte_nombre": "Primer Corte",
  "metodo_evaluacion": 1, "fecha_diligenciamiento": "2026-09-16"
}
```

**400** si el payload no valida (campos faltantes, `nivel_id` inexistente).
**403** si el docente no es dueño de la oferta.

---

### `GET /api/evaluaciones-rac/<id>/estadisticas/` — autenticado

Estadísticos calculados por la vista SQL `vw_evaluacion_estadistica` directamente en PostgreSQL.
Todos los valores son **derivados**, nunca se capturan a mano.

**Respuesta 200**
```json
{
  "matriculados": 30,
  "participantes": 28,
  "porcentaje_participacion": "93.33",
  "competentes": 24,
  "no_competentes": 4,
  "media": "3.85",
  "mediana": "4.00",
  "desviacion_estandar": "0.62",
  "valor_mayor": "4.75",
  "valor_menor": "2.25"
}
```

**Criterio de competencia:** `valoracion_final >= 3.0`.
**404** `{ "detail": "Aun no hay datos de rubrica para esta evaluacion." }` si no se ha diligenciado nada.

---

## 5. Códigos de estado usados

| Código | Significado en esta API |
|---|---|
| `200` | Operación exitosa |
| `201` | Recurso creado (diligenciamiento) |
| `207` | Éxito parcial — importación con errores fila a fila |
| `400` | Payload o parámetros inválidos |
| `401` | Credenciales inválidas en login |
| `403` | Sin sesión, o sin permiso sobre el recurso (rol o propiedad de la oferta) |
| `404` | Recurso no encontrado |
| `405` | Método no permitido (ej. POST a catálogo de solo lectura) |

---

## 6. Pendiente de implementar

- **Fase 10 — Reportes:** `POST /api/reportes/generar/` (NLG determinístico con plantillas).
- **Fase 9 — Dashboard:** endpoints de agregación por curso/programa/corte con los 9 filtros
  (RAC, RAP, Curso, Periodo, Año, Corte, Lugar de desarrollo, Programa, Modalidad).
