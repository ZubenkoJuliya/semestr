import requests
from bs4 import BeautifulSoup
import random

class BookScraper:
    def scrape_books_from_site(self):
        base_url = "http://books.toscrape.com/catalogue/page-"
        books_data = []

        for page in range(1, 6):
            url = f"{base_url}{page}.html"
            headers = {"User -Agent": "Mozilla/5.0"}

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                return [{"title": "Ошибка запроса", "price": "-", "availability": "-", "rating": str(e)}]

            soup = BeautifulSoup(response.text, "html.parser")
            book_elements = soup.select("article.product_pod")

            for book in book_elements:
                title = book.h3.a["title"]
                price = book.select_one(".price_color").text
                availability = book.select_one(".availability").text.strip()
                rating_class = book.select_one("p.star-rating")["class"]
                rating = next((cls for cls in rating_class if cls != "star-rating"), "No rating")

                books_data.append({
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating
                })

        return books_data

    def get_random_book(self):
        books = self.scrape_books_from_site()
        if books:
            random_book = random.choice(books)
            return f"📚 Случайная книга:\nНазвание: {random_book['title']}\nЦена: {random_book['price']}\nНаличие: {random_book['availability']}\nРейтинг: {random_book['rating']}"
        return "Не удалось получить случайную книгу."
