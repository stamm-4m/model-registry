-- Federated Learning demo seed: federations + participants.
-- FK-safe (resolves org / project ids via subqueries). Idempotent.
BEGIN;

INSERT INTO public.federations
    (id, slug, name, description, coordinator_org_id, aggregation_strategy,
     privacy_mechanism, privacy_params, rounds_planned, rounds_completed,
     status, tags, created_at, updated_at)
VALUES
 (gen_random_uuid(), 'biomass_fed_v1', 'Biomass soft-sensor FL',
  'Cross-lab biomass soft sensor trained without sharing raw data.',
  (SELECT id FROM public.organizations ORDER BY created_at LIMIT 1),
  'fedavg', 'differential_privacy', '{"epsilon":3.0,"delta":1e-5}'::jsonb,
  10, 7, 'running', ARRAY['biomass','soft-sensor'], now(), now()),
 (gen_random_uuid(), 'penicillin_yield_fed', 'Penicillin yield FL',
  'Federated penicillin-yield predictor across pilot plants.',
  (SELECT id FROM public.organizations ORDER BY created_at LIMIT 1),
  'fedprox', 'none', '{}'::jsonb,
  12, 12, 'completed', ARRAY['penicillin','yield'], now(), now()),
 (gen_random_uuid(), 'ecoli_softsensor_fed', 'E. coli soft-sensor FL',
  'E. coli fed-batch soft sensor, differential-privacy protected.',
  (SELECT id FROM public.organizations ORDER BY created_at LIMIT 1),
  'fedavg', 'differential_privacy', '{"epsilon":1.0}'::jsonb,
  8, 2, 'running', ARRAY['ecoli'], now(), now())
ON CONFLICT (slug) DO NOTHING;

INSERT INTO public.federation_participants
    (id, federation_id, project_id, role, joined_at, local_dataset_size,
     last_contribution_round)
SELECT gen_random_uuid(), f.id, p.id, v.role, now(), v.samples, v.last
FROM (VALUES
    ('biomass_fed_v1',       'P0001', 'coordinator', 42300, 7),
    ('biomass_fed_v1',       'P0002', 'participant', 31850, 7),
    ('biomass_fed_v1',       'P0003', 'participant', 18470, 6),
    ('penicillin_yield_fed', 'P0001', 'coordinator', 55000, 12),
    ('penicillin_yield_fed', 'P0002', 'participant', 28000, 12),
    ('ecoli_softsensor_fed', 'P0002', 'coordinator', 20000, 2),
    ('ecoli_softsensor_fed', 'P0003', 'participant',  9220, 1)
) AS v(fed_slug, proj_id, role, samples, last)
JOIN public.federations f ON f.slug = v.fed_slug
JOIN public.projects   p ON p.project_id = v.proj_id
ON CONFLICT DO NOTHING;

COMMIT;
