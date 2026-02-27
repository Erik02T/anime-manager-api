import logging

from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user

logger = logging.getLogger(__name__)


def require_roles(*allowed_roles: str):
    def dependency(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            logger.warning(
                "permission.denied",
                extra={
                    "user_id": current_user.id,
                    "role": current_user.role,
                    "allowed_roles": ",".join(allowed_roles),
                },
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency
