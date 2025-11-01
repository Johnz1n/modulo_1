from typing import List, Optional, Dict, Any
from ..repository.book_repository import BookRepositoryInterface
from ..models.book import Book


class BookService:
    def __init__(self, book_repository: BookRepositoryInterface):
        self.book_repository = book_repository
    
    def get_all_books(
        self,
        category: Optional[str] = None,
        in_stock: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        rating: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Book]:
        books = self.book_repository.get_all_books()
        
        filtered_books = self._apply_filters(
            books, category, in_stock, min_price, max_price, rating
        )
        
        return self._apply_pagination(filtered_books, limit, offset)

    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        return self.book_repository.get_book_by_id(book_id)
    
    def search_books(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Book]:
        books = self.book_repository.search_books(title, category)
        
        if limit:
            return books[:limit]
        
        return books
    
    def get_books_by_price_range(
        self,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Book]:
        books = self.book_repository.get_all_books()
        
        filtered_books = books
        
        if min_price is not None:
            filtered_books = [
                book for book in filtered_books
                if float(book.price) >= min_price
            ]
        
        if max_price is not None:
            filtered_books = [
                book for book in filtered_books
                if float(book.price) <= max_price
            ]
        
        return filtered_books
    
    def get_top_rated_books(self, limit: Optional[int] = 10) -> List[Book]:
        books = self.book_repository.get_all_books()
        
        sorted_books = sorted(
            books,
            key=lambda x: x.rating,
            reverse=True
        )
        
        if limit:
            return sorted_books[:limit]
        
        return sorted_books
    
    def get_overview_stats(self) -> Dict[str, Any]:
        books = self.book_repository.get_all_books()
        
        total_books = len(books)
        in_stock_books = sum(1 for book in books if book.in_stock)

        prices = [float(book.price) for book in books if book.price]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        
        ratings = [book.rating for book in books if book.rating]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        rating_distribution = {}
        for rating in range(1, 6):
            rating_distribution[f"{rating}_star"] = sum(1 for r in ratings if r == rating)

        categories = list(set(book.category for book in books if book.category))

        return {
            "total_books": total_books,
            "books_in_stock": in_stock_books,
            "books_out_of_stock": total_books - in_stock_books,
            "total_categories": len(categories),
            "price_stats": {
                "average": round(avg_price, 2),
                "minimum": min_price,
                "maximum": max_price
            },
            "average_rating": round(avg_rating, 2) if avg_rating else None,
            "rating_distribution": rating_distribution
        }
    
    def get_category_stats(self) -> List[Dict[str, Any]]:
        books = self.book_repository.get_all_books()
        
        category_stats = {}
        
        for book in books:
            category = book.category if book.category else 'Unknown'
            if category not in category_stats:
                category_stats[category] = {
                    "category": category,
                    "total_books": 0,
                    "books_in_stock": 0,
                    "prices": [],
                    "ratings": []
                }
            
            category_stats[category]["total_books"] += 1
            
            if book.in_stock:
                category_stats[category]["books_in_stock"] += 1
            
            if book.price:
                category_stats[category]["prices"].append(float(book.price))
            
            if book.rating:
                category_stats[category]["ratings"].append(book.rating)
        
        result = []
        for category, stats in category_stats.items():
            prices = stats["prices"]
            ratings = stats["ratings"]
            
            result.append({
                "category": category,
                "total_books": stats["total_books"],
                "books_in_stock": stats["books_in_stock"],
                "books_out_of_stock": stats["total_books"] - stats["books_in_stock"],
                "price_stats": {
                    "average": round(sum(prices) / len(prices), 2) if prices else 0,
                    "minimum": min(prices) if prices else 0,
                    "maximum": max(prices) if prices else 0,
                    "count": len(prices)
                },
                "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "rating_count": len(ratings)
            })
        
        return sorted(result, key=lambda x: x["total_books"], reverse=True)
    
    def _apply_filters(
        self,
        books: List[Book],
        category: Optional[str] = None,
        in_stock: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        rating: Optional[int] = None
    ) -> List[dict]:
        filtered_books = books
        
        if category:
            filtered_books = [
                book for book in filtered_books
                if book.category.lower() == category.lower()
            ]
        
        if in_stock is not None:
            filtered_books = [
                book for book in filtered_books
                if book.in_stock == in_stock
            ]
        
        if min_price is not None:
            filtered_books = [
                book for book in filtered_books
                if float(book.price) >= min_price
            ]
        
        if max_price is not None:
            filtered_books = [
                book for book in filtered_books
                if float(book.price) <= max_price
            ]
        
        if rating is not None:
            filtered_books = [
                book for book in filtered_books
                if book.rating == rating
            ]
        
        return filtered_books
    
    def _apply_pagination(
        self,
        books: List[Book],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Book]:
        if offset is None:
            offset = 0
        
        if limit is None:
            return books[offset:]
        
        start = offset
        end = offset + limit
        return books[start:end]