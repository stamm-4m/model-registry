from model_registry.backend.models.laboratory import Laboratory
from model_registry.backend.models.departament_laboratory import DepartmentLaboratory
from model_registry.backend.models.laboratory_user import LaboratoryUser
from model_registry.backend.repositories.base_repository import BaseRepository
from model_registry.backend.models.organization_departament import OrganizationDepartment
from model_registry.backend.models.department import Department
from model_registry.backend.models.organization import Organization

class LaboratoryRepository(BaseRepository):
    def get_with_department(self, lab_id):
        result = (
            self.db.query(
                Laboratory, 
                DepartmentLaboratory.department_id
            )
            .join(DepartmentLaboratory, DepartmentLaboratory.department_id == Department.id)
            .filter(Laboratory.id == lab_id)
            .first()
        ) 
        if result:
            lab, dep_id = result
            return lab, dep_id

        return None, None
    
    def get_all(self):
        return (
            self.db.query(
                Laboratory,
                Department.name.label("department_name")
            )
            .join(DepartmentLaboratory, DepartmentLaboratory.laboratory_id == Laboratory.id)
            .join(Department, Department.id == DepartmentLaboratory.department_id)
            .all()
        ) 

    def get_by_id(self, laboratory_id):
        return (
            self.db.query(Laboratory)
            .filter(Laboratory.id == laboratory_id)
            .first()
        )

    def create(self, name, location, department_id):
        laboratory = Laboratory(name=name, location=location)
        self.db.add(laboratory)
        self.db.commit()
        self.db.refresh(laboratory)

        lab_dept = DepartmentLaboratory(
            laboratory_id=laboratory.id,
            department_id=department_id
        )
        self.db.add(lab_dept)
        self.db.commit()

        return laboratory

    def update(self, laboratory_id, name=None, location=None, department_id=None):
        lab = self.get_by_id(laboratory_id)
        if not lab:
            return None

        if name is not None:
            lab.name = name

        if location is not None:
            lab.location = location

        if department_id is not None:
            dept_lab = (
                self.db.query(DepartmentLaboratory)
                .filter(DepartmentLaboratory.laboratory_id == laboratory_id)
                .first()
            )
            if dept_lab:
                dept_lab.department_id = department_id

        self.db.commit()
        self.db.refresh(lab)
        return lab

    def delete(self, laboratory_id):
        lab = self.get_by_id(laboratory_id)
        if not lab:
            return False

        self.db.delete(lab)
        self.db.commit()
        return True
    
    def get_by_department(self, department_id):
        return (
            self.db.query(Laboratory)
            .join(DepartmentLaboratory, DepartmentLaboratory.laboratory_id == Laboratory.id)
            .filter(DepartmentLaboratory.department_id == department_id)
            .all()
        )
    
    def get_laboratory_by_user_id(self, user_id):
        result = (
            self.db.query(Laboratory)
            .join(DepartmentLaboratory, DepartmentLaboratory.laboratory_id == Laboratory.id)
            .join(LaboratoryUser, LaboratoryUser.laboratory_id == Laboratory.id)
            .filter(LaboratoryUser.user_id == user_id)
            .first()
        )
        return result