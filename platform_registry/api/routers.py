from fastapi import APIRouter
from platform_registry.api.routes import (auth,
                                          users,
                                          roles,
                                          entities,
                                          platforms,
                                          projects,)

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(entities.router, prefix="/entities", tags=["Entities"])
api_router.include_router(platforms.router, prefix="/platforms", tags=["Platforms"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
