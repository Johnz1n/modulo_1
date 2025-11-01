import uuid
from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class Book:
    """
    Data model for a book scraped from books.toscrape.com
    """
    id: uuid.UUID
    title: str
    url: str
    image_url: str
    category: str

    price: Decimal
    in_stock: bool
    stock_quantity: Optional[int] = None

    rating: Optional[int] = None
    
    description: Optional[str] = None
    
    upc: Optional[str] = None
    product_type: Optional[str] = None
    price_excl_tax: Optional[Decimal] = None
    price_incl_tax: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    number_of_reviews: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        if isinstance(data.get('id'), str):
            data['id'] = uuid.UUID(data['id'])
        
        decimal_fields = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for field in decimal_fields:
            if field in data and data[field] is not None:
                if isinstance(data[field], str):
                    data[field] = Decimal(data[field])
        
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': str(self.id),
            'title': self.title,
            'url': self.url,
            'image_url': self.image_url,
            'category': self.category,
            'price': str(self.price),
            'in_stock': self.in_stock,
            'stock_quantity': self.stock_quantity,
            'rating': self.rating,
            'description': self.description,
            'upc': self.upc,
            'product_type': self.product_type,
            'price_excl_tax': str(self.price_excl_tax) if self.price_excl_tax else None,
            'price_incl_tax': str(self.price_incl_tax) if self.price_incl_tax else None,
            'tax': str(self.tax) if self.tax else None,
            'number_of_reviews': self.number_of_reviews
        }