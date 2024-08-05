from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from platform_registry.core import database
from platform_registry.core.security import Token
from platform_registry.core.config import settings
from platform_registry.core.security import create_access_token, authenticate_user

router = APIRouter()


@router.post("/auth/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Session = Depends(database.get_db)) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email address or password",
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    access_token_expires = timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)
    return create_access_token(data={"sub": user.username},
                               expires_delta=access_token_expires)
