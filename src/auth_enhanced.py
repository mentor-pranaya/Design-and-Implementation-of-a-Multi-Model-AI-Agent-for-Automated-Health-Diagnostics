"""
Enhanced authentication module with user management
Supports database-backed users with password hashing
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# API Key for backward compatibility
DEFAULT_API_KEY = secrets.token_urlsafe(32)
API_KEY = os.getenv("API_KEY", DEFAULT_API_KEY)

if os.getenv("ENVIRONMENT") != "production":
    logger.info(f"API Key: {API_KEY}")
    secret_prefix = str(SECRET_KEY)[:10] if SECRET_KEY else ""
    logger.info(f"JWT Secret: {secret_prefix}...")

# Security scheme
security = HTTPBearer()


class User:
    """User model for authentication"""
    def __init__(self, id: int, username: str, email: str, 
                 password_hash: str, role: str = "patient", 
                 is_active: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active


# In-memory user store (replace with database in production)
_users_db = {}
_user_counter = 1


def hash_password(password: str) -> str:
    """Hash a password for storage"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_user(username: str, email: str, password: str, role: str = "patient") -> User:
    """Create a new user (in-memory, replace with DB)"""
    global _user_counter
    
    # Check if user exists
    if any(u.username == username for u in _users_db.values()):
        raise ValueError("Username already exists")
    if any(u.email == email for u in _users_db.values()):
        raise ValueError("Email already exists")
    
    user_id = _user_counter
    _user_counter += 1
    
    user = User(
        id=user_id,
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role
    )
    
    _users_db[user_id] = user
    logger.info(f"Created user: {username} (ID: {user_id}, Role: {role})")
    return user


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username"""
    return next((u for u in _users_db.values() if u.username == username), None)


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID"""
    return _users_db.get(user_id)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    # Check default admin credentials first (backward compatibility)
    if password == API_KEY or password == "secret":
        # Return a default admin user
        admin_user = get_user_by_username("admin")
        if not admin_user and username == "admin":
            # Create default admin if it doesn't exist
            try:
                admin_user = create_user("admin", "admin@inbloodo.ai", API_KEY, "admin")
            except ValueError:
                admin_user = get_user_by_username("admin")
        if admin_user or username == "admin":
            return admin_user or User(
                id=0, username=username, email="", 
                password_hash="", role="admin"
            )
    
    # Check database users
    user = get_user_by_username(username)
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    
    # Try JWT token first
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        user = get_user_by_id(int(user_id))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User is inactive")
        
        return user
    except HTTPException:
        # Fall back to API key authentication for backward compatibility
        if token == API_KEY or token == "secret":
            # Return default admin user
            admin_user = get_user_by_username("admin")
            if not admin_user:
                admin_user = User(
                    id=0, username="admin", email="admin@inbloodo.ai",
                    password_hash="", role="admin"
                )
            return admin_user
        raise


def api_key_required(x_api_key: str | None = Header(None)):
    """
    Validate API key from request headers (backward compatible).
    For development, also accept 'secret' as a fallback.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401, 
            detail="API key required. Include 'x-api-key' header."
        )
    
    # Allow 'secret' for development/testing
    if x_api_key == "secret" and os.getenv("ENVIRONMENT") != "production":
        return x_api_key
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key"
        )
    
    return x_api_key


# Initialize default users
def initialize_default_users():
    """Create default users for testing"""
    try:
        # Admin user
        admin = create_user("admin", "admin@inbloodo.ai", "admin123", "admin")
        logger.info(f"✅ Created default admin user: admin / admin123")
        
        # Doctor user
        doctor = create_user("doctor", "doctor@inbloodo.ai", "doctor123", "doctor")
        logger.info(f"✅ Created default doctor user: doctor / doctor123")
        
        # Patient user
        patient = create_user("patient", "patient@inbloodo.ai", "patient123", "patient")
        logger.info(f"✅ Created default patient user: patient / patient123")
        
        # Test user with 'secret' password
        test = create_user("test", "test@inbloodo.ai", "secret", "patient")
        logger.info(f"✅ Created default test user: test / secret")
        
    except ValueError as e:
        logger.debug(f"Default users may already exist: {e}")


# Auto-initialize on import
if os.getenv("AUTO_INIT_USERS", "true").lower() == "true":
    initialize_default_users()
