import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.auth_service import AuthService

class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
        self._setup_routes()
    
    def _setup_routes(self):
        self.router.add_api_route("/login", self.login, methods=["POST"])
        self.router.add_api_route("/refresh", self.refresh_token, methods=["POST"])
    
    async def login(self, login_request: LoginRequest):
        try:
            result = self.auth_service.login(
                username=login_request.username,
                password=login_request.password
            )
            return result
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"auth_controller.login error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})
    
    async def refresh_token(self, refresh_request: RefreshTokenRequest):
        try:
            result = self.auth_service.refresh_token(refresh_request.refresh_token)
            return result
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"auth_controller.refresh_token error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})