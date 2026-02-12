# 🚀 Quick Setup: Enhanced Login System

## What's New

Your INBLOODO Agent now has an **enhanced authentication system** with:

✅ **User Management** - Create multiple user accounts  
✅ **Password Hashing** - Secure bcrypt password storage  
✅ **JWT Tokens** - Industry-standard token authentication  
✅ **Role-Based Access** - Admin, Doctor, Patient roles  
✅ **Registration Page** - Users can self-register  
✅ **Default Test Users** - Pre-configured accounts for testing  

---

## 📋 Prerequisites

The enhanced system requires these additional Python packages:

```bash
pip install passlib[bcrypt] python-jose[cryptography] pyjwt
```

---

## 🎯 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd "c:\Users\rakes\Downloads\blood report ai"
pip install passlib[bcrypt] python-jose[cryptography] pyjwt
```

### Step 2: Update Your API (Optional)

To use the enhanced authentication, modify your `src/api_optimized.py`:

**Option A (Recommended): Add registration endpoint**

Add this import at the top:
```python
from src.auth_enhanced import (
    authenticate_user, create_access_token, create_user,
    get_current_user, User
)
from pydantic import BaseModel, EmailStr
```

Add this model after `LoginRequest`:
```python
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "patient"
```

Add this endpoint after the login endpoint:
```python
@app.post("/api/register/")
async def api_register(data: RegisterRequest):
    """User registration endpoint"""
    try:
        user = create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            role=data.role
        )
        return {
            "status": "success",
            "message": "User created successfully",
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Registration error")
        raise HTTPException(status_code=500, detail="Registration failed")
```

Update the login endpoint to use enhanced auth:
```python
@app.post("/api/login/")
async def api_login(data: LoginRequest):
    """Enhanced authentication endpoint"""
    from src.auth_enhanced import authenticate_user, create_access_token
    from datetime import timedelta
    
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }
```

**Option B (Quick Test): Use enhanced login page with existing backend**

The enhanced login page works with your current system! Just:
1. Rename `templates/login.html` to `templates/login_original.html`
2. Rename `templates/login_enhanced.html` to `templates/login.html`
3. Start your server normally

---

### Step 3: Test It!

```bash
# Start the server
python launch_server.py

# Open browser to http://localhost:8000/login

# Try these test credentials:
# Username: admin    | Password: admin123
# Username: doctor   | Password: doctor123
# Username: patient  | Password: patient123
# Username: test     | Password: secret
```

---

## 🎨 What You Get

### 1. **Original Login Page** (`templates/login.html`)
- Simple username/password authentication
- Works with current API_KEY system
- Premium glassmorphism design

### 2. **Enhanced Login Page** (`templates/login_enhanced.html`)
- **Login Tab**: Sign in with existing account
- **Register Tab**: Create new account
- **Test Credentials Display**: Shows available test accounts
- **Better UX**: Form validation, success/error messages
- **Same Premium Design**: Glassmorphism, animations

### 3. **Enhanced Auth Module** (`src/auth_enhanced.py`)
- Password hashing with bcrypt
- JWT token generation and validation
- In-memory user database (easily switchable to SQL)
- Role-based access control setup
- Backward compatible with existing API_KEY

---

## 👥 Default Test Users

The system auto-creates these users on startup:

| Username | Password    | Role    | Email                  |
|----------|-------------|---------|------------------------|
| admin    | admin123    | admin   | admin@inbloodo.ai      |
| doctor   | doctor123   | doctor  | doctor@inbloodo.ai     |
| patient  | patient123  | patient | patient@inbloodo.ai    |
| test     | secret      | patient | test@inbloodo.ai       |

---

## 🔒 Security Features

### Current (Original System)
- ✅ API key validation
- ✅ Session tokens in localStorage
- ✅ CORS protection
- ✅ HTTPS recommended

### New (Enhanced System)
- ✅ **All above, PLUS:**
- ✅ Password hashing with bcrypt
- ✅ JWT tokens with expiration
- ✅ User roles (admin/doctor/patient)
- ✅ Protected user creation
- ✅ Email validation
- ✅ Token refresh capability
- ✅ Account activation status

---

## 📂 File Overview

### New Files Created
```
LOGIN_SYSTEM_DOCUMENTATION.md     # Complete documentation
QUICK_SETUP_LOGIN.md              # This file
src/auth_enhanced.py              # Enhanced authentication module
templates/login_enhanced.html     # Enhanced login/register page
```

### Existing Files (Unchanged)
```
templates/login.html              # Original login page (still works!)
src/auth.py                       # Original auth (still works!)
src/api_optimized.py              # Your API (add registration endpoint)
```

---

## 🎯 Usage Examples

### Login via Browser
1. Go to http://localhost:8000/login
2. Enter username and password
3. Click "Initialize Secure Session"
4. Redirected to dashboard on success

### Register New User (Enhanced Page)
1. Click "Register" tab
2. Enter username, email, password
3. Click "Create Account"
4. Auto-switched to login tab
5. Login with new credentials

### API Authentication (Programmatic)
```python
import requests

# Login
response = requests.post('http://localhost:8000/api/login/', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access_token']

# Use token for API calls
headers = {'x-api-key': token}
response = requests.post(
    'http://localhost:8000/analyze-report/',
    headers=headers,
    files={'file': open('blood_report.pdf', 'rb')}
)
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required
API_KEY=your-secret-api-key-here

# Optional (auto-generated if not set)
JWT_SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=development

# Auto-initialize default users (true/false)
AUTO_INIT_USERS=true
```

### Disable Default Users

If you don't want auto-created test users:

```env
AUTO_INIT_USERS=false
```

Or in code:
```python
# src/auth_enhanced.py
# Comment out the last line:
# initialize_default_users()
```

---

## 🚀 Production Deployment

### Before Going Live

1. **Add Database Storage**
   - Replace in-memory `_users_db` with SQLAlchemy
   - Create `User` table in your database
   - See `LOGIN_SYSTEM_DOCUMENTATION.md` for example

2. **Strengthen Security**
   ```python
   # .env
   ENVIRONMENT=production
   JWT_SECRET_KEY=<strong-random-key>
   API_KEY=<strong-random-key>
   ```

3. **Enable HTTPS**
   - Use SSL certificate
   - Redirect HTTP to HTTPS
   - Secure cookie flags

4. **Add Rate Limiting**
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/login/")
   @limiter.limit("5/minute")  # 5 attempts per minute
   async def api_login(...):
       ...
   ```

5. **Email Verification**
   - Send confirmation emails
   - Require email verification before login
   - Add password reset via email

---

## 🐛 Troubleshooting

### "Module not found: passlib"
```bash
pip install passlib[bcrypt]
```

### "Module not found: jwt"
```bash
pip install pyjwt
```

### "Registration endpoint not found"
You need to add the `/api/register/` endpoint to your `api_optimized.py` (see Step 2, Option A above)

### Default users not created
Check console logs when server starts. Should see:
```
✅ Created default admin user: admin / admin123
✅ Created default doctor user: doctor / doctor123
...
```

If missing, ensure `AUTO_INIT_USERS=true` in `.env`

### Token expired error
Tokens expire after 24 hours. User needs to login again. You can adjust:
```python
# src/auth_enhanced.py
ACCESS_TOKEN_EXPIRE_HOURS = 24  # Change to desired hours
```

---

## 📚 Learn More

- **Full Documentation**: `LOGIN_SYSTEM_DOCUMENTATION.md`
- **Original Auth**: `src/auth.py`
- **Enhanced Auth**: `src/auth_enhanced.py`
- **API Documentation**: http://localhost:8000/docs (when server running)

---

## ✅ Quick Checklist

- [ ] Install bcrypt, pyjwt packages
- [ ] Test enhanced login page
- [ ] (Optional) Add registration endpoint to API
- [ ] Test with default credentials
- [ ] (Optional) Create custom users
- [ ] Review security settings
- [ ] Set strong JWT_SECRET_KEY for production

---

**Status**: Ready to Use ✅  
**Backward Compatible**: Yes ✅  
**Production Ready**: With database migration ⚠️  

---

Need help? Check `LOGIN_SYSTEM_DOCUMENTATION.md` for detailed information!
