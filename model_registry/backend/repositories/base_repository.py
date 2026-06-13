from model_registry.api.core.database import SessionLocal


class BaseRepository:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()