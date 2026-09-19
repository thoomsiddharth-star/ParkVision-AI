from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, AdminLoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/admin/login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    """
    Administrator Authentication Endpoint.
    Strictly verifies administrator credentials against ADMIN_EMAIL & ADMIN_PASSWORD.
    Does not disclose whether email or password was wrong on failure.
    """
    email_clean = payload.email.strip().lower()
    admin_email_clean = settings.ADMIN_EMAIL.strip().lower()
    
    # Check if credentials match environment configured admin credentials
    is_env_admin = (email_clean == admin_email_clean and payload.password == settings.ADMIN_PASSWORD)
    
    # Check if user exists in database with ADMIN role
    db_admin = db.query(User).filter(User.email.ilike(payload.email), User.role == "ADMIN").first()
    is_db_admin = False
    if db_admin:
        is_db_admin = verify_password(payload.password, db_admin.hashed_password)

    if not is_env_admin and not is_db_admin:
        # Mandatory generic error message requirement:
        # "Invalid administrator credentials. Access denied."
        # Do not reveal whether email or password was incorrect.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_ADMIN_CREDENTIALS", "message": "Invalid administrator credentials. Access denied."}
        )

    # Ensure admin user exists in DB or return admin record
    if not db_admin:
        db_admin = db.query(User).filter(User.email.ilike(settings.ADMIN_EMAIL)).first()
        if not db_admin:
            db_admin = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                full_name="System Administrator",
                role="ADMIN",
                is_active=True
            )
            db.add(db_admin)
            db.commit()
            db.refresh(db_admin)

    token = create_access_token({"sub": str(db_admin.id), "email": db_admin.email, "role": "ADMIN"})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role="ADMIN",
        user=UserResponse.model_validate(db_admin)
    )

@router.post("/login", response_model=TokenResponse)
def user_login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Normal user / unified sign in endpoint."""
    email_clean = payload.email.strip().lower()

    # Check database user
    user = db.query(User).filter(User.email.ilike(payload.email)).first()

    # Special check for admin credentials
    if email_clean == settings.ADMIN_EMAIL.strip().lower() and payload.password == settings.ADMIN_PASSWORD:
        if not user:
            user = User(
                email=settings.ADMIN_EMAIL,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                full_name="System Administrator",
                role="ADMIN",
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
    elif not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_DISABLED", "message": "Account is disabled."}
        )

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user=UserResponse.model_validate(user)
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new normal user."""
    existing = db.query(User).filter(User.email.ilike(payload.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "EMAIL_EXISTS", "message": "A user with this email already exists."}
        )

    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name or payload.email.split("@")[0].capitalize(),
        role="USER",  # Always normal user on self-registration
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "role": "USER"})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role="USER",
        user=UserResponse.model_validate(new_user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile and role."""
    return UserResponse.model_validate(current_user)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint (invalidates session on client)."""
    return {"success": True, "message": f"Successfully logged out {current_user.email}."}
