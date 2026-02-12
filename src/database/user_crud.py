"""
Database CRUD Operations for User Management
Handles user creation, retrieval, updates, and OAuth integration
"""
from sqlalchemy.orm import Session
from src.database.models import User, Report
import bcrypt
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Password hashing context (replaced passlib with direct bcrypt)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


# ==================== USER CRUD ====================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_oauth(db: Session, provider: str, provider_id: str) -> Optional[User]:
    """Get user by OAuth provider and ID"""
    return db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_provider_id == provider_id
    ).first()


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "patient",
    full_name: Optional[str] = None,
    oauth_provider: Optional[str] = None,
    oauth_provider_id: Optional[str] = None,
    profile_picture: Optional[str] = None,
    is_verified: bool = False
) -> User:
    """
    Create a new user
    
    Args:
        db: Database session
        username: Unique username
        email: Unique email address
        password: Plain text password (will be hashed)
        role: User role (admin, doctor, patient)
        full_name: Optional full name
        oauth_provider: OAuth provider name (google, facebook, etc.)
        oauth_provider_id: OAuth provider user ID
        profile_picture: URL to profile picture
        is_verified: Whether email is verified
    
    Returns:
        User object
    
    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    if get_user_by_username(db, username):
        raise ValueError(f"Username '{username}' already exists")
    
    # Check if email exists
    if get_user_by_email(db, email):
        raise ValueError(f"Email '{email}' already exists")
    
    # Create user
    hashed_password = hash_password(password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        full_name=full_name,
        role=role,
        is_active=True,
        is_verified=is_verified,
        oauth_provider=oauth_provider,
        oauth_provider_id=oauth_provider_id,
        profile_picture=profile_picture,
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Created user: {username} ({email}) with role {role}")
    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username/email and password
    
    Args:
        db: Database session
        username: Username or email
        password: Plain text password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    # Try to find user by username or email
    user = get_user_by_username(db, username)
    if not user:
        user = get_user_by_email(db, username)
    
    if not user:
        return None
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {username}")
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"User authenticated: {user.username}")
    return user


def update_user(
    db: Session,
    user_id: int,
    **kwargs
) -> Optional[User]:
    """
    Update user information
    
    Args:
        db: Database session
        user_id: User ID
        **kwargs: Fields to update (email, full_name, role, etc.)
    
    Returns:
        Updated user object or None if user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update password separately if provided
    if 'password' in kwargs:
        user.password_hash = hash_password(kwargs.pop('password'))
    
    # Update other fields
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    logger.info(f"Updated user: {user.username}")
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete user (and all associated reports due to cascade)
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        True if deleted, False if user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    username = user.username
    db.delete(user)
    db.commit()
    
    logger.info(f"Deleted user: {username}")
    return True


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def get_users_by_role(db: Session, role: str) -> List[User]:
    """Get users by role"""
    return db.query(User).filter(User.role == role).all()


# ==================== OAUTH INTEGRATION ====================

def get_or_create_oauth_user(
    db: Session,
    provider: str,
    provider_id: str,
    email: str,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    profile_picture: Optional[str] = None
) -> User:
    """
    Get existing OAuth user or create new one
    
    Args:
        db: Database session
        provider: OAuth provider (google, facebook, github, microsoft)
        provider_id: Provider-specific user ID
        email: User email from OAuth
        username: Optional username
        full_name: Optional full name
        profile_picture: Optional profile picture URL
    
    Returns:
        User object
    """
    # Try to find existing user by OAuth credentials
    user = get_user_by_oauth(db, provider, provider_id)
    
    if user:
        # Update last login
        user.last_login = datetime.utcnow()
        if profile_picture:
            user.profile_picture = profile_picture
        db.commit()
        db.refresh(user)
        logger.info(f"OAuth user logged in: {user.username} via {provider}")
        return user
    
    # Try to find existing user by email (link accounts)
    user = get_user_by_email(db, email)
    
    if user:
        # Link OAuth to existing account
        user.oauth_provider = provider
        user.oauth_provider_id = provider_id
        user.is_verified = True  # OAuth providers verify emails
        user.last_login = datetime.utcnow()
        if profile_picture and not user.profile_picture:
            user.profile_picture = profile_picture
        db.commit()
        db.refresh(user)
        logger.info(f"Linked OAuth account: {user.username} with {provider}")
        return user
    
    # Create new user
    if not username:
        username = email.split('@')[0]
        # Ensure username is unique
        base_username = username
        counter = 1
        while get_user_by_username(db, username):
            username = f"{base_username}{counter}"
            counter += 1
    
    # Generate random password (user won't use it, they'll use OAuth)
    import secrets
    random_password = secrets.token_urlsafe(32)
    
    user = create_user(
        db=db,
        username=username,
        email=email,
        password=random_password,
        role="patient",
        full_name=full_name,
        oauth_provider=provider,
        oauth_provider_id=provider_id,
        profile_picture=profile_picture,
        is_verified=True  # OAuth providers verify emails
    )
    
    logger.info(f"Created new OAuth user: {username} via {provider}")
    return user


# ==================== REPORT USER ASSOCIATION ====================

def link_report_to_user(db: Session, report_id: int, user_id: int) -> bool:
    """Link a report to a user"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return False
    
    report.user_id = user_id
    db.commit()
    return True


def get_user_reports(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Report]:
    """Get all reports for a user"""
    return db.query(Report).filter(Report.user_id == user_id).offset(skip).limit(limit).all()


# ==================== INITIALIZATION ====================

def initialize_default_users(db: Session):
    """Initialize default test users if they don't exist"""
    default_users = [
        {
            "username": "admin",
            "email": "admin@inbloodo.ai",
            "password": "admin123",
            "role": "admin",
            "full_name": "System Administrator",
            "is_verified": True
        },
        {
            "username": "doctor",
            "email": "doctor@inbloodo.ai",
            "password": "doctor123",
            "role": "doctor",
            "full_name": "Dr. John Smith",
            "is_verified": True
        },
        {
            "username": "patient",
            "email": "patient@inbloodo.ai",
            "password": "patient123",
            "role": "patient",
            "full_name": "Jane Doe",
            "is_verified": True
        },
        {
            "username": "test",
            "email": "test@inbloodo.ai",
            "password": "secret",
            "role": "patient",
            "full_name": "Test User",
            "is_verified": True
        }
    ]
    
    for user_data in default_users:
        try:
            existing = get_user_by_username(db, str(user_data["username"]))
            if not existing:
                create_user(
                    db=db, 
                    username=str(user_data["username"]),
                    email=str(user_data["email"]),
                    password=str(user_data["password"]),
                    role=str(user_data["role"]),
                    full_name=str(user_data.get("full_name")) if user_data.get("full_name") else None,
                    is_verified=bool(user_data.get("is_verified", False))
                )
                logger.info(f"✅ Created default user: {user_data['username']}")
            else:
                logger.debug(f"Default user already exists: {user_data['username']}")
        except Exception as e:
            logger.error(f"Failed to create user {user_data['username']}: {e}")
    
    logger.info("Default users initialization complete")
