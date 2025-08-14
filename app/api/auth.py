from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.db import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.models.user import User, AuthProvider
from app.models.workspace import Workspace
from app.models import UserWorkspaceRole, UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and create a workspace"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create workspace
    workspace = Workspace(
        name=user_data.workspace_name,
        description=f"Workspace for {user_data.email}"
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        auth_provider=AuthProvider.EMAIL,
        is_verified=True  # Auto-verify for MVP
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign user as admin of the workspace
    user_role = UserWorkspaceRole(
        user_id=user.id,
        workspace_id=workspace.id,
        role=UserRole.ADMIN
    )
    db.add(user_role)
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "workspace_id": workspace.id,
            "role": UserRole.ADMIN.value
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            auth_provider=user.auth_provider.value,
            created_at=user.created_at
        )
    )

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    
    # Get user's primary workspace (for MVP, assume first workspace)
    user_role = db.query(UserWorkspaceRole).filter(
        UserWorkspaceRole.user_id == user.id
    ).first()
    
    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no workspace access"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "workspace_id": user_role.workspace_id,
            "role": user_role.role.value
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            auth_provider=user.auth_provider.value,
            created_at=user.created_at
        )
    )

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    from app.core.security import verify_token
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_with_workspace(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> tuple[User, int, str]:
    """Get current user with workspace context"""
    from app.core.security import verify_token
    
    # Get token from request
    token = oauth2_scheme.__call__(None)
    payload = verify_token(token)
    
    workspace_id = payload.get("workspace_id")
    role = payload.get("role")
    
    if not workspace_id or not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token: missing workspace or role"
        )
    
    return current_user, workspace_id, role
