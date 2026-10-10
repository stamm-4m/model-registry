-- MQTT instrument readings: additive migration for existing databases.
BEGIN;

CREATE TABLE IF NOT EXISTS public.instrument_readings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    instrument_id uuid REFERENCES public.instruments(id) ON DELETE SET NULL,
    topic text NOT NULL,
    measurement text NOT NULL,
    "time" timestamptz NOT NULL,
    payload jsonb NOT NULL,
    received_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.instrument_readings
    ADD COLUMN IF NOT EXISTS instrument_id uuid
    REFERENCES public.instruments(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_instrument_readings_time
    ON public.instrument_readings ("time");

INSERT INTO public.resources (id, name)
SELECT gen_random_uuid(), 'Instrument_readings'
WHERE NOT EXISTS (
    SELECT 1 FROM public.resources WHERE name = 'Instrument_readings'
);

INSERT INTO public.permissions (id, name, description)
SELECT gen_random_uuid(), permissions.name, permissions.description
FROM (VALUES
    ('instrument_readings:read',  'Read external instrument readings'),
    ('instrument_readings:write', 'Ingest external instrument readings'),
    ('instrument_readings:edit',  'Edit or delete external instrument readings')
) AS permissions(name, description)
WHERE NOT EXISTS (
    SELECT 1 FROM public.permissions existing
    WHERE existing.name = permissions.name
);

INSERT INTO public.role_permission (id, role_id, permission_id, resource_id)
SELECT gen_random_uuid(), r.id, p.id, resource.id
FROM public.roles r
JOIN public.resources resource ON resource.name = 'Instrument_readings'
JOIN public.permissions p
  ON p.name IN (
      'instrument_readings:read',
      'instrument_readings:write',
      'instrument_readings:edit'
  )
WHERE r.name = 'super_admin'
ON CONFLICT DO NOTHING;

COMMIT;
