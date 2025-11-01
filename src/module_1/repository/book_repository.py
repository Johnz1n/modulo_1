from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import json
import pandas as pd

from ..models.book import Book


class BookRepositoryInterface(ABC):
    @abstractmethod
    def get_all_books(self) -> List[Book]:
        pass
    
    @abstractmethod
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        pass
    
    @abstractmethod
    def search_books(self, title: Optional[str] = None, category: Optional[str] = None) -> List[Book]:
        pass


class BookRepository(BookRepositoryInterface):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.books_file = data_dir / "books.json"
    
    def _load_books_data(self) -> List[Book]:
        if not self.books_file.exists():
            return []
        
        with open(self.books_file, 'r', encoding='utf-8') as f:
            books_data = json.load(f)

        return [Book.from_dict(book) for book in books_data]
    
    def get_all_books(self) -> List[Book]:
        return self._load_books_data()
    
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        books = self._load_books_data()
        for book in books:
            if str(book.id) == str(book_id):
                return book
        return None

    def search_books(self, title: Optional[str] = None, category: Optional[str] = None) -> List[Book]:
        books = self._load_books_data()
        filtered_books = books
        
        if title:
            title_lower = title.lower()
            filtered_books = [
                book for book in filtered_books
                if title_lower in book.title.lower()
            ]
        
        if category:
            category_lower = category.lower()
            filtered_books = [
                book for book in filtered_books
                if category_lower in book.category.lower()
            ]
        
        return filtered_books