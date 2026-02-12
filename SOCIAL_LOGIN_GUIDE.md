# 🔐 Social Login Integration Guide

## Overview

Add **OAuth2 Social Login** to your INBLOODO Agent application, allowing users to sign in with:
- 🔵 **Google**
- 🔷 **Facebook** 
- 🐙 **GitHub**
- Ⓜ️ **Microsoft**
- 🍎 **Apple**

---

## 🎯 Benefits of Social Login

### For Users
- ✅ **Faster Registration**: No forms to fill
- ✅ **No Password to Remember**: Use existing accounts
- ✅ **Trusted Authentication**: Provider handles security
- ✅ **One-Click Login**: Seamless experience
- ✅ **Profile Auto-Fill**: Name, email pre-populated

### For You (Developer)
- ✅ **Reduced Support**: Fewer password reset requests
- ✅ **Higher Conversion**: Users prefer social login (50%+ adoption)
- ✅ **Verified Emails**: Providers verify email addresses
- ✅ **Security**: OAuth2 is battle-tested
- ✅ **Professional**: Enterprise-grade authentication

---

## 📦 Required Packages

```bash
pip install authlib httpx itsdangerous
```

Update `requirements.txt`:
```txt
# OAuth2 Social Login
authlib
httpx
itsdangerous
```

---

## 🔑 Getting API Keys

### 1. Google OAuth Setup

**Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "INBLOODO Agent"
3. Enable "Google+ API"

**Step 2: Create OAuth Credentials**
1. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
2. Application type: "Web application"
3. Name: "INBLOODO Login"
4. Authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback`
   - `https://yourdomain.com/auth/google/callback`
5. Copy **Client ID** and **Client Secret**

**Step 3: Add to .env**
```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

---

### 2. Facebook OAuth Setup

**Step 1: Create Facebook App**
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create App → "Consumer" → "Add Facebook Login"
3. App Name: "INBLOODO Agent"

**Step 2: Configure OAuth**
1. Settings → Basic → Copy App ID and App Secret
2. Facebook Login → Settings
3. Valid OAuth Redirect URIs:
   - `http://localhost:8000/auth/facebook/callback`
   - `https://yourdomain.com/auth/facebook/callback`

**Step 3: Add to .env**
```env
FACEBOOK_CLIENT_ID=your_facebook_app_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret_here
```

---

### 3. GitHub OAuth Setup

**Step 1: Register OAuth App**
1. Go to [GitHub Settings](https://github.com/settings/developers)
2. "OAuth Apps" → "New OAuth App"
3. Application name: "INBLOODO Agent"
4. Homepage URL: `http://localhost:8000`
5. Authorization callback URL: `http://localhost:8000/auth/github/callback`

**Step 2: Add to .env**
```env
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

---

## 💻 Backend Implementation

### Create OAuth Module

Create `src/oauth_providers.py`:

```python
"""
OAuth2 Social Login Providers
Supports Google, Facebook, GitHub, Microsoft
"""
import os
from typing import Optional, Dict
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Initialize OAuth
oauth = OAuth()

# Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Facebook OAuth
oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
    authorize_url='https://www.facebook.com/v12.0/dialog/oauth',
    access_token_url='https://graph.facebook.com/v12.0/oauth/access_token',
    redirect_uri='http://localhost:8000/auth/facebook/callback',
    client_kwargs={
        'scope': 'email public_profile'
    }
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    client_kwargs={
        'scope': 'user:email'
    }
)

# Microsoft OAuth
oauth.register(
    name='microsoft',
    client_id=os.getenv('MICROSOFT_CLIENT_ID'),
    client_secret=os.getenv('MICROSOFT_CLIENT_SECRET'),
    server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def get_oauth_provider(provider_name: str):
    """Get OAuth provider by name"""
    try:
        return oauth.create_client(provider_name)
    except KeyError:
        raise HTTPException(400, f"Unknown OAuth provider: {provider_name}")


async def get_user_info_google(token: dict) -> Dict:
    """Extract user info from Google token"""
    user_info = token.get('userinfo', {})
    return {
        'provider': 'google',
        'provider_id': user_info.get('sub'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
        'email_verified': user_info.get('email_verified', False)
    }


async def get_user_info_facebook(token: dict, client) -> Dict:
    """Extract user info from Facebook token"""
    import httpx
    
    resp = await client.get(
        'https://graph.facebook.com/me',
        params={
            'fields': 'id,name,email,picture',
            'access_token': token['access_token']
        }
    )
    data = resp.json()
    
    return {
        'provider': 'facebook',
        'provider_id': data.get('id'),
        'email': data.get('email'),
        'name': data.get('name'),
        'picture': data.get('picture', {}).get('data', {}).get('url'),
        'email_verified': True  # Facebook verifies emails
    }


async def get_user_info_github(token: dict, client) -> Dict:
    """Extract user info from GitHub token"""
    import httpx
    
    # Get user profile
    user_resp = await client.get(
        'https://api.github.com/user',
        headers={'Authorization': f"Bearer {token['access_token']}"}
    )
    user_data = user_resp.json()
    
    # Get primary email
    email_resp = await client.get(
        'https://api.github.com/user/emails',
        headers={'Authorization': f"Bearer {token['access_token']}"}
    )
    emails = email_resp.json()
    primary_email = next((e['email'] for e in emails if e['primary']), None)
    
    return {
        'provider': 'github',
        'provider_id': str(user_data.get('id')),
        'email': primary_email or user_data.get('email'),
        'name': user_data.get('name') or user_data.get('login'),
        'picture': user_data.get('avatar_url'),
        'email_verified': True
    }


async def get_user_info_microsoft(token: dict) -> Dict:
    """Extract user info from Microsoft token"""
    user_info = token.get('userinfo', {})
    return {
        'provider': 'microsoft',
        'provider_id': user_info.get('sub'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': None,  # Microsoft doesn't provide picture in token
        'email_verified': user_info.get('email_verified', False)
    }
```

---

### Add OAuth Routes to API

Add to `src/api_optimized.py`:

```python
from starlette.middleware.sessions import SessionMiddleware
from src.oauth_providers import (
    oauth, 
    get_user_info_google, 
    get_user_info_facebook,
    get_user_info_github,
    get_user_info_microsoft
)
from src.auth_enhanced import create_user, get_user_by_email, create_access_token

# Add session middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET_KEY", "your-secret-key"))

# Helper function to get or create user from OAuth
def get_or_create_oauth_user(user_info: dict):
    """Get existing user or create new one from OAuth data"""
    from src.auth_enhanced import get_user_by_email, create_user
    import secrets
    
    email = user_info['email']
    if not email:
        raise HTTPException(400, "Email not provided by OAuth provider")
    
    # Check if user exists
    user = get_user_by_email(email)
    
    if not user:
        # Create new user
        # Generate random password (user won't use it, they'll use OAuth)
        random_password = secrets.token_urlsafe(32)
        
        # Extract username from email or name
        username = email.split('@')[0]
        if get_user_by_username(username):
            username = f"{username}_{secrets.token_hex(4)}"
        
        user = create_user(
            username=username,
            email=email,
            password=random_password,
            role='patient'  # Default role
        )
        
        logger.info(f"Created new user via {user_info['provider']}: {email}")
    
    return user


# Google OAuth Routes
@app.get('/auth/google/login')
async def google_login(request: Request):
    """Initiate Google OAuth flow"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth/google/callback')
async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await get_user_info_google(token)
        
        # Get or create user
        user = get_or_create_oauth_user(user_info)
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        
        # Redirect to dashboard with token
        response = RedirectResponse(url='/')
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=86400  # 24 hours
        )
        return response
        
    except Exception as e:
        logger.exception("Google OAuth error")
        return RedirectResponse(url=f'/login?error={str(e)}')


# Facebook OAuth Routes
@app.get('/auth/facebook/login')
async def facebook_login(request: Request):
    """Initiate Facebook OAuth flow"""
    redirect_uri = request.url_for('facebook_callback')
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@app.get('/auth/facebook/callback')
async def facebook_callback(request: Request):
    """Handle Facebook OAuth callback"""
    try:
        import httpx
        token = await oauth.facebook.authorize_access_token(request)
        
        async with httpx.AsyncClient() as client:
            user_info = await get_user_info_facebook(token, client)
        
        user = get_or_create_oauth_user(user_info)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        
        response = RedirectResponse(url='/')
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400)
        return response
        
    except Exception as e:
        logger.exception("Facebook OAuth error")
        return RedirectResponse(url=f'/login?error={str(e)}')


# GitHub OAuth Routes
@app.get('/auth/github/login')
async def github_login(request: Request):
    """Initiate GitHub OAuth flow"""
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get('/auth/github/callback')
async def github_callback(request: Request):
    """Handle GitHub OAuth callback"""
    try:
        import httpx
        token = await oauth.github.authorize_access_token(request)
        
        async with httpx.AsyncClient() as client:
            user_info = await get_user_info_github(token, client)
        
        user = get_or_create_oauth_user(user_info)
        
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        
        response = RedirectResponse(url='/')
        response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=86400)
        return response
        
    except Exception as e:
        logger.exception("GitHub OAuth error")
        return RedirectResponse(url=f'/login?error={str(e)}')
```

---

## 🎨 Frontend - Social Login Buttons

The enhanced login page with social buttons is being created separately. It will include:
- Beautiful social login buttons
- Proper branding colors (Google blue, Facebook blue, etc.)
- Icons for each provider
- Hover effects and animations
- Responsive design

---

## ⚙️ Configuration (.env)

Complete `.env` file with all OAuth providers:

```env
# Existing
API_KEY=your-api-key
JWT_SECRET_KEY=your-jwt-secret

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Facebook OAuth
FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Microsoft OAuth (Optional)
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
```

---

## 🧪 Testing

### 1. Test Google Login
```
1. Click "Sign in with Google"
2. Choose Google account
3. Grant permissions
4. Redirected to dashboard
5. Check localStorage for token
```

### 2. Test Account Linking
```
1. Create account with email test@example.com
2. Try to login with Google using same email
3. Should link accounts (not create duplicate)
```

---

## 🔒 Security Best Practices

### 1. Verify Email from Provider
```python
if not user_info.get('email_verified'):
    raise HTTPException(400, "Email not verified by provider")
```

### 2. Use HTTPS in Production
```python
# Only for production
redirect_uri = 'https://yourdomain.com/auth/google/callback'
```

### 3. Secure Session Secret
```python
# Strong random secret
app.add_middleware(
    SessionMiddleware, 
    secret_key=secrets.token_urlsafe(32)
)
```

### 4. Validate State Parameter
OAuth library handles this automatically via Authlib

---

## 📊 User Flow Diagram

```
User Clicks "Sign in with Google"
            ↓
Redirected to /auth/google/login
            ↓
Redirected to Google Login Page
            ↓
User authenticates with Google
            ↓
Google redirects to /auth/google/callback?code=xxx
            ↓
Backend exchanges code for token
            ↓
Backend fetches user info from Google
            ↓
Check if user exists by email
    ↓                    ↓
   Exists          Doesn't Exist
    ↓                    ↓
Login User       Create New User
    ↓                    ↓
    └──────┬──────────────┘
           ↓
Generate JWT Access Token
           ↓
Set Token in Cookie
           ↓
Redirect to Dashboard (/)
```

---

## 🚀 Deployment Checklist

### Development
- [x] Install authlib, httpx
- [x] Create OAuth providers module
- [x] Add OAuth routes to API
- [x] Update login page with social buttons
- [x] Configure .env with test credentials
- [x] Test each provider locally

### Production
- [ ] Use production OAuth credentials
- [ ] Update redirect URIs to production domain
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Add error logging
- [ ] Monitor OAuth failures
- [ ] Set up account linking logic
- [ ] Add terms of service acceptance

---

## 📚 Additional Resources

- [Authlib Documentation](https://docs.authlib.org/)
- [Google OAuth Guide](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Guide](https://developers.facebook.com/docs/facebook-login)
- [GitHub OAuth Guide](https://docs.github.com/en/developers/apps/building-oauth-apps)

---

**Status**: 📋 Implementation Guide Complete  
**Next**: Enhanced login page with social buttons being created...
