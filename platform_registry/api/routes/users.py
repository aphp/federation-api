from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import users
from platform_registry import schemas
from platform_registry.core import database
from platform_registry.api.deps import registry_admin_user

router = APIRouter(dependencies=[Depends(registry_admin_user)])


@router.get("/", response_model=list[schemas.User])
async def get_users(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return users.get_all_users(db, skip=skip, limit=limit)


@router.get("/{username}", response_model=schemas.User)
async def get_user(username: str, db: Session = Depends(database.get_db)):
    db_user = users.get_user(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = users.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"A user is already registered with the given email address <{user.email}>")
    user_valid = users.check_user_against_linked_role(db=db, user=user)
    if not user_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="")
    return users.create_user(db=db, user=user)
