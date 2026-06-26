from model_registry.backend.models.experiment import Experiment
from model_registry.backend.repositories.base_repository import BaseRepository


class ExperimentRepository(BaseRepository):
    def update_experiment(
        self,
        experiment_id,
        name=None,
        project_id=None,
        description=None,
        initial_conditions=None,
        set_points=None,
        start_time=None,
        end_time=None,
    ):
        exp = self.get_experiment_by_id(experiment_id)
        if not exp:
            return None
        if name is not None:
            exp.name = name
        if project_id is not None:
            exp.project_id = project_id
        if description is not None:
            exp.description = description
        if initial_conditions is not None:
            exp.initial_conditions = initial_conditions
        if set_points is not None:
            exp.set_points = set_points
        if start_time is not None:
            exp.start_time = start_time
        if end_time is not None:
            exp.end_time = end_time
        self.db.commit()
        self.db.refresh(exp)
        return exp

    def get_all_experiments(self):
        return self.db.query(Experiment).all()

    def get_experiment_by_id(self, experiment_id):
        return self.db.query(Experiment).filter(Experiment.id == experiment_id).first()

    def add_experiment(self, experiment):
        self.db.add(experiment)
        self.db.commit()
        self.db.refresh(experiment)
        return experiment

    def delete_experiment(self, experiment_id):
        exp = self.get_experiment_by_id(experiment_id)
        if exp:
            self.db.delete(exp)
            self.db.commit()
        return exp
