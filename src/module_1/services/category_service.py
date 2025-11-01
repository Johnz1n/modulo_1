from typing import List

from ..models.category import Category
from ..repository.category_repository import CategoryRepositoryInterface


class CategoryService:
    def __init__(self, category_repository: CategoryRepositoryInterface):
        self.category_repository = category_repository
    
    def get_all_categories(self) -> List[Category]:
        return self.category_repository.get_all_categories()