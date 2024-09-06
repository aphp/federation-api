from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from platform_registry.api import deps
from platform_registry.models import User
from platform_registry.services import platforms, access_keys
from platform_registry import schemas
from platform_registry.core import database

router = APIRouter()
keys_router = APIRouter(prefix="/access-keys")


@router.get(path="/", response_model=list[schemas.Platform],
            summary="List all available active platforms")
async def get_platforms(db: Session = Depends(database.get_db),
                        user: User = Depends(deps.either_platform_or_admin)):
    return platforms.get_platforms(db=db, user=user)


@router.get(path="/recipients", response_model=list[schemas.PlatformRecipient],
            summary="List all available active platforms as recipients to share a project with.")
async def get_recipient_platforms(db: Session = Depends(database.get_db),
                                  user: User = Depends(deps.platform_user)):
    return platforms.get_platforms(db=db, user=user, to_share_project=True)


@router.get(path="/{platform_id}", response_model=schemas.Platform,
            summary="Get a specific platform by its ID")
async def get_platform(platform_id: str,
                       db: Session = Depends(database.get_db),
                       user: User = Depends(deps.registry_admin_user)):
    db_platform = platforms.get_platform_by_id(db=db, platform_id=platform_id)
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return db_platform


@router.post(path="/", response_model=schemas.Platform, status_code=status.HTTP_201_CREATED,
             summary="Create a new platform",
             description="When adding a new platform, the following will be auto-generated:\n\n"
                         "* An associated `user-account` allowing to log into the API.\n\n"
                         "  * Given in the form _`platform-username`_[_platform-user-ID_].\n\n"
                         "* An `Access Key` that will be used as password for authentication.\n\n")
async def create_platform(platform: schemas.PlatformCreate,
                          db: Session = Depends(database.get_db),
                          user: User = Depends(deps.registry_admin_user)):
    return platforms.setup_platform(db=db, platform=platform)


@router.patch(path="/{platform_id}", response_model=schemas.Platform, status_code=status.HTTP_200_OK)
async def patch_platform(platform_id: str,
                         platform_in: schemas.PlatformPatch,
                         db: Session = Depends(database.get_db),
                         user: User = Depends(deps.either_platform_or_admin)):
    if user.platform_id and user.platform_id != platform_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to manage this platform")
    platform = platforms.get_platform_by_id(db=db, platform_id=platform_id)
    if not platform:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found")
    return platforms.update_platform(db=db, platform=platform, platform_in=platform_in)


@keys_router.get(path="/my-keys", response_model=list[schemas.AccessKey])
async def get_platform_access_keys(db: Session = Depends(database.get_db),
                                   user: User = Depends(deps.platform_user)):
    return access_keys.get_platform_access_keys(db=db, platform_id=user.platform_id)


@keys_router.get(path="/", response_model=list[schemas.AccessKey])
async def get_access_keys(db: Session = Depends(database.get_db),
                          user: User = Depends(deps.registry_admin_user)):
    return access_keys.get_access_keys(db=db)


@keys_router.get(path="/{key_id}", response_model=schemas.AccessKey)
async def get_access_key(key_id: str,
                         db: Session = Depends(database.get_db),
                         user: User = Depends(deps.registry_admin_user)):
    access_key = access_keys.get_access_key_by_id(db=db, key_id=key_id)
    if access_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    return access_key


@keys_router.post(path="/", response_model=schemas.AccessKey, status_code=status.HTTP_201_CREATED,
                  summary="Create a new access key for a platform",
                  description="A platform is supposed to have a single _`valid`_ `access key`")
async def create_access_key(access_key: schemas.AccessKeyCreate,
                            db: Session = Depends(database.get_db),
                            user: User = Depends(deps.registry_admin_user)):
    if access_keys.get_platform_current_valid_key(db=db, platform_id=access_key.platform_id) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"This platform '{access_key.platform_id}' has an ongoing valid access key")
    return access_keys.create_access_key(db=db, access_key=access_key)


@keys_router.patch(path="/{key_id}", response_model=schemas.AccessKey,
                   summary="Update validity dates for an existing access key")
async def patch_access_key(key_id: str,
                           key_in: schemas.AccessKeyPatch,
                           db: Session = Depends(database.get_db),
                           user: User = Depends(deps.registry_admin_user)):
    valid, msg = access_keys.check_access_key_validity(key_in=key_in)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    key = access_keys.get_access_key_by_id(db=db, key_id=key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    return access_keys.update_access_key(db=db, key=key, key_in=key_in)


@keys_router.patch(path="/{key_id}/archive", response_model=schemas.AccessKey,
                   summary="Set an end of validity date to the access key with the given ID.")
async def archive_access_key(key_id: str,
                             db: Session = Depends(database.get_db),
                             user: User = Depends(deps.registry_admin_user)):
    key = access_keys.get_access_key_by_id(db=db, key_id=key_id)
    if not key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Access key not found")
    return access_keys.archive_access_key(db=db, key=key)

router.include_router(keys_router)
