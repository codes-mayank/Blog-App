from fastapi import APIRouter, Depends, HTTPException, Request, Response
from app.core.config import settings
from app.core.security import get_password_hash, create_access_token, verify_password, create_token_payload, get_current_user
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.schemas import UserIn, UserLogin, UserOut, Token
from app.models import User


router = APIRouter()


@router.post("/signup", response_model=UserOut)
async def signup(response: Response, user: UserIn, db: Session = Depends(get_db)):
    existing_name = db.query(User).filter(User.username == user.username).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(data=create_token_payload(db_user).model_dump())
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME, 
        value=access_token,
        httponly=True
    )
    return db_user

@router.get("/me", response_model=UserOut)
async def read_users_me(token: Token = Depends(get_current_user), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.id == token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
    return {"message": "Logged out successfully"}

@router.post("/login", response_model=UserOut)
async def login(response: Response, user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
                    or_(
                        User.username == user.username_or_email, 
                        User.email == user.username_or_email
                    )
                ).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or email")
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token = create_access_token(data=create_token_payload(db_user).model_dump())
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME, 
        value=access_token,
        httponly=True
    )
    return db_user