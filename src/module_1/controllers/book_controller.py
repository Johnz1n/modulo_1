import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..services.book_service import BookService
from ..models.book import Book

class BookController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service
        self.router = APIRouter(prefix="/api/v1", tags=["books"])
        self._setup_routes()
    
    def _setup_routes(self):
        self.router.add_api_route("/books/search", self.search_books, methods=["GET"], response_model=List[Book])
        self.router.add_api_route("/books/top-rated", self.get_top_rated_books, methods=["GET"], response_model=List[Book])
        self.router.add_api_route("/books/price-range", self.get_books_by_price_range, methods=["GET"], response_model=List[Book])
        self.router.add_api_route("/books/{book_id}", self.get_book_by_id, methods=["GET"], response_model=Book)
        self.router.add_api_route("/books", self.get_books, methods=["GET"], response_model=List[Book])
    
    async def get_books(
        self,
        category: Optional[str] = Query(None, description="Filter by category"),
        in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
        min_price: Optional[float] = Query(None, description="Minimum price filter"),
        max_price: Optional[float] = Query(None, description="Maximum price filter"),
        rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
        limit: Optional[int] = Query(100, ge=1, le=1000, description="Limit results"),
        offset: Optional[int] = Query(0, ge=0, description="Offset for pagination")
    ) -> List[Book]:
        try:
            books = self.book_service.get_all_books(
                category=category,
                in_stock=in_stock,
                min_price=min_price,
                max_price=max_price,
                rating=rating,
                limit=limit,
                offset=offset
            )

            return books
        except Exception as e:
            logging.error(f"book_controller.get_books error: {str(e)}") 
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})
    
    async def get_book_by_id(self, book_id: str) -> Book:
        try:
            book = self.book_service.get_book_by_id(book_id)
            if not book:
                raise HTTPException(status_code=404, detail={"message": "Book not found"})
            return book
        except Exception as e:
            logging.error(f"book_controller.get_book_by_id error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})
    
    async def search_books(
        self,
        title: Optional[str] = Query(None, description="Search by title"),
        category: Optional[str] = Query(None, description="Search by category"),
        limit: Optional[int] = Query(20, ge=1, le=100, description="Limit results")
    ) -> List[Book]:
        if not title and not category:
            raise HTTPException(status_code=400, detail={"message": "At least one search parameter (title or category) is required"})
        
        try:
            books = self.book_service.search_books(title=title, category=category, limit=limit)
            return books
        except Exception as e:
            logging.error(f"book_controller.search_books error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})
    
    async def get_top_rated_books(
        self,
        limit: Optional[int] = Query(10, ge=1, le=50, description="Limit results")
    ) -> List[Book]:
        try:
            books = self.book_service.get_top_rated_books(limit=limit)
            return books
        except Exception as e:
            logging.error(f"book_controller.get_top_rated_books error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})

    async def get_books_by_price_range(
        self,
        min_price: Optional[float] = Query(None, description="Minimum price"),
        max_price: Optional[float] = Query(None, description="Maximum price")
    ) -> List[Book]:
        if min_price is None and max_price is None:
            raise HTTPException(status_code=400, detail={"message": "At least one price parameter (min or max) is required"})
        
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(status_code=400, detail={"message": "Minimum price cannot be greater than maximum price"})
        
        try:
            books = self.book_service.get_books_by_price_range(min_price=min_price, max_price=max_price)
            return books
        except Exception as e:
            logging.error(f"book_controller.get_books_by_price_range error: {str(e)}")
            raise HTTPException(status_code=500, detail={"message": "Internal server error"})