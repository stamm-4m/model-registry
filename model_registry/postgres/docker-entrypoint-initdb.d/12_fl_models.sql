-- Federated global models: one aggregated global model per federation, linked
-- to its coordinator project (so it shows in "ML Soft Sensors") and pointed to
-- by federations.current_global_model_id. FK-safe + idempotent.
BEGIN;

INSERT INTO public.models
    (id, slug, name, algorithm, status, version, inputs, outputs,
     federation_id, federation_round, federation_role, validation_status,
     description, tags, is_active, created_at, updated_at)
SELECT gen_random_uuid(), v.slug, v.name, v.algo, 'trained', '1.0.0',
       v.inputs::jsonb, v.outputs::jsonb,
       f.id, f.rounds_completed, 'aggregated_global', 'approved',
       v.descr, ARRAY['federated'], true, now(), now()
FROM (VALUES
    ('biomass_fed_v1', 'fed_biomass_global',
     'Biomass soft sensor (federated global)', 'neural_network',
     '{"scaler": null, "features": [{"name":"temperature"},{"name":"pH"},{"name":"dissolved_oxygen"},{"name":"agitator"}]}',
     '{"scaler": null, "information": [{"name":"biomass"}]}',
     'Aggregated global model produced by federation biomass_fed_v1.'),
    ('penicillin_yield_fed', 'fed_penicillin_global',
     'Penicillin yield (federated global)', 'rnn',
     '{"scaler": null, "features": [{"name":"temperature"},{"name":"pH"},{"name":"dissolved_oxygen"},{"name":"sugar_feed_rate"}]}',
     '{"scaler": null, "information": [{"name":"penicillin_concentration"}]}',
     'Aggregated global model produced by federation penicillin_yield_fed.'),
    ('ecoli_softsensor_fed', 'fed_ecoli_global',
     'E. coli soft sensor (federated global)', 'linear_regression',
     '{"scaler": null, "features": [{"name":"OD"},{"name":"feed_rate"},{"name":"DO"}]}',
     '{"scaler": null, "information": [{"name":"product_titer"}]}',
     'Aggregated global model produced by federation ecoli_softsensor_fed.')
) AS v(fed_slug, slug, name, algo, inputs, outputs, descr)
JOIN public.federations f ON f.slug = v.fed_slug
ON CONFLICT (slug) DO NOTHING;

-- link each global model to its coordinator project -> appears in ML Soft Sensors
INSERT INTO public.project_models (id, project_id, model_id, role)
SELECT gen_random_uuid(), p.id, m.id, 'primary'
FROM (VALUES
    ('fed_biomass_global',    'P0001'),
    ('fed_penicillin_global', 'P0001'),
    ('fed_ecoli_global',      'P0002')
) AS v(model_slug, proj_id)
JOIN public.models   m ON m.slug = v.model_slug
JOIN public.projects p ON p.project_id = v.proj_id
ON CONFLICT DO NOTHING;

-- point each federation at its aggregated global model
UPDATE public.federations f
SET current_global_model_id = m.id, updated_at = now()
FROM public.models m
WHERE m.federation_id = f.id
  AND m.federation_role = 'aggregated_global'
  AND f.current_global_model_id IS NULL;

COMMIT;
