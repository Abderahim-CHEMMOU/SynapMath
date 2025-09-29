from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.dependencies import get_auth_service, get_current_user, oauth2_scheme
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserProfile)
def register(
    payload: schemas.RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> schemas.UserProfile:
    try:
        return auth_service.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/login", response_model=schemas.TokenResponse)
def login(
    payload: schemas.LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> schemas.TokenResponse:
    try:
        token = auth_service.login(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return schemas.TokenResponse(access_token=token)


@router.post("/logout")
def logout(
    _current_user: schemas.UserProfile = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    auth_service.logout(token)
    return {"status": "ok"}


@router.get("/me", response_model=schemas.UserProfile)
def me(current_user: schemas.UserProfile = Depends(get_current_user)) -> schemas.UserProfile:
    return current_user
