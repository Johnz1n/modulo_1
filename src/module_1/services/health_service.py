import requests
from typing import Dict, Any
from pathlib import Path


class HealthService:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def get_health_status(self) -> Dict[str, Any]:
        books_file = self.data_dir / "books.json"
        categories_file = self.data_dir / "categories.json"
        
        books_exists = books_file.exists()
        categories_exists = categories_file.exists()

        response = requests.get("https://books.toscrape.com/")
        books_to_scrape_status = True if response.status_code == 200 else False
    
        status = "ok" if books_exists and categories_exists and books_to_scrape_status else "not_ok"

        return {
            "status": status,
            "timestamp": "2025-11-01T00:00:00Z",
            "services": {
                "api": "ok",
                "data_files": {
                    "books_json": "ok" if books_exists else "not_ok",
                    "categories_json": "ok" if categories_exists else "not_ok"
                },
                "books_to_scrape": "ok" if books_to_scrape_status else "not_ok"
            },
            "checks": {
                "books_file_exists": books_exists,
                "categories_file_exists": categories_exists,
                "books_to_scrape_responding": books_to_scrape_status
            }
        }