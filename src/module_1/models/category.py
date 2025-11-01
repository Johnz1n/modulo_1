import uuid
from dataclasses import dataclass

@dataclass
class Category:
    """
    Data model for a book category scraped from books.toscrape.com
    """
    id: uuid.UUID
    name: str
    url: str
    slug: str

    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'name': self.name,
            'url': self.url,
            'slug': self.slug
        }