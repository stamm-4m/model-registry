"""Explainability compute for scikit-learn models (server-side).

Pure compute: every entry point receives an ALREADY-LOADED model object (from
`app.state.registry`), its synthesized config and optional input scaler. This
module never loads artifacts, never resolves paths and never touches the DB or
filesystem — that stays the registry's job. The Dash backend reaches this only
through the protected `POST /{project_id}/explain/{model_id}` endpoint.

Capabilities (each independent, wrapped in try/except — one failure never sinks
the rest; the function never raises):
  * tree models   -> impurity importance, export_text rules, depth-2 subtree
  * linear models -> signed coefficients + intercept
  * any estimator -> partial dependence (pipeline-wrapped if a scaler exists)
  * tree/linear   -> SHAP (TreeExplainer / LinearExplainer)
  * with labels   -> permutation importance (uploaded data only)

PDP/SHAP run over a background sampled uniformly from each feature's declared
`expected_range` unless the caller supplies real rows.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_BG_N = 80
_PDP_GRID = 30
_MAX_INSTANCES = 8


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------
def _inputs_block(config: Dict[str, Any]) -> Dict[str, Any]:
    mlc = (config or {}).get("ml_model_configuration")
    if isinstance(mlc, dict) and isinstance(mlc.get("inputs"), dict):
        return mlc["inputs"]
    if isinstance((config or {}).get("inputs"), dict):  # tolerate flat shape
        return config["inputs"]
    return {}


def _feature_specs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    feats = (_inputs_block(config) or {}).get("features", [])
    out = []
    for f in feats or []:
        if isinstance(f, dict):
            out.append(f)
        elif isinstance(f, str):
            out.append({"name": f})
    return out


def _names_and_ranges(config) -> Tuple[List[str], List[Tuple[float, float]]]:
    names, ranges = [], []
    for f in _feature_specs(config):
        names.append(str(f.get("name", f"x[{len(names)}]")))
        er = f.get("expected_range") or {}
        lo, hi = er.get("min"), er.get("max")
        try:
            lo = float(lo); hi = float(hi)
            if hi <= lo:
                hi = lo + 1.0
        except (TypeError, ValueError):
            lo, hi = 0.0, 1.0
        ranges.append((lo, hi))
    return names, ranges


def _sample_background(ranges, n=_BG_N, seed=0):
    import numpy as np
    rng = np.random.default_rng(seed)
    cols = [rng.uniform(lo, hi, size=n) for (lo, hi) in ranges]
    return np.column_stack(cols) if cols else np.empty((n, 0))


# ---------------------------------------------------------------------------
# Tree capabilities
# ---------------------------------------------------------------------------
def _pick_tree(model):
    if hasattr(model, "tree_"):
        return model
    est = getattr(model, "estimators_", None)
    if est is None:
        return None
    try:
        first = est[0]
    except Exception:
        return None
    if hasattr(first, "tree_"):
        return first
    try:
        first = first[0]
    except Exception:
        return None
    return first if hasattr(first, "tree_") else None


def _extract_subtree(tree_est, names):
    t = tree_est.tree_
    feat, thr = t.feature, t.threshold
    cl, cr, val = t.children_left, t.children_right, t.value

    def leaf_val(i):
        try:
            return float(val[i].ravel()[0])
        except Exception:
            return 0.0

    def is_leaf(i):
        return bool(cl[i] == -1)

    def split_label(i):
        fi = feat[i]
        nm = names[fi] if 0 <= fi < len(names) else f"x[{fi}]"
        return f"{nm} ≤ {thr[i]:.2f}"

    out = {"n0": {"leaf": is_leaf(0),
                  "label": (f"{leaf_val(0):.2f}" if is_leaf(0) else split_label(0))}}
    for nkey, lL, lR, child in (("n1", "l1", "l2", cl[0]), ("n2", "l3", "l4", cr[0])):
        if child == -1:
            out[nkey] = {"leaf": True, "label": ""}
            out[lL] = {"leaf": True, "label": ""}
            out[lR] = {"leaf": True, "label": ""}
            continue
        out[nkey] = {"leaf": is_leaf(child),
                     "label": (f"{leaf_val(child):.2f}" if is_leaf(child) else split_label(child))}
        gl, gr = cl[child], cr[child]
        out[lL] = {"leaf": True, "label": (f"{leaf_val(gl):.2f}" if gl != -1 else "")}
        out[lR] = {"leaf": True, "label": (f"{leaf_val(gr):.2f}" if gr != -1 else "")}
    return out


def _tree_caps(model, names, res, caps):
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return
    res["importances"] = sorted(zip(names, [float(v) for v in importances]),
                                key=lambda p: p[1], reverse=True)
    caps.append("impurity")
    tree_est = _pick_tree(model)
    if tree_est is None:
        return
    try:
        from sklearn.tree import export_text
        res["rules_text"] = export_text(tree_est, feature_names=list(names), max_depth=3)
        caps.append("rules")
    except Exception as exc:
        logger.debug("export_text failed: %s", exc)
    try:
        res["subtree"] = _extract_subtree(tree_est, names)
        caps.append("tree")
    except Exception as exc:
        logger.debug("subtree failed: %s", exc)


# ---------------------------------------------------------------------------
# Linear capability
# ---------------------------------------------------------------------------
def _linear_caps(model, names, res, caps):
    import numpy as np
    coef = getattr(model, "coef_", None)
    if coef is None:
        return
    c = np.asarray(coef)
    if c.ndim > 1:
        if c.shape[-1] == len(names):
            c = c[0]
        elif c.shape[0] == len(names):
            c = c[:, 0]
        else:
            c = c.ravel()
    c = np.asarray(c).ravel()
    if len(c) != len(names):
        return
    res["coef"] = sorted(zip(names, [float(v) for v in c]),
                         key=lambda p: abs(p[1]), reverse=True)
    ic = getattr(model, "intercept_", None)
    try:
        res["intercept"] = float(np.ravel(ic)[0]) if ic is not None else None
    except Exception:
        res["intercept"] = None
    caps.append("coef")


# ---------------------------------------------------------------------------
# Data-backed capabilities
# ---------------------------------------------------------------------------
def _estimator_for_pdp(model, scaler):
    if scaler is None:
        return model
    try:
        from sklearn.pipeline import Pipeline
        return Pipeline([("scaler", scaler), ("model", model)])
    except Exception:
        return model


def _pdp_caps(model, scaler, X, names, res, caps):
    from sklearn.inspection import partial_dependence
    est = _estimator_for_pdp(model, scaler)
    pdp = {}
    for i, nm in enumerate(names):
        try:
            pd_ = partial_dependence(est, X, [i], grid_resolution=_PDP_GRID, kind="average")
            grid = pd_.get("grid_values", pd_.get("values"))
            pdp[nm] = {"x": [float(v) for v in grid[0]],
                       "y": [float(v) for v in pd_["average"][0]]}
        except Exception as exc:
            logger.debug("pdp failed for %s: %s", nm, exc)
    if pdp:
        res["pdp"] = pdp
        caps.append("pdp")


def _shap_caps(model, scaler, X, names, family, res, caps):
    import numpy as np
    try:
        import shap
    except Exception as exc:
        logger.info("shap not available: %s", exc)
        return
    is_tree = family in ("tree_single", "tree_ensemble")
    is_linear = family == "linear"
    if scaler is not None or not (is_tree or is_linear):
        return
    try:
        expl = shap.TreeExplainer(model) if is_tree else shap.LinearExplainer(model, X)
        sv = expl.shap_values(X)
        if isinstance(sv, list):
            sv = sv[0]
        sv = np.asarray(sv)
        base = expl.expected_value
        base = float(np.ravel(base)[0]) if np.ndim(base) else float(base)
    except Exception as exc:
        logger.info("shap compute failed: %s", exc)
        return

    order = list(np.argsort(np.abs(sv).mean(axis=0))[::-1])
    points = {}
    for j in order:
        col = X[:, j].astype(float)
        span = (col.max() - col.min()) or 1.0
        points[names[j]] = {"shap": [float(v) for v in sv[:, j]],
                            "fval": [float((v - col.min()) / span) for v in col]}
    res["shap_summary"] = {"features": [names[j] for j in order], "points": points}

    instances = {}
    for idx in range(1, min(_MAX_INSTANCES, sv.shape[0]) + 1):
        row = sv[idx - 1]
        pairs = sorted(zip(names, [float(v) for v in row]),
                       key=lambda p: abs(p[1]), reverse=True)[:8]
        instances[str(idx)] = {"pairs": pairs, "base": base,
                               "pred": float(base + float(row.sum()))}
    res["shap_instances"] = instances
    caps.append("shap")


def _perm_caps(model, scaler, X, y, names, res, caps):
    from sklearn.inspection import permutation_importance
    est = _estimator_for_pdp(model, scaler)
    r = permutation_importance(est, X, y, n_repeats=5, random_state=0)
    res["perm_importance"] = sorted(zip(names, [float(v) for v in r.importances_mean]),
                                    key=lambda p: p[1], reverse=True)
    caps.append("permutation")


# ---------------------------------------------------------------------------
# Public entry points (model already loaded by the registry)
# ---------------------------------------------------------------------------
def _base_result(model, names, source, background):
    return {
        "ok": True, "source": source, "model_class": type(model).__name__,
        "feature_names": names,
        "n_estimators": int(getattr(model, "n_estimators", 0) or 0),
        "max_depth": (int(model.max_depth) if getattr(model, "max_depth", None) is not None else None),
        "background": background, "capabilities": [],
    }


def explain(model, config, scaler=None, family=None) -> Dict[str, Any]:
    if model is None:
        return {"ok": False, "reason": "model not loaded (R model or unsupported artifact)"}
    names, ranges = _names_and_ranges(config)
    res = _base_result(model, names, "sklearn",
                       f"sampled uniformly from declared operating ranges (n={_BG_N})")
    res["scaled"] = scaler is not None
    caps = res["capabilities"]
    for fn in (lambda: _tree_caps(model, names, res, caps),
               lambda: _linear_caps(model, names, res, caps)):
        try:
            fn()
        except Exception as exc:
            logger.debug("data-free cap failed: %s", exc)
    if names:
        try:
            import numpy as np  # noqa: F401
            X = _sample_background(ranges, seed=abs(hash(res["model_class"])) % (2**32))
            for fn in (lambda: _pdp_caps(model, scaler, X, names, res, caps),
                       lambda: _shap_caps(model, scaler, X, names, family or "", res, caps)):
                try:
                    fn()
                except Exception as exc:
                    logger.debug("data-backed cap failed: %s", exc)
        except Exception as exc:
            logger.debug("background failed: %s", exc)
    return res


def explain_with_data(model, config, scaler, family, X, y=None) -> Dict[str, Any]:
    if model is None:
        return {"ok": False, "reason": "model not loaded (R model or unsupported artifact)"}
    import numpy as np
    names, _ = _names_and_ranges(config)
    try:
        if hasattr(X, "columns"):
            missing = [c for c in names if c not in X.columns]
            if missing:
                return {"ok": False, "reason": f"missing columns: {', '.join(missing)}"}
            Xv = X[names].to_numpy(dtype=float)
        else:
            Xv = np.asarray(X, dtype=float)
        if Xv.ndim != 2 or Xv.shape[1] != len(names):
            return {"ok": False, "reason": f"expected {len(names)} feature columns, got {Xv.shape}"}
    except Exception as exc:
        return {"ok": False, "reason": f"data shape: {exc}"}

    res = _base_result(model, names, "uploaded", f"uploaded data (n={Xv.shape[0]})")
    res["scaled"] = scaler is not None
    caps = res["capabilities"]
    steps = [lambda: _tree_caps(model, names, res, caps),
             lambda: _linear_caps(model, names, res, caps),
             lambda: _pdp_caps(model, scaler, Xv, names, res, caps),
             lambda: _shap_caps(model, scaler, Xv, names, family or "", res, caps)]
    if y is not None:
        steps.append(lambda: _perm_caps(model, scaler, Xv, np.asarray(y), names, res, caps))
    for fn in steps:
        try:
            fn()
        except Exception as exc:
            logger.debug("explain_with_data cap failed: %s", exc)
    return res
