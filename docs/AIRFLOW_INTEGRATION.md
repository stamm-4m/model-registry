# Integración con Airflow (workflow-orchestrator) — guía para Carlos

Este documento explica qué se hizo para que **crear un experimento dispare
automáticamente el pipeline de predicciones en Airflow**, y qué hay que
configurar en tu máquina (donde corre `model-registry`) para que se conecte
con la máquina de Santiago (donde corre `workflow-orchestrator`/Airflow).

Todo lo que se describe aquí se probó y funciona, pero se probó con las dos
partes corriendo **en la misma máquina** (para poder iterar rápido). Para que
funcione entre tus dos VMs separadas, la diferencia es únicamente
**configuración de red/URLs** — el código no cambia.

---

## 1. Qué problema resuelve esto

Antes: crear un experimento en el Dash no hacía nada más — alguien tenía que
disparar el DAG de Airflow a mano.

Ahora: al guardar un experimento nuevo en el Dash, automáticamente:
1. Se crea su primer `run` (`POST /api/v1/runs/`).
2. Se dispara el DAG `deployment_soft_sensors` en Airflow, pasándole ese
   `run_id`.
3. Airflow espera datos de sensores para ese `run_id`, llama al modelo oficial
   del proyecto, y guarda la predicción — todo por HTTP, nada de conexión
   directa a bases de datos entre las dos máquinas.

```
Dash (crear experimento)
   │
   ├─► POST /api/v1/experiments/         (tu API)
   ├─► POST /api/v1/runs/                (tu API)
   │
   └─► POST http://<airflow>/auth/token                              (login en Airflow)
       POST http://<airflow>/api/v2/dags/deployment_soft_sensors/dagRuns  (dispara el DAG)
                │
                ▼
        Airflow espera datos → llama al modelo → guarda la predicción
                │
                └─► POST http://<tu-api>/api/v1/predictions/
```

---

## 2. Código nuevo/modificado en `model-registry`

Todo esto está en la rama `ml-santiago` (avísanos cuándo la subimos / si ya
está commiteada para que hagas `git pull`):

| Archivo | Qué cambia |
|---|---|
| `model_registry/backend/services/airflow_client.py` | **Nuevo.** Hace el login en Airflow (`/auth/token`) y dispara el DAG (`POST /api/v2/dags/deployment_soft_sensors/dagRuns`). |
| `model_registry/backend/services/api_clients/runs_api_client.py` | **Nuevo.** Cliente CRUD para `/api/v1/runs/`, igual patrón que los demás clientes existentes. |
| `model_registry/backend/services/api_clients/__init__.py` | Exporta `RunsApiClient`. |
| `model_registry/backend/config/settings.py` | Agrega 3 settings nuevas (opcionales): `AIRFLOW_API_BASE`, `AIRFLOW_TRIGGER_USERNAME`, `AIRFLOW_TRIGGER_PASSWORD`. Si no las configuras, el sistema simplemente no dispara Airflow (lo loguea y sigue, no rompe la creación del experimento). |
| `model_registry/backend/callbacks/callbacks_modal_experiment.py` | En `save_experiment`, cuando se crea un experimento **nuevo** (no al editar), llama a `_start_prediction_loop(...)` que crea el `run` y dispara Airflow. |

No se tocó nada del lado de la API FastAPI (`model_registry/api/...`) — todos
los endpoints que usa Airflow para leer/escribir datos **ya existían**
(`/api/v1/runs/{id}/sensor_readings`, `/api/v1/runs/{id}/actuator_states`,
`/api/v1/predictions/`, `/{project_id}/predict/{model_id}`, etc.). Lo único
nuevo es quién los llama y cuándo.

---

## 3. Qué tienes que configurar en tu `.env`

Archivo: `model_registry/backend/.env` (no está en git, hay que ponerlo a mano).

```bash
# Dirección pública de Airflow en la máquina de Santiago (puerto del
# api-server de Airflow — en su setup actual es el 8081)
AIRFLOW_API_BASE=http://178.104.166.114:8081

# Usuario de Airflow (rol "Op") que Santiago ya creó para esto
AIRFLOW_TRIGGER_USERNAME=model-registry-service
AIRFLOW_TRIGGER_PASSWORD=7yZpNX4I8QOLeND6FeJdX97M
```

**Confírmale a Santiago** cuál es la IP/puerto real donde va a quedar Airflow
corriendo de forma estable (la de arriba es la que usamos en las pruebas) y
si ese puerto está abierto hacia tu VM (firewall/security group).

---

## 4. Qué tienes que crear en tu base de datos

Airflow necesita un usuario de servicio **en tu base** para poder leer
sensores/actuadores y escribir predicciones por API. Pasos:

### 4.1. Crear el usuario (vía API, no SQL directo)
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"airflow-service@stamm.local.com","password":"ELIGE_UNA_CONTRASEÑA","full_name":"Airflow Service Account"}'
```

### 4.2. Crear el rol `service_airflow` con permisos mínimos
```sql
INSERT INTO roles (id, name) VALUES (gen_random_uuid(), 'service_airflow');
```

### 4.3. Darle exactamente estos 9 permisos (ni más ni menos — es la lista mínima que Airflow necesita)
```sql
INSERT INTO role_permission (role_id, permission_id, resource_id)
SELECT (SELECT id FROM roles WHERE name = 'service_airflow'), p.id, r.id
FROM permissions p, resources r
WHERE (p.name, r.name) IN (
  ('models:read', 'Models'),
  ('models:deploy', 'Models'),
  ('experiments:read', 'Experiments'),
  ('runs:read', 'Runs'),
  ('sensors:read', 'Sensors'),
  ('actuators:read', 'Actuators'),
  ('soft_sensors:read', 'Soft_sensors'),
  ('project_soft_sensors:read', 'Project_soft_sensors'),
  ('predictions:write', 'Predictions')
);
```

### 4.4. Asignarle el rol al usuario
```sql
INSERT INTO user_role (user_id, role_id)
SELECT (SELECT id FROM users WHERE email = 'airflow-service@stamm.local.com'),
       (SELECT id FROM roles WHERE name = 'service_airflow');
```

### 4.5. Mapear al menos un modelo real a `soft_sensors` (si no lo has hecho ya)
Las predicciones se guardan matcheando el modelo contra `soft_sensors.path_metadata`.
Si tu proyecto todavía no tiene ninguno registrado así:
```sql
INSERT INTO soft_sensors (path_metadata, path_model)
VALUES ('projects/<CARPETA_DEL_PROYECTO>/models/<MODEL_ID>/metadata.yaml',
        'projects/<CARPETA_DEL_PROYECTO>/models/<MODEL_ID>/model.pkl');

INSERT INTO project_soft_sensors (project_id, soft_sensor_id)
VALUES ('<UUID_DEL_PROYECTO>', (SELECT id FROM soft_sensors WHERE path_metadata LIKE '%<MODEL_ID>%'));
```
`<MODEL_ID>` debe ser el mismo string que devuelve `GET /{project_id}/list_models/`.

> Nota: hoy Airflow llama a **un solo modelo "oficial"** por proyecto (no a
> todos los registrados) — está configurado del lado de Santiago
> (`MODEL_ID_PENICILLIN` / `MODEL_ID_ECOLI` en su `.env`). Cuál modelo usar
> oficialmente es algo que falta decidir en equipo.

---

## 5. Del lado de Santiago (para que tú lo sepas, no lo tienes que hacer tú)

En `workflow-orchestrator/.env`, Santiago tiene:
```bash
MODEL_REGISTRY_API_BASE=http://<TU_IP_PUBLICA>:8080
MODEL_REGISTRY_SERVICE_EMAIL=airflow-service@stamm.local.com
MODEL_REGISTRY_SERVICE_PASSWORD=<LA_CONTRASEÑA_QUE_ELIJAS_EN_4.1>
```
O sea: **avísale la contraseña que elegiste** en el paso 4.1, porque él la
necesita configurar de su lado para que Airflow pueda loguearse en tu API.

---

## 6. Cómo probar que quedó bien conectado

1. Crea un experimento de prueba en el Dash.
2. Revisa los logs del backend (`docker logs model-registry-backend -f`) —
   deberías ver `POST /api/v1/runs/` seguido de
   `[airflow] triggered deployment_soft_sensors for run_id=...`.
3. Si ves `[airflow] failed to obtain token` o `trigger failed`, es un
   problema de red/credenciales (revisa `AIRFLOW_API_BASE` y que el puerto
   esté abierto) — la creación del experimento igual funciona, solo no
   dispara Airflow.
4. Mientras tanto, alguien tiene que estar mandando datos de sensor para ese
   `run_id` (hardware real, o el simulador de prueba que armamos —
   pregúntale a Santiago por `scripts/simulate_sensors.py` /
   `scripts/send_data_curl.sh` en `workflow-orchestrator`).
5. Confirma la predicción: `GET /api/v1/runs/{run_id}/predictions` con tu
   token.

---

## Referencia
El contrato completo de la API de Airflow (qué mandar exactamente al
disparar el DAG) está documentado en
`workflow-orchestrator/docs/trigger-from-model-registry.md`.
