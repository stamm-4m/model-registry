from model_registry.backend.repositories.experiment_repository import ExperimentRepository
from model_registry.backend.models.experiment import Experiment

class ExperimentService:
    def __init__(self):
        self.repo = ExperimentRepository()

    def get_all_experiments(self):
        return self.repo.get_all_experiments()

    def get_experiment_by_id(self, experiment_id):
        return self.repo.get_experiment_by_id(experiment_id)

    def update_experiment(self, experiment_id, name=None, project_id=None, description=None, initial_conditions=None, set_points=None, start_time=None, end_time=None):
        return self.repo.update_experiment(
            experiment_id,
            name=name,
            project_id=project_id,
            description=description,
            initial_conditions=initial_conditions,
            set_points=set_points,
            start_time=start_time,
            end_time=end_time
        )
    
    def add_experiment(self, **kwargs):
        experiment = Experiment(**kwargs)
        return self.repo.add_experiment(experiment)

    def delete_experiment(self, experiment_id):
        return self.repo.delete_experiment(experiment_id)
