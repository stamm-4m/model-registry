--
-- 09_detector_packs.sql
--
-- Drift-detector PACKS — the versioned, uploadable source of the detector
-- catalog. One row per (name, version) of the `stamm-drift-detectors` pip
-- package. The registry UI (Drift Detectors page) uploads a slim
-- `drift_detectors/` archive; the register endpoint validates it, ingests
-- each detector's metadata.yaml into the `drift_detectors` catalog
-- (06_drift_detectors_seed shape) and records provenance here. Exactly one
-- pack per name is `is_active` (the pinned/deployed version the DAG runs).
--
-- Additive + idempotent (IF NOT EXISTS / ON CONFLICT). New resource +
-- permissions are unique, so the role_permission UNIQUE(role_id, permission_id)
-- trap does not apply. Grants mirror 07: super_admin + any role that already
-- reads drift_detectors.
--
-- Apply to a running DB:
--   docker compose exec -T postgres psql -U stamm -d stamm -f /docker-entrypoint-initdb.d/09_detector_packs.sql
-- Also runs automatically on a fresh DB boot. Rebuild/restart the `api`
-- container after so the new ORM model + /api/v1/ routes are picked up.
--
BEGIN;

-- ---------------------------------------------------------------- table
CREATE TABLE IF NOT EXISTS public.detector_packs (
    id             uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name           text NOT NULL,                       -- pip package name, e.g. stamm-drift-detectors
    version        text NOT NULL,                       -- semver from pyproject / __version__
    source         text NOT NULL DEFAULT 'upload',      -- upload | pip | git
    checksum       text,                                -- sha256 of the uploaded archive
    storage_path   text,                                -- on-disk path of the stored slim archive
    detector_count integer NOT NULL DEFAULT 0,
    detectors      jsonb   NOT NULL DEFAULT '[]'::jsonb,-- list of ingested detector_ids
    is_active      boolean NOT NULL DEFAULT false,      -- the pinned/deployed pack (one per name)
    notes          text,
    created_by     uuid REFERENCES public.users(id),
    created_at     timestamp DEFAULT now()
);

-- One pack row per (name, version); re-registering the same version updates it.
DO $$ BEGIN
    ALTER TABLE public.detector_packs
        ADD CONSTRAINT detector_packs_name_version_uq UNIQUE (name, version);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- At most one active pack per name (partial unique index).
CREATE UNIQUE INDEX IF NOT EXISTS detector_packs_one_active_per_name
    ON public.detector_packs (name) WHERE is_active;

-- ------------------------------------------------------------- resource
-- require_permission_resource() looks up Resource by tablename.capitalize().
INSERT INTO public.resources (id, name)
SELECT uuid_generate_v4(), 'Detector_packs'
WHERE NOT EXISTS (SELECT 1 FROM public.resources WHERE name = 'Detector_packs');

-- ----------------------------------------------------------- permissions
INSERT INTO public.permissions (id, name, description) VALUES
  (uuid_generate_v4(), 'detector_packs:read',  'Read drift-detector packs'),
  (uuid_generate_v4(), 'detector_packs:write', 'Register/upload drift-detector packs'),
  (uuid_generate_v4(), 'detector_packs:edit',  'Activate/pin or delete drift-detector packs')
ON CONFLICT (name) DO NOTHING;

-- ----------------------------------------------------------------- grants
-- super_admin + every role that can READ drift_detectors today.
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
JOIN public.permissions p ON p.name LIKE 'detector_packs:%'
JOIN public.resources  r ON r.name = 'Detector_packs'
ON CONFLICT DO NOTHING;

COMMIT;
-- end of 09_detector_packs.sql --
