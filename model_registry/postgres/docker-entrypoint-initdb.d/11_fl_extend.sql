-- FL Phase-0 extensions: strategy_params + model_spec on federations,
-- and a federation_rounds summary table (per-round global metric + per-
-- participant contribution weights) that drives the convergence &
-- contribution charts. Idempotent.
BEGIN;

ALTER TABLE public.federations
    ADD COLUMN IF NOT EXISTS strategy_params jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE public.federations
    ADD COLUMN IF NOT EXISTS model_spec jsonb NOT NULL DEFAULT '{}'::jsonb;

CREATE TABLE IF NOT EXISTS public.federation_rounds (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    federation_id         uuid NOT NULL REFERENCES public.federations(id) ON DELETE CASCADE,
    round_number          integer NOT NULL,
    status                text NOT NULL DEFAULT 'completed',
    global_metric_name    text,
    global_metric_value   numeric,
    participants_expected integer,
    participants_received integer,
    contributions         jsonb NOT NULL DEFAULT '{}'::jsonb,  -- {project_id: weight}
    global_model_id       uuid REFERENCES public.models(id),
    started_at            timestamptz DEFAULT now(),
    aggregated_at         timestamptz DEFAULT now(),
    created_at            timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT federation_rounds_uq UNIQUE (federation_id, round_number)
);
CREATE INDEX IF NOT EXISTS federation_rounds_fed_idx
    ON public.federation_rounds (federation_id, round_number);

-- strategy params + shared model spec per federation
UPDATE public.federations SET
    strategy_params = '{"mu": 0.1}'::jsonb,
    model_spec = '{"framework":"pytorch","version":"2.3","architecture":"mlp",
                   "inputs":["temperature","pH","dissolved_oxygen","agitator"],
                   "outputs":["biomass"],"init":"random_seed_42"}'::jsonb
WHERE slug = 'biomass_fed_v1';
UPDATE public.federations SET
    strategy_params = '{}'::jsonb,
    model_spec = '{"framework":"pytorch","version":"2.3","architecture":"lstm",
                   "inputs":["temperature","pH","dissolved_oxygen","sugar_feed_rate"],
                   "outputs":["penicillin_concentration"],"init":"random_seed_7"}'::jsonb
WHERE slug = 'penicillin_yield_fed';
UPDATE public.federations SET
    strategy_params = '{"epsilon": 1.0}'::jsonb,
    model_spec = '{"framework":"sklearn","version":"1.5.2","architecture":"linear",
                   "inputs":["OD","feed_rate","DO"],"outputs":["product_titer"],
                   "init":"zeros"}'::jsonb
WHERE slug = 'ecoli_softsensor_fed';

-- per-round summaries (rising global R² + fixed per-participant weights)
INSERT INTO public.federation_rounds
    (federation_id, round_number, status, global_metric_name, global_metric_value,
     participants_expected, participants_received, contributions, aggregated_at)
SELECT f.id, g.r, 'completed', 'val_r2',
       round((0.45 + 0.34 * (1 - exp(-0.35 * g.r)))::numeric, 3),
       cfg.expected, cfg.expected, cfg.contrib::jsonb, now()
FROM public.federations f
JOIN (VALUES
    ('biomass_fed_v1',       3, '{"P0001":0.42,"P0002":0.34,"P0003":0.24}'),
    ('penicillin_yield_fed', 2, '{"P0001":0.55,"P0002":0.45}'),
    ('ecoli_softsensor_fed', 2, '{"P0002":0.60,"P0003":0.40}')
) AS cfg(slug, expected, contrib) ON cfg.slug = f.slug
JOIN LATERAL generate_series(1, GREATEST(f.rounds_completed, 1)) AS g(r) ON true
ON CONFLICT (federation_id, round_number) DO NOTHING;

-- Resource + permissions + grant so the auto-CRUD endpoint for the new
-- federation_rounds table passes require_permission_resource (else 403).
-- role_permission has UNIQUE(role_id, permission_id) — bind each perm to the
-- ONE resource in a 1-to-1 pair (see role_permission constraint trap).
INSERT INTO public.resources (id, name)
SELECT gen_random_uuid(), 'Federation_rounds'
WHERE NOT EXISTS (SELECT 1 FROM public.resources WHERE name = 'Federation_rounds');

INSERT INTO public.permissions (id, name, description)
SELECT gen_random_uuid(), v.name, v.description
FROM (VALUES
    ('federation_rounds:read',  'Read federation rounds'),
    ('federation_rounds:write', 'Create/update federation rounds'),
    ('federation_rounds:edit',  'Edit federation rounds')
) AS v(name, description)
WHERE NOT EXISTS (SELECT 1 FROM public.permissions WHERE name = v.name);

INSERT INTO public.role_permission (id, role_id, permission_id, resource_id)
SELECT gen_random_uuid(),
       '11111111-1111-1111-1111-111111111111'::uuid,   -- super_admin role
       p.id, r.id
FROM public.permissions p, public.resources r
WHERE p.name IN ('federation_rounds:read','federation_rounds:write','federation_rounds:edit')
  AND r.name = 'Federation_rounds'
ON CONFLICT DO NOTHING;

COMMIT;
