from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from platform_registry.schemas import LoginResponse
from platform_registry.core import database
from platform_registry.core.security import create_access_token, authenticate_user
from platform_registry.services import users

router = APIRouter()


@router.post("/auth/login", response_model=LoginResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Session = Depends(database.get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    user = users.update_user_last_login(db, user)
    token = create_access_token(data={"sub": user.username})
    return LoginResponse(access_token=token.access_token,
                         username=user.username,
                         firstname=user.firstname,
                         lastname=user.lastname,
                         email=user.email,
                         last_login=user.last_login,
                         role=user.role and user.role.name,
                         is_admin=user.role and user.role.is_registry_admin)
