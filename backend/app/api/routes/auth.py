from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user, require_roles
from app.schemas.auth import CreateUserRequest, LoginRequest, TokenResponse, UserPublic
from app.services.auth import authenticate_user, create_access_token, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    public_user = UserPublic(
        email=user.email,
        name=user.name,
        role=user.role,
        department=user.department,
    )
    return TokenResponse(access_token=create_access_token(user), user=public_user)


@router.get("/me", response_model=UserPublic)
def me(user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return user


@router.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
def create_new_user(request: CreateUserRequest) -> UserPublic:
    """Admin-only: create a new platform user stored in the database."""
    new_user = create_user(
        email=request.email,
        name=request.name,
        role=request.role,
        department=request.department,
        password=request.password,
    )
    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email already exists or the database is unavailable.",
        )
    return UserPublic(
        email=new_user.email,
        name=new_user.name,
        role=new_user.role,
        department=new_user.department,
    )
