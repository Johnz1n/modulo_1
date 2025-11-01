from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv

from ..repository.book_repository import BookRepository
from ..repository.category_repository import CategoryRepository
from ..repository.user_repository import UserRepository
from ..services.book_service import BookService
from ..services.category_service import CategoryService
from ..services.health_service import HealthService
from ..services.auth_service import AuthService
from ..controllers.book_controller import BookController
from ..controllers.category_controller import CategoryController
from ..controllers.stats_controller import StatsController
from ..controllers.health_controller import HealthController
from ..controllers.auth_controller import AuthController
from ..controllers.scraping_controller import ScrapingController
from ..middleware.auth_middleware import AuthMiddleware
from ..services.scraping_service import ScrapingService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Books Scraper API",
    description="API para acessar dados de livros extraídos do books.toscrape.com",
    version="1.0.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

DATA_DIR = Path("/app/data")

book_repository = BookRepository(DATA_DIR)
category_repository = CategoryRepository(DATA_DIR)
user_repository = UserRepository(DATA_DIR)

book_service = BookService(book_repository)
category_service = CategoryService(category_repository)
health_service = HealthService(DATA_DIR)
auth_service = AuthService(user_repository)
scraping_service = ScrapingService(book_repository, DATA_DIR)
auth_middleware = AuthMiddleware(auth_service)

book_controller = BookController(book_service)
category_controller = CategoryController(category_service)
stats_controller = StatsController(book_service)
health_controller = HealthController(health_service)
auth_controller = AuthController(auth_service)
scraping_controller = ScrapingController(scraping_service, auth_middleware)

app.include_router(book_controller.router)
app.include_router(category_controller.router)
app.include_router(stats_controller.router)
app.include_router(health_controller.router)
app.include_router(auth_controller.router)
app.include_router(scraping_controller.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)