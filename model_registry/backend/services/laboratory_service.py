from model_registry.backend.core.exceptions import LaboratoryInUseException
from model_registry.backend.models.departament_laboratory import DepartmentLaboratory
from model_registry.backend.repositories.laboratory_repository import LaboratoryRepository


class LaboratoryService:

    def get_by_department(self, department_id):
        repo = LaboratoryRepository()
        labs = repo.get_by_department(department_id)
        repo.close()
        return labs

    def create_laboratory(self, name, location,  department_id):
        repo = LaboratoryRepository()
        lab = repo.create(name, location, department_id)
        repo.close()
        return lab
    def get_laboratory_all(self):
        repo = LaboratoryRepository()
        labs = repo.get_all()
        repo.close()
        return labs
    def get_laboratory_with_dept(self, laboratory_id):
        repo = LaboratoryRepository()
        result = repo.get_with_department(laboratory_id)
        repo.close()
        return result
    def update_laboratory(self, laboratory_id, name=None, location=None, department_id=None):
        repo = LaboratoryRepository()

        lab = repo.update(
            laboratory_id=laboratory_id,
            name=name,
            location=location,
            department_id=department_id
        )

        repo.close()
        return lab

    def delete_laboratory(self, laboratory_id):
        repo = LaboratoryRepository()

        # Validar si el laboratorio está asociado a algún departamento
        lab_count = (
            repo.db.query(DepartmentLaboratory)
            .filter(DepartmentLaboratory.laboratory_id == laboratory_id)
            .count()
        )

        if lab_count > 0:
            repo.close()
            raise LaboratoryInUseException(departments=lab_count)

        result = repo.delete(laboratory_id)
        repo.close()

        return result
    
    def get_labs_by_department(self, department_id):
        repo = LaboratoryRepository()
        labs = repo.get_by_department(department_id)
        repo.close()
        return labs
    
    def get_laboratory(self, laboratory_id):
        repo = LaboratoryRepository()
        lab = repo.get_by_id(laboratory_id)
        repo.close()
        return lab

    def get_laboratory_by_user_id(self, user_id):
        repo = LaboratoryRepository()
        lab = repo.get_laboratory_by_user_id(user_id)
        repo.close()
        return lab
