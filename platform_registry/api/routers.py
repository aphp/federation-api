from fastapi import APIRouter
from platform_registry.api.routes import (auth,
                                          users,
                                          roles,
                                          entity_types,
                                          regulatory_frameworks,
                                          entities,
                                          project_membership,
                                          project_regulatory_framework,
                                          platforms,
                                          platform_shared_projects,
                                          projects)

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(entity_types.router, prefix="/entity_types", tags=["Entity Types"])
api_router.include_router(regulatory_frameworks.router, prefix="/regulatory_frameworks", tags=["Regulatory Frameworks"])
api_router.include_router(entities.router, prefix="/entities", tags=["Entities"])
api_router.include_router(project_membership.router, prefix="/project_memberships", tags=["Project Memberships"])
api_router.include_router(project_regulatory_framework.router, prefix="/project_regulatory_frameworks", tags=["Project Regulatory Frameworks"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["Platforms"])
api_router.include_router(platform_shared_projects.router, prefix="/platform_shared_projects", tags=["Platform Shared Projects"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
