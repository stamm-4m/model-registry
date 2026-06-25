from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ExplainRequest(BaseModel):
    """Body for POST /{project_id}/explain/{model_id}.

    All fields optional. With no body the explainer uses a background sampled
    from each feature's declared operating range. Provide `rows` (records from
    an uploaded CSV) to evaluate on real data; include `target_column` to also
    compute permutation importance.
    """
    family: Optional[str] = None
    rows: Optional[List[Dict[str, Any]]] = None
    target_column: Optional[str] = None
