from datetime import datetime

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from platform_registry.crud import users
from platform_registry import models
from platform_registry.core import database
from platform_registry.core.security import TokenPayload
from platform_registry.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenPayload(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = users.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def current_active_user(user: models.User = Depends(current_user)):
    if user.expiration_date <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    return user


def registry_admin_user(user: models.User = Depends(current_active_user)):
    if not (user.role and user.role.is_registry_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions: requires a Registry Admin account")
    return user


def platform_user(user: models.User = Depends(current_active_user)):
    if not (user.role and user.role.is_platform):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions: requires a Platform account")
    return user


def either_platform_or_admin(user: models.User = Depends(current_active_user)):
    if not user.role or not (user.role.is_platform or user.role.is_registry_admin):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions: requires a Platform or Registry Administrator account")
    return user


def get_regulatory_frameworks_reader(user: models.User = Depends(current_active_user)):
    if not (user.role.is_platform or user.role.is_registry_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Not enough permissions: requires a Platform or Registry Administrator account")
    return user


def regulatory_frameworks_manager(user: models.User = Depends(registry_admin_user)):
    return user

