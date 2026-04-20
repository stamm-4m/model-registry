from model_registry.backend.repositories.organization_repository import OrganizationRepository
from model_registry.backend.core.exceptions import OrganizationInUseException


class OrganizationService:

    def create_organization(self, name, location):
        repo = OrganizationRepository()
        org = repo.create(name, location)
        repo.close()
        return org

    def get_organization(self, organization_id):
        repo = OrganizationRepository()
        org = repo.get_by_id(organization_id)
        repo.close()
        return org

    def get_all_organizations(self):
        repo = OrganizationRepository()
        orgs = repo.get_all()
        repo.close()
        return orgs

    def update_organization(self, organization_id, name=None, location=None):
        repo = OrganizationRepository()
        org = repo.update(organization_id, name=name, location=location)
        repo.close()
        return org

    def delete_organization(self, organization_id):
        repo = OrganizationRepository()

        deps = repo.get_dependency_counts(organization_id)

        if deps["departments"] > 0 or deps["users"] > 0:
            repo.close()
            raise OrganizationInUseException(
                departments=deps["departments"],
                users=deps["users"]
            )

        result = repo.delete(organization_id)
        repo.close()

        return result
    