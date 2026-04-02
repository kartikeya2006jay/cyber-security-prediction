from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.config import get_settings
from app.core.rate_limiter import limiter
from app.dependencies.role_guard import get_current_user, role_required
from app.models.user_model import UserRole
from app.schemas.auth_schema import (
    CreateUserRequest,
    LoginRequest,
    TokenResponse,
    UpdateUserRoleRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_user,
    delete_user,
    list_users,
    update_user_role,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
) -> TokenResponse:
    user_agent = request.headers.get("user-agent", "unknown")
    client_ip = request.client.host if request.client else "unknown"

    try:
        user, token, expires_in = await authenticate_user(payload, client_ip, user_agent)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    settings = get_settings()
    response.set_cookie(
        key=settings.token_cookie_name,
        value=token,
        httponly=True,
        secure=settings.token_cookie_secure,
        samesite="lax",
        max_age=expires_in,
    )

    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        role=UserRole(user["role"]),
    )


@router.post(
    "/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_route(
    payload: CreateUserRequest,
    _: dict = Depends(role_required(UserRole.SUPER_ADMIN)),
) -> UserResponse:
    try:
        user = await create_user(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UserResponse(**user)


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return UserResponse(**current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> Response:
    settings = get_settings()
    response.delete_cookie(key=settings.token_cookie_name)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/users", response_model=list[UserResponse])
async def get_users(
    _: dict = Depends(role_required(UserRole.SUPER_ADMIN)),
) -> list[UserResponse]:
    users = await list_users()
    return [UserResponse(**user) for user in users]


@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role_route(
    user_id: str,
    payload: UpdateUserRoleRequest,
    _: dict = Depends(role_required(UserRole.SUPER_ADMIN)),
) -> UserResponse:
    try:
        updated = await update_user_role(user_id, payload.role)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return UserResponse(**updated)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
    user_id: str,
    _: dict = Depends(role_required(UserRole.SUPER_ADMIN)),
) -> Response:
    try:
        await delete_user(user_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
