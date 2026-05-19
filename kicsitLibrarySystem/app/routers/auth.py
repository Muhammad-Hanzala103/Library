from datetime import timedelta

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_optional_current_user
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.services.activity_log_service import write_activity_log
from app.services.auth_service import authenticate_user
from app.utils.security import create_access_token


router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    current_user: User | None = Depends(get_optional_current_user),
) -> HTMLResponse | RedirectResponse:
    settings = get_settings()
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "app_name": settings.app_name, "error": None},
    )


@router.post("/login")
def login(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse | HTMLResponse:
    settings = get_settings()
    user = authenticate_user(db, username_or_email.strip(), password)
    if user is None:
        write_activity_log(
            db,
            request=request,
            action="FAILED_LOGIN",
            module="Authentication",
            description=f"Failed login attempt for {username_or_email.strip()}",
        )
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "app_name": settings.app_name,
                "error": "Invalid username/email or password.",
                "username_or_email": username_or_email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    write_activity_log(
        db,
        request=request,
        action="LOGIN",
        module="Authentication",
        user=user,
        entity_name="User",
        entity_id=str(user.id),
        description="User logged in successfully.",
    )
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return response


@router.get("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    write_activity_log(
        db,
        request=request,
        action="LOGOUT",
        module="Authentication",
        user=current_user,
        entity_name="User",
        entity_id=str(current_user.id),
        description="User logged out.",
    )
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key=settings.session_cookie_name)
    return response

