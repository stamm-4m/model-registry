# Integración con Airflow (workflow-orchestrator) — guía para Carlos

Este documento explica qué se hizo para que **crear un experimento dispare
automáticamente el pipeline de predicciones en Airflow**, y qué necesitas
correr en tu máquina para que funcione.

**Importante — arquitectura**: la idea es que todo esto sea **portable**:
cualquiera que clone los dos repos (`model-registry` y `workflow-orchestrator`)
y los levante con Docker debe poder correr el flujo completo en su propia
máquina, sin depender del servidor de nadie más. Eso significa que **tú
también necesitas levantar `workflow-orchestrator` (Airflow) localmente**,
además de `model-registry` — no es que tu `model-registry` se conecte al
Airflow de Santiago por internet. Los dos stacks corren en la misma máquina,
en la misma red Docker (`ml_net`), y se hablan por el nombre del contenedor,
no por IP pública. Por eso `AIRFLOW_API_BASE=http://localhost:8081` te dio
`Connection refused` — no tenías Airflow corriendo en tu máquina todavía.

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
   directa a bases de datos entre los dos servicios.

```
Dash (crear experimento)
   │
   ├─► POST /api/v1/experiments/         (tu API)
   ├─► POST /api/v1/runs/                (tu API)
   │
   └─► POST http://airflow-webserver:8080/auth/token                              (login en Airflow)
       POST http://airflow-webserver:8080/api/v2/dags/deployment_soft_sensors/dagRuns  (dispara el DAG)
                │
                ▼
        Airflow espera datos → llama al modelo → guarda la predicción
                │
                └─► POST http://model-registry-api:8080/api/v1/predictions/
```

---

## 2. Levantar `workflow-orchestrator` (Airflow) en tu máquina

Esto es lo que te falta y por eso te está dando el error de conexión.

```bash
git clone git@github.com:stamm-4m/workflow-orchestrator.git
cd workflow-orchestrator
git checkout ml-santiago   # o main, una vez que se mergee
```

Copia/crea el `.env` (revisa `docker-compose.yaml` para ver qué variables
espera — como mínimo necesitas `AIRFLOW_UID`, `AIRFLOW__API_AUTH__JWT_SECRET`,
`AIRFLOW_ADMIN_USER/PASSWORD/EMAIL`, y las `MODEL_REGISTRY_*` apuntando a
**tu propio** `model-registry` local, no al de Santiago):

```bash
MODEL_REGISTRY_API_BASE=http://model-registry-api:8080
MODEL_REGISTRY_SERVICE_EMAIL=airflow-service@stamm.local.com
MODEL_REGISTRY_SERVICE_PASSWORD=<la misma que uses en el paso 4.1 de abajo>
MODEL_REGISTRY_PROJECT_ID_PENICILLIN=P0001
FEATURES_PENICILLIN=temperature,pH,dissolved_oxygen_concentration,agitator,CO2_percent_in_off_gas,oxygen_in_percent_in_off_gas,vessel_volume,sugar_feed_rate
MODEL_ID_PENICILLIN=0001_python_penicillin_RF
```

Levanta el stack:
```bash
docker compose up -d --build
```

Esto crea, entre otros, el contenedor `airflow-webserver` en el puerto
**8081 del host** (el 8080 ya lo usa `model-registry-api`), y se conecta a
la red externa `ml_net` que ya creó tu stack de `model-registry` — por eso
es importante levantar primero `model-registry` y después `workflow-orchestrator`.

Despausa el DAG antes de probar:
```bash
docker exec <contenedor-airflow-worker> airflow dags unpause deployment_soft_sensors
```

### Crear el usuario que dispara el DAG (en TU Airflow, no en el de Santiago)
```bash
docker exec <contenedor-airflow-worker> airflow users create \
  --username model-registry-service \
  --password ELIGE_UNA_CONTRASEÑA \
  --firstname ModelRegistry --lastname Service \
  --role Op \
  --email model-registry-service@stamm.local.com
```
Esa contraseña es la que va en `AIRFLOW_TRIGGER_PASSWORD` (paso 3).

---

## 3. Qué configurar en `model_registry/backend/.env`

```bash
# Nombre del contenedor de Airflow en tu propia red Docker — NO localhost,
# NO la IP de Santiago. Funciona porque ambos stacks comparten la red ml_net.
AIRFLOW_API_BASE=http://airflow-webserver:8080

AIRFLOW_TRIGGER_USERNAME=model-registry-service
AIRFLOW_TRIGGER_PASSWORD=<la que elegiste al crear el usuario arriba>
```

---

## 4. Código nuevo/modificado en `model-registry`

Todo esto está en la rama `ml-santiago`:

| Archivo | Qué cambia |
|---|---|
| `model_registry/backend/services/airflow_client.py` | **Nuevo.** Hace el login en Airflow (`/auth/token`) y dispara el DAG (`POST /api/v2/dags/deployment_soft_sensors/dagRuns`). |
| `model_registry/backend/services/api_clients/runs_api_client.py` | **Nuevo.** Cliente CRUD para `/api/v1/runs/`, igual patrón que los demás clientes existentes. |
| `model_registry/backend/services/api_clients/__init__.py` | Exporta `RunsApiClient`. |
| `model_registry/backend/config/settings.py` | Agrega 3 settings nuevas (opcionales): `AIRFLOW_API_BASE`, `AIRFLOW_TRIGGER_USERNAME`, `AIRFLOW_TRIGGER_PASSWORD`. Si no las configuras, el sistema simplemente no dispara Airflow (lo loguea y sigue, no rompe la creación del experimento). |
| `model_registry/backend/callbacks/callbacks_modal_experiment.py` | En `save_experiment`, cuando se crea un experimento **nuevo** (no al editar), llama a `_start_prediction_loop(...)` que crea el `run`, resuelve **todos** los modelos elegidos en el dropdown (`experiment_models` → `models.slug`, vía `_resolve_model_slugs`) y el bioreactor elegido (`vessel_id`), y dispara Airflow pasándoselos como `model_ids`/`vessel_id`. |

No se tocó nada del lado de la API FastAPI (`model_registry/api/...`) — todos
los endpoints que usa Airflow para leer/escribir datos **ya existían**
(`/api/v1/runs/{id}/sensor_readings`, `/api/v1/runs/{id}/actuator_states`,
`/api/v1/predictions/`, `/{project_id}/predict/{model_id}`, etc.). Lo único
nuevo es quién los llama y cuándo.

---

## 5. Qué crear en tu base de datos

Airflow necesita un usuario de servicio **en tu base** para poder leer
sensores/actuadores y escribir predicciones por API. Pasos:

### 5.1. Crear el usuario (vía API, no SQL directo)
```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"airflow-service@stamm.local.com","password":"ELIGE_UNA_CONTRASEÑA","full_name":"Airflow Service Account"}'
```
Esta es la contraseña que va en `MODEL_REGISTRY_SERVICE_PASSWORD` del `.env`
de `workflow-orchestrator` (paso 2).

### 5.2. Crear el rol `service_airflow` con permisos mínimos
```sql
INSERT INTO roles (id, name) VALUES (gen_random_uuid(), 'service_airflow');
```

### 5.3. Darle exactamente estos 11 permisos (ni más ni menos — es la lista mínima que Airflow necesita)
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
  ('predictions:write', 'Predictions'),
  ('sensor_readings:write', 'Sensor_readings'),
  ('actuator_states:write', 'Actuator_states')
);
```
Las dos últimas (`sensor_readings:write`, `actuator_states:write`) no las usa el DAG en sí — son para
`scripts/auto_simulate_sensors.py` (ver más abajo), que usa esta misma cuenta para inyectar datos de
prueba mientras no hay sensores reales conectados.

### 5.4. Asignarle el rol al usuario
```sql
INSERT INTO user_role (user_id, role_id)
SELECT (SELECT id FROM users WHERE email = 'airflow-service@stamm.local.com'),
       (SELECT id FROM roles WHERE name = 'service_airflow');
```

### 5.5. Migrar `predictions` para apuntar a `models` en vez de `soft_sensors`
`soft_sensors`/`project_soft_sensors` ya no se usan — el registry (`api/core/registry.py`)
carga los modelos directamente desde la tabla `models` desde hace rato, y ahora
las predicciones también se guardan contra ahí. Corre esto una sola vez en tu base:
```sql
BEGIN;

ALTER TABLE predictions DROP CONSTRAINT IF EXISTS predictions_soft_sensor_id_fkey;
ALTER TABLE predictions RENAME COLUMN soft_sensor_id TO model_id;
ALTER TABLE predictions
    ADD CONSTRAINT predictions_model_id_fkey
    FOREIGN KEY (model_id) REFERENCES models(id)
    NOT VALID;  -- las predicciones viejas quedan con su UUID anterior, no se validan retroactivamente

COMMIT;
```
Con esto, cualquier modelo que ya esté en `models` (los que aparecen en el
dropdown de experimentos) puede recibir predicciones automáticas sin ningún
paso extra — no hace falta crear nada a mano por modelo como antes.

> Nota: Airflow corre una predicción por **cada** modelo que se haya
> seleccionado en el dropdown del experimento — model-registry manda la
> lista completa de `slug`s al disparar el DAG (`model_ids`, ver sección 4).
> Si el experimento no tiene ningún modelo asociado, Airflow cae de vuelta a
> `MODEL_ID_PENICILLIN`/`MODEL_ID_ECOLI` en su `.env` (un solo modelo). Si
> los modelos seleccionados tienen distinto intervalo de muestreo
> (`input_time_interval`), Airflow revisa datos nuevos usando el intervalo
> más corto entre todos, para que ninguno se quede sin dato fresco.

---

## 6. Cómo probar que quedó bien conectado

1. Confirma que ambos stacks están arriba: `docker ps` debe mostrar los
   contenedores de `model-registry` **y** de `workflow-orchestrator`
   (incluyendo `airflow-webserver`), todos en la red `ml_net`.
2. Crea un experimento de prueba en el Dash.
3. Revisa los logs del backend (`docker logs model-registry-backend -f`) —
   deberías ver `POST /api/v1/runs/` seguido de
   `[airflow] triggered deployment_soft_sensors for run_id=...`.
4. Si ves `[airflow] failed to obtain token` o `Connection refused`, revisa
   que `airflow-webserver` esté corriendo y en la misma red `ml_net` que
   `model-registry-backend` (`docker network inspect ml_net`).
5. Mientras tanto, alguien tiene que estar mandando datos de sensor para ese
   `run_id` (hardware real, o el simulador de prueba —
   `workflow-orchestrator/scripts/simulate_sensors.py` /
   `scripts/send_data_curl.sh`).
6. Confirma la predicción: `GET /api/v1/runs/{run_id}/predictions` con tu
   token.

---

## Referencia
El contrato completo de la API de Airflow (qué mandar exactamente al
disparar el DAG) está documentado en
`workflow-orchestrator/docs/trigger-from-model-registry.md`.
