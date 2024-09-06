from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.api import deps
from platform_registry.models import User
from platform_registry.services import users
from platform_registry import schemas
from platform_registry.core import database

regular_users_router = APIRouter(prefix="/regular")
system_users_router = APIRouter(prefix="/system")


@regular_users_router.get(path="/", response_model=list[schemas.RegularUser],
                          summary="List all users who may be assigned as members and work on projects")
async def get_users(db: Session = Depends(database.get_db),
                    user: User = Depends(deps.either_platform_or_admin)):
    return users.get_regular_users(db=db)


@regular_users_router.post(path="/", response_model=schemas.RegularUser, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.RegularUserCreate,
                      db: Session = Depends(database.get_db),
                      user: User = Depends(deps.either_platform_or_admin)):
    db_user = users.get_user_by_username(db=db, username=user_in.username, user=user)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"A user is already registered with the given username <{user_in.username}>")
    return users.create_user(db=db, user=user_in)


@regular_users_router.patch(path="/{username}", response_model=schemas.RegularUser, status_code=status.HTTP_200_OK)
async def patch_user(username: str,
                     user_in: schemas.RegularUserPatch,
                     db: Session = Depends(database.get_db),
                     user: User = Depends(deps.either_platform_or_admin)):
    db_user = users.get_user_by_username(db=db, username=username)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not users.is_user_updatable(user=db_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The target is not a regular user and can not be updated")
    return users.update_user(db=db, user=db_user, user_in=user_in)


@system_users_router.get(path="/", response_model=list[schemas.SystemUser],
                         description="List users able to use this API, who can be authenticated and assigned "
                                     "a `Registry Admin` or `Platform` role")
async def get_system_users(db: Session = Depends(database.get_db),
                           user: User = Depends(deps.registry_admin_user)):
    return users.get_all_users(db=db)
