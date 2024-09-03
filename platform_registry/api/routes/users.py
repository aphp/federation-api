from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.api import deps
from platform_registry.services import users
from platform_registry import schemas
from platform_registry.core import database
from platform_registry.api.deps import registry_admin_user

router = APIRouter(dependencies=[Depends(registry_admin_user)])


@router.get("/", response_model=list[schemas.User])
async def get_users(db: Session = Depends(database.get_db),
                    user: schemas.User = Depends(deps.either_platform_or_admin)):
    if user.role.is_registry_admin:
        return users.get_all_users(db=db)
    return users.get_regular_users(db=db)


@router.get("/{username}", response_model=schemas.User)
async def get_user(username: str,
                   db: Session = Depends(database.get_db),
                   user: schemas.User = Depends(deps.either_platform_or_admin)):
    db_user = users.get_user_by_username(db=db, username=username, user=user)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.RegularUserCreate,
                      db: Session = Depends(database.get_db),
                      user: schemas.User = Depends(deps.registry_admin_user)):
    # create only regular users by Registry Administrator
    db_user = users.get_user_by_username(db=db, username=user_in.username, user=user)
    if db_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER,
                            detail=f"A user is already registered with the given username <{user_in.username}>")
    return users.create_user(db=db, user=user_in)
