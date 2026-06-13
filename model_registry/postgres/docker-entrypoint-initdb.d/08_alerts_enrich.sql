--
-- 08_alerts_enrich.sql
--
-- Enriches the `alerts` (firings) table so the FermOps Health alert feed can
-- show real structured fields. The base table (01_schema) only has
-- id / condition / message / experiment_id; this adds the display dimensions
-- the feed expects. Idempotent (ADD COLUMN IF NOT EXISTS).
--
-- The streamer / DAG that writes firings should populate these going forward;
-- existing rows take the column defaults (NULL / 'active'). FermOps falls back
-- to per-field defaults when a column is NULL, so this is safe immediately.
--
--   created_at -> feed "ts"        (when the alert fired)
--   condition  -> feed "severity"  ('warning'|'critical' -> med|high) [existing]
--   alert_type -> feed "type"      ('Drift'|'Divergence'|'Coverage'|...)
--   variable   -> feed "variable"  (signal the alert concerns)
--   phase      -> feed "phase"
--   status     -> feed "status"    ('active'|'resolved')
--
BEGIN;
ALTER TABLE public.alerts
    ADD COLUMN IF NOT EXISTS created_at timestamp DEFAULT now(),
    ADD COLUMN IF NOT EXISTS alert_type text,
    ADD COLUMN IF NOT EXISTS variable   text,
    ADD COLUMN IF NOT EXISTS phase      text,
    ADD COLUMN IF NOT EXISTS status     text NOT NULL DEFAULT 'active';
COMMIT;
-- end of 08_alerts_enrich.sql --
