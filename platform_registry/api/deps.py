from datetime import datetime

import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from platform_registry import models, crud
from platform_registry.core import database
from platform_registry.core.auth import TokenPayload, oauth2_scheme
from platform_registry.core.config import settings


async def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
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
    user = crud.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if current_user.expiration_date <= datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


# def get_current_active_admin(current_user: models.User = Depends(get_current_active_user)):
#     if "admin" not in [role.name for role in current_user.roles]:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough permissions")
#     return current_user
