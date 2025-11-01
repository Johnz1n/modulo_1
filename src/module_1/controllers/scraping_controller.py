import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any

from ..middleware.auth_middleware import AuthMiddleware
from ..services.scraping_service import ScrapingService

security = HTTPBearer()


class ScrapingController:

    def __init__(self, scraping_service: ScrapingService, auth_middleware: AuthMiddleware):
        self.scraping_service = scraping_service
        self.auth_middleware = auth_middleware
        self.router = APIRouter(prefix="/api/v1/scraping", tags=["scraping"])
        self._setup_routes()
    
    def _setup_routes(self):
        @self.router.post(
            "/trigger",
            summary="Trigger scraping process",
            description="Triggers the book scraping process if it hasn't been executed in the last hour. Requires authentication.",
            dependencies=[Depends(security)]
        )
        async def trigger_scraping_endpoint(user_payload: Dict[str, Any] = Depends(self.auth_middleware.verify_token)):
            return await self.trigger_scraping(user_payload)

    async def trigger_scraping(self, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            username = user_payload.get("sub", "unknown")
            result = await self.scraping_service.trigger_scraping_if_allowed(username)

            return result   
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"scraping_controller.trigger_scraping error: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={"message": "Internal server error during scraping"}
            )
