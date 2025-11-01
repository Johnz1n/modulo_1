import time
from module_1.services.book_scraper_service import BookScraper

def main():
    start_time = time.time()
    scraper = BookScraper()

    books, categories = scraper.run()

    end_time = time.time()
    # Print some statistics
    if books and categories:
        categories = set(book.category for book in books)
        print(f"Categories found: {len(categories)}")
        
        in_stock_books = sum(1 for book in books if book.in_stock)
        print(f"Books in stock: {in_stock_books}/{len(books)}")
        
        avg_price = sum(book.price for book in books) / len(books)
        print(f"Average price: £{avg_price:.2f}")

        execution_time = end_time - start_time

        print(f"Total execution time: {execution_time:.2f} seconds")


if __name__ == "__main__":
    main()
