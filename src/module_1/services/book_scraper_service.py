import uuid
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
import re
import json
from pathlib import Path
import pandas as pd
from urllib.parse import urljoin

from src.module_1.models.book import Book
from src.module_1.models.category import Category

class BookScraper:
    def __init__(self, base_url: str = "https://books.toscrape.com/"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.path = Path("data")
        
    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_categories(self) -> List[Category]:
        soup = self._get_soup(self.base_url)
        if not soup:
            return []
        
        categories = []
        
        category_nav = soup.find('div', class_='side_categories')
        if not category_nav:
            print("Could not find category navigation")
            return []
        
        category_links = category_nav.find_all('a')[1:]
        
        for link in category_links:
            category_name = link.get_text().strip()
            category_url = urljoin(self.base_url, link.get('href', ''))
            slug = category_url.split('/')[-2]
            
            categories.append(Category(
                id=uuid.uuid4(),
                name=category_name,
                url=category_url,
                slug=slug
            ))

        print(f"Found {len(categories)} categories")
        return categories
    
    def get_books_from_category(self, category_url: str, category_name: str) -> List[str]:
        book_urls = []
        page_num = 1
        
        while True:
            if page_num == 1:
                page_url = category_url
            else:
                base_category_url = category_url.replace('index.html', '')
                page_url = f"{base_category_url}page-{page_num}.html"
            
            print(f"Scraping {category_name} - Page {page_num}")
            soup = self._get_soup(page_url)
            
            if not soup:
                break
            
            books_section = soup.find('section')
            if not books_section:
                break
                
            book_containers = books_section.find_all('article', class_='product_pod')
            
            if not book_containers:
                break
            
            # Extract book URLs from this page
            page_book_urls = []
            for container in book_containers:
                book_link = container.find('h3').find('a')
                if book_link:
                    book_url = book_link.get('href', '')
                    book_url = book_url.replace('../', '')
                    book_url = urljoin(self.base_url + '/catalogue/', book_url)
                    page_book_urls.append(book_url)
            
            book_urls.extend(page_book_urls)
            print(f"Found {len(page_book_urls)} books on page {page_num}")
            
            next_button = soup.find('li', class_='next')
            if not next_button:
                break
                
            page_num += 1
        
        print(f"Total books found in {category_name}: {len(book_urls)}")
        return book_urls
    
    def _parse_rating(self, soup: BeautifulSoup) -> Optional[int]:
        rating_element = soup.find('p', class_=re.compile(r'star-rating'))
        if rating_element:
            rating_classes = rating_element.get('class', [])
            for cls in rating_classes:
                if cls in ['One', 'Two', 'Three', 'Four', 'Five']:
                    return {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}[cls]
        return None
    
    def _parse_price(self, price_text: str) -> Decimal:
        price_match = re.search(r'[\d.]+', price_text)
        if price_match:
            return Decimal(price_match.group())
        return Decimal('0')
    
    def _parse_stock_info(self, availability_text: str) -> Tuple[bool, Optional[int]]:
        in_stock = 'in stock' in availability_text.lower()
        
        # Extract quantity if available
        quantity_match = re.search(r'\((\d+) available\)', availability_text)
        quantity = int(quantity_match.group(1)) if quantity_match else None
        
        return in_stock, quantity
    
    def scrape_book_details(self, book_url: str, category: str) -> Optional[Book]:
        soup = self._get_soup(book_url)
        if not soup:
            return None
        
        try:
            title = soup.find('h1').get_text().strip()
            
            image_container = soup.find('div', class_='item active')
            image_url = ""
            if image_container:
                img_tag = image_container.find('img')
                if img_tag:
                    image_url = urljoin(self.base_url, img_tag.get('src', ''))
            
            price_element = soup.find('p', class_='price_color')
            price = self._parse_price(price_element.get_text()) if price_element else Decimal('0')
            
            availability_element = soup.find('p', class_='instock availability')
            availability_text = availability_element.get_text().strip() if availability_element else ""
            in_stock, stock_quantity = self._parse_stock_info(availability_text)
            
            rating = self._parse_rating(soup)
            
            description = None
            description_section = soup.find('div', id='product_description')
            if description_section:
                description_p = description_section.find_next_sibling('p')
                if description_p:
                    description = description_p.get_text().strip()
            
            # Product information table
            product_info = {}
            product_table = soup.find('table', class_='table-striped')
            if product_table:
                rows = product_table.find_all('tr')
                for row in rows:
                    keys = row.find_all('th')
                    cells = row.find_all('td')
                    if len(cells) > 0 and len(keys) > 0:
                        key = keys[0].get_text().strip()
                        value = cells[0].get_text().strip()
                        product_info[key] = value
            
            # Extract specific product information
            upc = product_info.get('UPC')
            product_type = product_info.get('Product Type')
            price_excl_tax = self._parse_price(product_info.get('Price (excl. tax)', '0'))
            price_incl_tax = self._parse_price(product_info.get('Price (incl. tax)', '0'))
            tax = self._parse_price(product_info.get('Tax', '0'))
            
            # Number of reviews
            number_of_reviews = None
            reviews_text = product_info.get('Number of reviews', '0')
            if reviews_text.isdigit():
                number_of_reviews = int(reviews_text)
            
            book = Book(
                id=uuid.uuid4(),
                title=title,
                url=book_url,
                image_url=image_url,
                category=category,
                price=price,
                in_stock=in_stock,
                stock_quantity=stock_quantity,
                rating=rating,
                description=description,
                upc=upc,
                product_type=product_type,
                price_excl_tax=price_excl_tax if price_excl_tax > 0 else None,
                price_incl_tax=price_incl_tax if price_incl_tax > 0 else None,
                tax=tax if tax > 0 else None,
                number_of_reviews=number_of_reviews
            )
            
            return book
            
        except Exception as e:
            print(f"Error scraping book {book_url}: {e}")
            return None

    def scrape_all_books(self, max_books_per_category: Optional[int] = None) -> Tuple[List[Book], List[Category]]:
        all_books = []
        categories = self.get_categories()
        
        for i, category in enumerate(categories, 1):
            print(f"\n=== Processing category: {category.name} {i}/{len(categories)} ===")

            book_urls = self.get_books_from_category(category.url, category.name)
            
            if max_books_per_category:
                book_urls = book_urls[:max_books_per_category]
            
            for i, book_url in enumerate(book_urls, 1):
                print(f"Scraping book {i}/{len(book_urls)} in {category.name}")
                
                book = self.scrape_book_details(book_url, category.name)
                if book:
                    all_books.append(book)
                else:
                    print(f"Failed to scrape: {book_url}")

        return all_books, categories

    def save_categories_to_json(self, categories: List[Category], filename: str):
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        categories_data = [category.to_dict() for category in categories]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(categories_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(categories)} categories to {filename}")

    def save_to_json(self, books: List[Book], filename: str):
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        books_data = [book.to_dict() for book in books]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(books)} books to {filename}")
    
    def save_to_csv(self, books: List[Book], filename: str):
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        books_data = [book.to_dict() for book in books]
        df = pd.DataFrame(books_data)
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Saved {len(books)} books to {filename}")

    def run(self) -> Tuple[List[Book], List[Category]]:
        print("Starting comprehensive scrape of books.toscrape.com")
        print("This will scrape ALL books from ALL categories...")

        books, categories = self.scrape_all_books()

        print(f"\n=== Scraping completed! ===")
        print(f"Total books scraped: {len(books)}")
        

        self.save_categories_to_json(categories, self.path / "categories.json")
        self.save_to_json(books, self.path / "books.json")
        self.save_to_csv(books, self.path / "books.csv")

        return books, categories