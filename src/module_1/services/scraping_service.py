import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Tuple
from fastapi import HTTPException

from ..repository.book_repository import BookRepository
from ..services.book_scraper_service import BookScraper


class ScrapingService:
    def __init__(self, book_repository: BookRepository, data_dir: Path):
        self.book_repository = book_repository
        self.data_dir = data_dir
        self.books_json_path = data_dir / "books.json"
    
    def check_recent_scraping_execution(self) -> Tuple[bool, datetime]:
        if not self.books_json_path.exists():
            return False, None
        
        modification_time = datetime.fromtimestamp(self.books_json_path.stat().st_mtime)
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
    
        was_recent = modification_time > one_hour_ago
        
        return was_recent, modification_time
    
    async def execute_scraping(self) -> Dict[str, Any]:
        try:
            logging.info("Starting scraping process...")
            
            loop = asyncio.get_event_loop()
            
            def run_scraper():
                scraper = BookScraper()
                books, categories = scraper.run()
                return {
                    "total_books": len(books) if books else 0,
                    "total_categories": len(categories) if categories else 0,
                    "execution_time": datetime.now().isoformat()
                }
            
            result = await loop.run_in_executor(None, run_scraper)
            
            logging.info(f"Scraping completed successfully: {result}")
            return result
        except Exception as e:
            logging.error(f"scraping_service.execute_scraping error: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail={"message": f"Error during scraping execution: {str(e)}"}
            )
    
    async def trigger_scraping_if_allowed(self, username: str) -> Dict[str, Any]:
        was_recent, last_execution = self.check_recent_scraping_execution()
        
        if was_recent:
            raise HTTPException(
                status_code=429, 
                detail={
                    "message": "Scraping was already executed recently",
                    "last_execution": last_execution.isoformat(),
                    "retry_after": "1 hour from last execution",
                    "next_allowed_execution": (last_execution + timedelta(hours=1)).isoformat()
                }
            )
        
        logging.info(f"Scraping triggered by user: {username}")
        scraping_result = await self.execute_scraping()
        
        return {
            "message": "Scraping completed successfully",
            "triggered_by": username,
            "timestamp": datetime.now().isoformat(),
            "results": scraping_result
        }