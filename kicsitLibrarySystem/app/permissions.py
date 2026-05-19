from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.auth import get_current_user
from app.models import User
from app.services.auth_service import get_user_permission_codes


def require_permission(permission_code: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        permissions = get_user_permission_codes(current_user)
        if permission_code not in permissions and "system.manage_all" not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return current_user

    return dependency

