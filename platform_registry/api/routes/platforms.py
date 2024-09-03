from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.api import deps
from platform_registry.services import platforms, access_keys
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()
keys_router = APIRouter(prefix="/access-keys")


@router.get("/", response_model=list[schemas.Platform])
async def get_platforms(db: Session = Depends(database.get_db),
                        user: schemas.User = Depends(deps.either_platform_or_admin)):
    return platforms.get_platforms(db=db, user=user)


@router.get("/project-share", response_model=list[schemas.PlatformRecipient])
async def get_platforms_to_share_project(db: Session = Depends(database.get_db),
                                         user: schemas.User = Depends(deps.platform_user)):
    return platforms.get_platforms(db=db, user=user, to_share_project=True)


@router.get("/{platform_id}", response_model=schemas.Platform)
async def get_platform(platform_id: str,
                       db: Session = Depends(database.get_db),
                       user: schemas.User = Depends(deps.registry_admin_user)):
    db_platform = platforms.get_platform_by_id(db=db, platform_id=platform_id)
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return db_platform


@router.post("/", response_model=schemas.Platform, status_code=status.HTTP_201_CREATED)
async def create_platform(platform: schemas.PlatformCreate,
                          db: Session = Depends(database.get_db),
                          user: schemas.User = Depends(deps.registry_admin_user)):
    return platforms.setup_platform(db=db, platform=platform)


@keys_router.get("/my-keys", response_model=list[schemas.AccessKey])
async def get_platform_access_keys(db: Session = Depends(database.get_db),
                                   user: schemas.User = Depends(deps.platform_user)):
    return access_keys.get_platform_access_keys(db=db, platform_id=user.platform_id)


@keys_router.get("/", response_model=list[schemas.AccessKey])
async def get_access_keys(db: Session = Depends(database.get_db),
                          user: schemas.User = Depends(deps.registry_admin_user)):
    return access_keys.get_access_keys(db=db)


@keys_router.get("/{key_id}", response_model=schemas.AccessKey)
async def get_access_key(key_id: str,
                         db: Session = Depends(database.get_db),
                         user: schemas.User = Depends(deps.registry_admin_user)):
    access_key = access_keys.get_access_key_by_id(db=db, key_id=key_id)
    if access_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    return access_key


@keys_router.post("/", response_model=schemas.AccessKey, status_code=status.HTTP_201_CREATED)
async def create_access_key(access_key: schemas.AccessKeyCreate,
                            db: Session = Depends(database.get_db),
                            user: schemas.User = Depends(deps.registry_admin_user)):
    if access_keys.get_platform_current_valid_key(db=db, platform_id=access_key.platform_id) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"This platform '{access_key.platform_id}' has an ongoing valid access key")
    return access_keys.create_access_key(db=db, access_key=access_key)


@keys_router.patch("/{key_id}", response_model=schemas.AccessKey)
async def patch_access_key(key_id: str,
                           key_in: schemas.AccessKeyPatch,
                           db: Session = Depends(database.get_db),
                           user: schemas.User = Depends(deps.registry_admin_user)):
    valid, msg = access_keys.check_access_key_validity(key_in=key_in)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    key = access_keys.get_access_key_by_id(db=db, key_id=key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    return access_keys.update_access_key(db=db, key=key, key_in=key_in)


@keys_router.patch("/{key_id}/archive", response_model=schemas.AccessKey)
async def archive_access_key(key_id: str,
                             db: Session = Depends(database.get_db),
                             user: schemas.User = Depends(deps.registry_admin_user)):
    key = access_keys.get_access_key_by_id(db=db, key_id=key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    return access_keys.archive_access_key(db=db, key=key)

router.include_router(keys_router)
