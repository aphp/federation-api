from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from platform_registry.api.routers import api_router
from platform_registry.core.config import settings

app = FastAPI(openapi_url=settings.OPENAPI_URL,
              title=settings.PROJECT_NAME,
              description=settings.DESCRIPTION_MD,
              version=settings.VERSION,)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(CORSMiddleware,
                       allow_origins=[str(origin).strip("/")
                                      for origin in settings.BACKEND_CORS_ORIGINS],
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"])

app.include_router(api_router)
