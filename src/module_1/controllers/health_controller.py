import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..services.health_service import HealthService

class HealthController:
    def __init__(self, health_service: HealthService):
        self.health_service = health_service
        self.router = APIRouter(prefix="/api/v1", tags=["health"])
        self._setup_routes()
    
    def _setup_routes(self):
        self.router.add_api_route("/health", self.get_health, methods=["GET"])
    
    async def get_health(self) -> Dict[str, Any]:
        try:
            health_status = self.health_service.get_health_status()
            return health_status
        except Exception as e:
            logging.error(f"health_controller.get_health error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})