from pydantic import BaseModel

class PredictionRequest(BaseModel):
    req: dict   # Contains "input_data"
