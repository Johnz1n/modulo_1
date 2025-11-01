import logging
from fastapi import APIRouter, HTTPException
from typing import List

from ..services.category_service import CategoryService
from ..models.category import Category

class CategoryController:
    def __init__(self, category_service: CategoryService):
        self.category_service = category_service
        self.router = APIRouter(prefix="/api/v1", tags=["categories"])
        self._setup_routes()
    
    def _setup_routes(self):
        self.router.add_api_route("/categories", self.get_categories, methods=["GET"], response_model=List[Category])
    
    async def get_categories(self) -> List[Category]:
        try:
            categories = self.category_service.get_all_categories()
            return categories
        except Exception as e:
            logging.error(f"category_controller.get_categories error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})