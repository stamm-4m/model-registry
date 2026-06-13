--
-- 06_drift_detectors_seed.sql
--
-- Seeds the drift_detectors CATALOG from the stamm-drift-detectors pack
-- (metadata.yaml per detector). Idempotent: re-running refreshes the
-- display metadata (name/kind/description/params) but PRESERVES the
-- operator's `enabled` toggle. detector_id is UNIQUE.
--
-- Apply to a running DB:
--   docker compose exec -T postgres psql -U stamm -d stamm -f /docker-entrypoint-initdb.d/06_drift_detectors_seed.sql
-- (or pipe via < on the host). Also runs automatically on a fresh DB boot.
--
BEGIN;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'model_disagreement', 'MDM — Model Disagreement Metric', 'model_based', 'Pair-wise output-level disagreement detector for ensembles of co-deployed predictive models. Designed for the soft-sensor regime in which fresh ground-truth labels arrive offline hours-to-days late, so residual-based monitoring is unavailable. MDM is a pluggable orchestrator: the set of…', '{"metrics": "Sequence of DisagreementMetric instances; default is [MSEDisagreement(), PearsonDisagreement(), SpearmanDisagreement()].", "threshold": "Disagreement above which drift is flagged. Compared against the error-family aggregate (score field)."}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'kdq_tree', 'KDQ-tree Drift Detection', 'multivariate', 'KDQ-tree is a neighborhood-based multivariate drift detection method that compares the local distributions of test data and reference data using k-nearest neighbor comparisons. For each reference point, it identifies a neighborhood in both datasets and applies univariate KS tests across all…', '{"k_neighbors": "Number of nearest neighbors used for defining local neighborhoods.", "ks_method": "Method used in the KS test (e.g., ''asymp'', ''exact'', or ''auto'').", "alpha": "Significance threshold for the average p-value in a neighborhood. A lower alpha increases sensitivity to subtle changes.\n"}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'mmd', 'MMD — Maximum Mean Discrepancy', 'multivariate', 'Maximum Mean Discrepancy (MMD) is a nonparametric kernel-based method used to detect distributional drift between two multivariate datasets. It compares the mean embeddings of the distributions in a reproducing kernel Hilbert space (RKHS) using a kernel function, typically the RBF kernel. MMD is…', '{"gamma": "Bandwidth parameter for the RBF kernel.", "threshold": "Drift threshold for the MMD score. A higher score suggests greater  discrepancy between distributions.\n"}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'pca_cd', 'PCA-CD — PCA-based Change Detection', 'multivariate', 'PCA-CD (PCA-based Change Detection) detects drift in multivariate data by projecting both reference and test samples into a lower-dimensional PCA space, and then comparing their distributions. Drift is flagged when either the mean of projected components (CSD) or their variances (KL divergence)…', '{"n_components": "Number of principal components used for PCA projection.", "csd_threshold": "Threshold for mean shift detection using cumulative squared differences (CSD).", "kl_threshold": "Threshold for variance shift detection using symmetric KL divergence."}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'adwin', 'ADWIN — ADaptive WINdowing', 'univariate', 'ADaptive WINdowing (ADWIN) is a streaming drift detection algorithm for univariate data. It maintains a variable-length sliding window and uses Hoeffding bounds to detect statistically significant changes in the mean of the incoming data stream. Drift is detected when the average of recent data…', '{"delta": "Confidence parameter used in the Hoeffding bound to determine  significance of change. Lower values increase sensitivity to smaller shifts.\n"}'::jsonb, true, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'eddm', 'EDDM — Early Drift Detection Method', 'univariate', 'EDDM monitors the distance between consecutive errors in a binary error stream. Early drift is signalled when the running statistic mu + 2*sigma drops sufficiently below its historical maximum, indicating that the model is producing errors more closely together than before. EDDM is commonly used…', '{"warning_level": "Ratio threshold under which a warning is raised.", "drift_level": "Ratio threshold under which drift is signalled.", "min_n_errors": "Minimum number of accumulated errors required before drift can fire."}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'hddm_a', 'HDDM-A — Hoeffding Drift Detection Method (A-test)', 'univariate', 'HDDM-A monitors a univariate stream by maintaining a long-term mean estimator and a short-term (cut-point) mean estimator, and signals drift whenever their difference exceeds the Hoeffding inequality bound at the chosen confidence level. The detector also raises a "warning" status one step…', '{"drift_confidence": "Confidence level for drift detection (smaller = stricter).", "warning_confidence": "Confidence level for raising a warning before drift.", "two_sided": "If true, detect both increases and decreases of the mean."}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'ks', 'KS — Kolmogorov–Smirnov Test', 'univariate', 'The Kolmogorov–Smirnov (KS) test is a non-parametric method for comparing the empirical cumulative distribution functions (ECDFs) of two univariate datasets. It measures the largest absolute difference between the ECDFs. A statistically significant difference (based on a p-value and significance…', '{"alpha": "Significance level for rejecting the null hypothesis of equal distributions. Drift is flagged when the p-value falls below this threshold.\n"}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'page_hinkley', 'PH — Page-Hinkley', 'univariate', 'The Page-Hinkley test is a sequential change-point detector that tracks the cumulative deviation of incoming observations from a running mean. A drift is signalled when this cumulative deviation exceeds a threshold (lambda), after a tolerance (delta) has been subtracted from each step. Useful…', '{"delta": "Allowed magnitude of changes before flagging drift.", "lambda_": "Detection threshold; lower values increase sensitivity.", "alpha": "Forgetting factor for the running mean (0 < alpha <= 1)."}'::jsonb, false, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

INSERT INTO public.drift_detectors (id, detector_id, name, kind, description, params, enabled, created_at)
VALUES (uuid_generate_v4(), 'psi', 'PSI — Population Stability Index', 'univariate', 'The Population Stability Index (PSI) measures shifts in the distribution of a feature between two datasets, typically to monitor changes over time (e.g., training vs. test sets). It quantifies the divergence between the reference and test distributions using histogram binning. A higher PSI score…', '{"bins": "Number of bins used to discretize the data for histogram comparison.", "epsilon": "Small constant to avoid division by zero or log(0) during PSI calculation.", "threshold": "Drift threshold above which the PSI score is considered significant."}'::jsonb, true, now())
ON CONFLICT (detector_id) DO UPDATE SET
    name = EXCLUDED.name, kind = EXCLUDED.kind,
    description = EXCLUDED.description, params = EXCLUDED.params;

COMMIT;
-- 10 detectors seeded.
