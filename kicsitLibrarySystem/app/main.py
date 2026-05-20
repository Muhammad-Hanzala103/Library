from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routers import auth as auth_router
from app.routers import catalog
from app.routers import consumers
from app.routers import circulation
from app.routers import dashboard
from app.routers import phase5
from app.routers import phase6
from app.routers import phase7
from app.routers import phase8
from app.routers import settings as settings_router
from app.routers import backup as backup_router


settings = get_settings()
templates = Jinja2Templates(directory="app/templates")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(auth_router.router)
    app.include_router(dashboard.router)
    app.include_router(catalog.router)
    app.include_router(consumers.router)
    app.include_router(circulation.router)
    app.include_router(phase5.router)
    app.include_router(phase6.router)
    app.include_router(phase7.router)
    app.include_router(phase8.router)
    app.include_router(settings_router.router)
    app.include_router(backup_router.router)

    @app.get("/", include_in_schema=False)
    def home() -> RedirectResponse:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    @app.get("/health", tags=["System"])
    def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> HTMLResponse | RedirectResponse:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        if exc.status_code == status.HTTP_403_FORBIDDEN:
            return templates.TemplateResponse(
                "errors/403.html",
                {"request": request, "app_name": settings.app_name},
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return templates.TemplateResponse(
            "errors/error.html",
            {"request": request, "app_name": settings.app_name, "status_code": exc.status_code, "detail": exc.detail},
            status_code=exc.status_code,
        )

    return app


app = create_app()
