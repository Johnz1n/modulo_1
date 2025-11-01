import os
import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException

from ..repository.user_repository import UserRepository
from ..models.user import User


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def _create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_user_by_username(username)
        if not user:
            return None
        
        if not self._verify_password(password, user.password):
            return None
        
        if not user.is_active:
            return None
        
        return user

    def login(self, username: str, password: str) -> Dict[str, Any]:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail={"message": "Invalid credentials"})
        
        access_token = self._create_access_token(data={"sub": user.username, "user_id": str(user.id)})
        refresh_token = self._create_refresh_token(data={"sub": user.username, "user_id": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": user.to_public_dict()
        }

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail={"message": "Token expired"})
        except Exception as e:
            logging.error(f"auth_service.verify_token error: {str(e)}")
            raise HTTPException(status_code=401, detail={"message": "Invalid token"})

        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail={"message": "Invalid token type"})
        
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail={"message": "Invalid token"})
        
        return payload


    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        payload = self.verify_token(refresh_token, token_type="refresh")
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        user = self.user_repository.get_user_by_username(username)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail={"message": "User not found or inactive"})
        
        new_access_token = self._create_access_token(data={"sub": username, "user_id": user_id})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }