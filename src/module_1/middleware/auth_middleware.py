import logging
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ..services.auth_service import AuthService

security = HTTPBearer()

class AuthMiddleware:
    """
    Middleware reutilizável para autenticação JWT
    """
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        try:
            if not credentials or not credentials.credentials:
                raise HTTPException(
                    status_code=401, 
                    detail={"message": "Authorization header missing"}
                )
            
            token = credentials.credentials
            payload = self.auth_service.verify_token(token, token_type="access")
            
            return payload
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"auth_middleware.verify_token error: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail={"message": "Invalid authentication token"}
            )
    
    def get_current_user_payload(self) -> callable:
        return self.verify_token