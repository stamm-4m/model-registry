--
-- 07_drift_monitoring.sql
--
-- Phase 4 (drift monitoring) — two NEW tables + their resources/permissions:
--   experiment_drift_detectors  -- per-experiment detector SELECTION (FermOps writes)
--   drift_results               -- detector RESULTS (Airflow DAG writes, last task)
--
-- Additive + idempotent (IF NOT EXISTS / ON CONFLICT). Touches NOTHING in the
-- auth/user-privileges system beyond GRANTING the two new resources to the
-- roles that already use drift detectors (super_admin + any role that can read
-- drift_detectors today). New permissions are unique, so the role_permission
-- UNIQUE(role_id, permission_id) trap doesn't apply.
--
-- Apply to a running DB:
--   docker compose exec -T postgres psql -U stamm -d stamm -f /docker-entrypoint-initdb.d/07_drift_monitoring.sql
-- Also runs automatically on a fresh DB boot. Rebuild the `api` container after
-- so the new ORM models + /api/v1/ CRUD routes are picked up.
--
BEGIN;

-- ---------------------------------------------------------------- tables
CREATE TABLE IF NOT EXISTS public.experiment_drift_detectors (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id   uuid NOT NULL REFERENCES public.experiments(id) ON DELETE CASCADE,
    detector_id     text NOT NULL,                         -- -> drift_detectors.detector_id
    -- univariate monitor -> 1 variable e.g. {DO}; multivariate -> a set
    -- e.g. {DO,pH,Temperature,RPM}. Stored sorted+deduped for stable uniqueness.
    variables       text[] NOT NULL DEFAULT '{}',
    phase           text,
    params_override jsonb NOT NULL DEFAULT '{}'::jsonb,
    enabled         boolean NOT NULL DEFAULT true,
    created_by      uuid REFERENCES public.users(id),
    created_at      timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS experiment_drift_detectors_exp_idx
    ON public.experiment_drift_detectors (experiment_id);

-- Idempotent migration for any DB created with the earlier `variable text`
-- shape (Option A). Safe on fresh boots (the column already matches).
ALTER TABLE public.experiment_drift_detectors
    DROP CONSTRAINT IF EXISTS experiment_drift_detectors_uq;
ALTER TABLE public.experiment_drift_detectors
    ADD COLUMN IF NOT EXISTS variables text[] NOT NULL DEFAULT '{}';
ALTER TABLE public.experiment_drift_detectors
    DROP COLUMN IF EXISTS variable;
DO $$ BEGIN
    ALTER TABLE public.experiment_drift_detectors
        ADD CONSTRAINT experiment_drift_detectors_uq
        UNIQUE (experiment_id, detector_id, variables);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS public.drift_results (
    id           uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id       uuid NOT NULL REFERENCES public.runs(id) ON DELETE CASCADE,
    detector_id  text NOT NULL,
    variable     text NOT NULL,
    phase        text,
    result_type  text NOT NULL DEFAULT 'score',            -- score|pointwise|streaming
    score        double precision,
    drift        boolean NOT NULL DEFAULT false,
    details      jsonb NOT NULL DEFAULT '{}'::jsonb,
    pack_version text,
    computed_at  timestamp,
    created_at   timestamp DEFAULT now()
);
CREATE INDEX IF NOT EXISTS drift_results_run_idx
    ON public.drift_results (run_id, detector_id, variable);

-- ------------------------------------------------------------- resources
-- require_permission_resource() looks up Resource by tablename.capitalize().
INSERT INTO public.resources (id, name)
SELECT uuid_generate_v4(), 'Experiment_drift_detectors'
WHERE NOT EXISTS (SELECT 1 FROM public.resources WHERE name = 'Experiment_drift_detectors');
INSERT INTO public.resources (id, name)
SELECT uuid_generate_v4(), 'Drift_results'
WHERE NOT EXISTS (SELECT 1 FROM public.resources WHERE name = 'Drift_results');

-- ----------------------------------------------------------- permissions
INSERT INTO public.permissions (id, name, description) VALUES
  (uuid_generate_v4(), 'experiment_drift_detectors:read',  'Read drift-detector selection'),
  (uuid_generate_v4(), 'experiment_drift_detectors:write', 'Create/update drift-detector selection'),
  (uuid_generate_v4(), 'experiment_drift_detectors:edit',  'Edit drift-detector selection'),
  (uuid_generate_v4(), 'drift_results:read',  'Read drift results'),
  (uuid_generate_v4(), 'drift_results:write', 'Write drift results'),
  (uuid_generate_v4(), 'drift_results:edit',  'Edit drift results')
ON CONFLICT (name) DO NOTHING;

-- ----------------------------------------------------------------- grants
-- Roles to grant: super_admin, plus every role that can READ drift_detectors
-- today (so the engineer role inherits the same access). Each new permission
-- binds to its matching new resource.
WITH grant_roles AS (
    SELECT '11111111-1111-1111-1111-111111111111'::uuid AS role_id
    UNION
    SELECT DISTINCT rp.role_id
    FROM public.role_permission rp
    JOIN public.permissions pd ON pd.id = rp.permission_id AND pd.name = 'drift_detectors:read'
    JOIN public.resources  rd ON rd.id = rp.resource_id  AND rd.name = 'Drift_detectors'
)
INSERT INTO public.role_permission (id, role_id, permission_id, resource_id)
SELECT uuid_generate_v4(), gr.role_id, p.id, r.id
FROM grant_roles gr
JOIN public.permissions p ON p.name LIKE 'experiment_drift_detectors:%'
JOIN public.resources  r ON r.name = 'Experiment_drift_detectors'
ON CONFLICT DO NOTHING;

WITH grant_roles AS (
    SELECT '11111111-1111-1111-1111-111111111111'::uuid AS role_id
    UNION
    SELECT DISTINCT rp.role_id
    FROM public.role_permission rp
    JOIN public.permissions pd ON pd.id = rp.permission_id AND pd.name = 'drift_detectors:read'
    JOIN public.resources  rd ON rd.id = rp.resource_id  AND rd.name = 'Drift_detectors'
)
INSERT INTO public.role_permission (id, role_id, permission_id, resource_id)
SELECT uuid_generate_v4(), gr.role_id, p.id, r.id
FROM grant_roles gr
JOIN public.permissions p ON p.name LIKE 'drift_results:%'
JOIN public.resources  r ON r.name = 'Drift_results'
ON CONFLICT DO NOTHING;

COMMIT;
-- end of 07_drift_monitoring.sql --
