import logging
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..services.book_service import BookService

class StatsController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service
        self.router = APIRouter(prefix="/api/v1/stats", tags=["statistics"])
        self._setup_routes()
    
    def _setup_routes(self):
        self.router.add_api_route("/overview", self.get_overview_stats, methods=["GET"])
        self.router.add_api_route("/categories", self.get_category_stats, methods=["GET"])
    
    async def get_overview_stats(self) -> Dict[str, Any]:
        try:
            stats = self.book_service.get_overview_stats()
            return stats
        except Exception as e:
            logging.error(f"stats_controller.get_overview_stats error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})
    
    async def get_category_stats(self) -> List[Dict[str, Any]]:
        try:
            stats = self.book_service.get_category_stats()
            return stats
        except Exception as e:
            logging.error(f"stats_controller.get_category_stats error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})