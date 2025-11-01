from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
import json
from ..models.category import Category


class CategoryRepositoryInterface(ABC):
    @abstractmethod
    def get_all_categories(self) -> List[Category]:
        pass


class CategoryRepository(CategoryRepositoryInterface):
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.categories_file = data_dir / "categories.json"

    def _load_categories_data(self) -> List[Category]:
        if not self.categories_file.exists():
            return []

        with open(self.categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)

        return [Category(**category) for category in categories_data]

    def get_all_categories(self) -> List[Category]:
        return self._load_categories_data()