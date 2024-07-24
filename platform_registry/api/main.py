import logging

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from platform_registry.api.deps import get_current_active_user
from platform_registry.api.routers import (auth,
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
from platform_registry.core.config import settings

app = FastAPI(openapi_url=settings.OPENAPI_URL,
              dependencies=[Depends(get_current_active_user)],)

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(roles.router, prefix="/roles", tags=["Roles"])
app.include_router(entity_types.router, prefix="/entity_types", tags=["Entity Types"])
app.include_router(regulatory_frameworks.router, prefix="/regulatory_frameworks", tags=["Regulatory Frameworks"])
app.include_router(entities.router, prefix="/entities", tags=["Entities"])
app.include_router(project_membership.router, prefix="/project_memberships", tags=["Project Memberships"])
app.include_router(project_regulatory_framework.router, prefix="/project_regulatory_frameworks", tags=["Project Regulatory Frameworks"])
app.include_router(platforms.router, prefix="/platforms", tags=["Platforms"])
app.include_router(platform_shared_projects.router, prefix="/platform_shared_projects", tags=["Platform Shared Projects"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])

logging.basicConfig(filename=settings.LOG_FILE, level=logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=settings.PROJECT_NAME,
                                 version=settings.PROJECT_VERSION,
                                 description=settings.PROJECT_DESC,
                                 routes=app.routes)
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run('app:app', host='0.0.0.0', port=5000, reload=True)

