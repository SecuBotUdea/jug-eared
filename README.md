# jug-eared

Servicio de routing y registro de equipos del ecosistema **SecuBot-UdeA**. Actúa como hub central: resuelve qué equipo es dueño de cada repositorio, despacha alertas normalizadas a `Secubot-` (gamificación) y `Discord` (notificaciones), y orquesta el flujo de rescan cuando un usuario solicita verificar una alerta.

---

## Rol en la arquitectura

```
parser-dependabot ──► POST /alerts/      ──► jug-eared ──► Secubot-  (POST /events/rescan_result)
                                                      └──► Discord   (POST /webhook/notify)

Discord (bot)     ──► POST /rescan/      ──► jug-eared ──► parser-dependabot (POST /verify/{alert_id})

Secubot-          ──► POST /gamification/ ──► jug-eared ──► Discord  (POST /webhook/notify)
```

jug-eared no contiene lógica de negocio. No normaliza alertas, no calcula puntos ni se comunica directamente con GitHub. Solo resuelve equipos y enruta.

---

## Endpoints

### `POST /alerts/`

Recibe una alerta normalizada desde `parser-dependabot`. Resuelve el equipo propietario y despacha en background hacia `Secubot-` y `Discord`.

**Headers:**
| Header | Descripción |
|---|---|
| `X-Source` | Fuente de la alerta (`dependabot`, `owasp_zap`, `trivy_sast`). Opcional, para trazabilidad. |

**Body (`IncomingAlert`):**
```json
{
  "alert_id": "dependabot-pangoaguirre-learndependabot-12",
  "source_type": "dependabot",
  "source_id": "12",
  "title": "CVE-2024-XXXX in lodash",
  "severity": "high",
  "status": "open",
  "component": "lodash",
  "location": "package.json",
  "external_references_score": 0.85,
  "normalized_payload": {}
}
```

**Resolución del equipo:** extrae `{owner}-{repo}` del `alert_id` (todo entre el primer y el último segmento separados por `-`) y busca en MongoDB el equipo registrado para ese repositorio. Si no hay coincidencia, el alert se descarta con un warning en logs.

**Respuestas:**
- `202 {"status": "received", "alert_id": "..."}` — encolado para routing
- `422` — payload inválido

---

### `POST /rescan/`

Recibe una solicitud de rescan desde el bot de Discord. Cachea el `user_id` en MongoDB y despacha en background hacia `parser-dependabot` para que dispare la verificación.

**Body (`RescanRequest`):**
```json
{
  "action": "rescan",
  "alert_id": "dependabot-pangoaguirre-learndependabot-12",
  "guild_id": "123456789",
  "user_id": "987654321"
}
```

**Comportamiento:** guarda `(alert_id, user_id, guild_id)` en la colección `rescans` de MongoDB. Cuando `parser-dependabot` re-entrega el webhook del alert resuelto, `route_alert` consume ese registro para atribuir los puntos al usuario correcto.

**Respuestas:**
- `202 {"status": "received", "alert_id": "..."}` — rescan encolado
- `422` — payload inválido

---

### `POST /gamification/`

Recibe el resultado de puntuación desde `Secubot-` y reenvía la notificación a `Discord`.

**Body (`GamificationResult`):**
```json
{
  "alert_id": "dependabot-pangoaguirre-learndependabot-12",
  "team_id": "team-abc",
  "user_id": "987654321",
  "points_awarded": true,
  "points": 135,
  "message": "¡Resolviste una alerta crítica!"
}
```

**Respuestas:**
- `202 {"status": "received", "alert_id": "..."}` — notificación encolada

---

### `POST /teams/`

Registra un equipo en el sistema.

**Body (`TeamRegisterRequest`):**
```json
{
  "team_id": "team-abc",
  "name": "Equipo Alpha",
  "repository": "pangoaguirre-learndependabot",
  "github_token": "ghp_xxxx"
}
```

El campo `repository` debe seguir el formato `{owner}-{repo}` (con guión, no slash), que es el identificador que `parser-dependabot` y `jug-eared` usan para resolver equipos.

**Respuestas:**
- `201` — equipo registrado
- `422` — payload inválido

---

### `DELETE /teams/{repository}`

Elimina un equipo por su `repository`.

- `204` — eliminado
- `404` — no encontrado

---

### `GET /teams/`

Lista todos los equipos registrados.

- `200` — array de `Team`

---

### `GET /health`

- `200 {"status": "ok"}`

---

## Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `SECUBOT_URL` | Sí | URL base de `Secubot-`, ej. `http://localhost:9000` |
| `DISCORD_URL` | Sí | URL del endpoint `/webhook/notify` del servicio Discord |
| `PARSER_URL` | Sí | URL base de `parser-dependabot` para rutas `/verify/{alert_id}` |
| `MONGO_URI` | Sí | URI de conexión a MongoDB Atlas |
| `MONGO_DB_NAME` | No (default: `secubot`) | Nombre de la base de datos |

---

## Instalación y ejecución local

```bash
git clone https://github.com/SecuBotUdea/jug-eared.git
cd jug-eared

python -m venv .venv
source .venv/bin/activate
pip install .

cp .env.example .env   # completar con valores reales
uvicorn app.main:app --reload
```

Con `uv`:
```bash
uv venv && source .venv/bin/activate
uv pip install .
uvicorn app.main:app --reload
```

---

## Tests

```bash
pip install .[dev]
pytest -q
```

---

## Flujo completo de una alerta

```
1. parser-dependabot  →  POST /alerts/
2. jug-eared extrae {owner}-{repo} del alert_id
3. MongoDB: busca equipo por repository
4. background: POST Secubot /events/rescan_result  (alert + team_id + user_id si hay rescan)
5. background: POST Discord /webhook/notify         (notificación al canal del equipo)
```

### Flujo de rescan

```
1. Usuario en Discord hace clic en "Rescan"
2. Discord bot  →  POST /rescan/
3. jug-eared guarda (alert_id, user_id) en MongoDB
4. background: POST parser /verify/{alert_id}  (con github_token del equipo)
5. parser verifica en GitHub y re-entrega el webhook normalizado
6. jug-eared recibe el alert actualizado en POST /alerts/
7. consume_rescan_user()  →  atribuye puntos al usuario que solicitó el rescan
```

---

## Estructura del proyecto

```
app/
├── api/
│   ├── dependencies.py
│   └── routes/
│       ├── alerts.py        # POST /alerts/
│       ├── registry.py      # CRUD /teams/
│       ├── rescan.py        # POST /rescan/
│       └── gamification.py  # POST /gamification/
├── core/
│   ├── registry.py
│   └── router.py            # route_alert, route_rescan
├── db/
│   └── repository.py        # MongoTeamRepository
├── models/
│   ├── alert.py
│   ├── gamification.py
│   ├── notification.py
│   ├── rescan.py
│   ├── status_change.py
│   └── team.py
├── config.py                # Settings (pydantic-settings)
└── main.py                  # lifespan, routers
```

---

## Stack

- **Python** 3.11+
- **FastAPI** + **uvicorn**
- **Motor** (async MongoDB)
- **MongoDB Atlas**
- **httpx** (llamadas a Secubot-, Discord y parser)
- **pydantic-settings**

---

## Notas

- Las llamadas a `Secubot-` y `Discord` en `route_alert` son secuenciales. Si Discord falla, Secubot ya fue notificado; el error queda en logs pero no revierte la operación.
- El caché de rescan (`rescans` collection) es consumido una sola vez (`find_one_and_delete`). Si el parser re-entrega el webhook antes de que `save_rescan_user` complete, el alert se routea sin `user_id`.
- `PARSER_URL` se usa como prefijo: la llamada final es `POST {PARSER_URL}/{alert_id}` con el `github_token` del equipo en el header `X-Github-Token`.