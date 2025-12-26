from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from app.core.auth import hash_password, verify_password, generate_api_key, create_access_token, get_current_user
from app.core.database import db
from app.core.plans import get_plan_by_name, get_default_plan
from app.schemas.user_schema import UserRegister, UserLogin, UserResponse, TokenResponse, UserProfile
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    
    # Check if username or email already exists
    existing_user = await db.fetchrow(
        "SELECT id FROM users WHERE username = $1 OR email = $2",
        user_data.username, user_data.email
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Get plan
    plan = await get_plan_by_name(user_data.plan_name)
    if not plan:
        plan = await get_default_plan()
    
    # Hash password and generate API key
    hashed_password = hash_password(user_data.password)
    api_key = generate_api_key()
    
    # Create user
    user_id = await db.fetchval("""
        INSERT INTO users (username, email, hashed_pass, api_key, plan_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """, user_data.username, user_data.email, hashed_password, api_key, plan['id'])
    
    # Get created user with plan info
    user = await db.fetchrow("""
        SELECT u.id, u.username, u.email, u.created_at, p.name as plan_name, p.max_tokens
        FROM users u
        JOIN plans p ON u.plan_id = p.id
        WHERE u.id = $1
    """, user_id)
    
    return UserResponse(**dict(user))


@router.post("/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin):
    """Login user and return JWT token"""
    
    # Get user
    user = await db.fetchrow("""
        SELECT u.*, p.name as plan_name, p.max_tokens
        FROM users u
        JOIN plans p ON u.plan_id = p.id
        WHERE u.username = $1
    """, user_data.username)
    
    if not user or not verify_password(user_data.password, user['hashed_pass']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user['id'])},
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user['id'],
        username=user['username'],
        email=user['email'],
        plan_name=user['plan_name'],
        max_tokens=user['max_tokens'],
        created_at=user['created_at']
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user_response
    )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    
    return UserProfile(
        id=current_user['id'],
        username=current_user['username'],
        email=current_user['email'],
        plan_name=current_user['plan_name'],
        max_tokens=current_user['max_tokens'],
        price=current_user['price'],
        api_key=current_user['api_key'],
        created_at=current_user['created_at'],
        updated_at=current_user['updated_at']
    )


@router.post("/regenerate-api-key")
async def regenerate_api_key(current_user: dict = Depends(get_current_user)):
    """Regenerate user's API key"""
    
    new_api_key = generate_api_key()
    
    await db.execute(
        "UPDATE users SET api_key = $1, updated_at = NOW() WHERE id = $2",
        new_api_key, current_user['id']
    )
    
    return {"message": "API key regenerated successfully", "api_key": new_api_key}