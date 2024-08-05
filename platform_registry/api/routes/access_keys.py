from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.crud import access_keys
from platform_registry import schemas
from platform_registry.api import deps
from platform_registry.core import database

router = APIRouter()


@router.get("/", response_model=list[schemas.AccessKey])
async def get_access_keys(skip: int = 0,
                          limit: int = 10,
                          db: Session = Depends(database.get_db),
                          user: schemas.User = Depends(deps.either_platform_or_admin)):
    return access_keys.get_access_keys(db, keys_reader=user, skip=skip, limit=limit)


@router.get("/{key_id}", response_model=schemas.AccessKey)
async def get_access_key(key_id: str,
                         db: Session = Depends(database.get_db),
                         user: schemas.User = Depends(deps.either_platform_or_admin)):
    access_key = access_keys.get_access_key(db, key_id=key_id)
    if access_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    if user.role.is_platform and str(user.platform_id) != access_key.platform_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access key does not belong to Platform")
    return access_key


@router.post("/", response_model=schemas.AccessKey)
async def create_access_key(access_key: schemas.AccessKeyCreate,
                            db: Session = Depends(database.get_db),
                            user: schemas.User = Depends(deps.either_platform_or_admin)):
    """
    * a platform user account can create access keys for its own platform
    * an admin user account can create them for all platforms
    """
    if user.role.is_platform and str(user.platform_id) != access_key.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can not create access keys for other platforms")
    return access_keys.create_access_key(db=db, access_key=access_key)


@router.patch("/{key_id}", response_model=schemas.AccessKey)
async def patch_access_key(key_id: str,
                           key_in: schemas.AccessKeyPatch,
                           db: Session = Depends(database.get_db),
                           user: schemas.User = Depends(deps.either_platform_or_admin)):
    valid, msg = access_keys.check_access_key_validity(db=db,
                                                       start=key_in.start_datetime,
                                                       end=key_in.end_datetime)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    key = access_keys.get_access_key(db, key_id=key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if user.role.is_platform and str(user.platform_id) != key.platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This access key belongs to another platform")
    return access_keys.update_access_key(db=db, key=key, key_in=key_in)
