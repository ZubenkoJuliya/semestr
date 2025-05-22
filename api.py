import requests

class GoogleBooksAPI:
    def search_by_title(self, title_word: str):
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title_word}&maxResults=5"
        response = requests.get(url)
        if response.status_code != 200:
            return "Ошибка при запросе к API Google Books."

        data = response.json()
        items = data.get('items', [])
        if not items:
            return "Книги с таким словом в названии не найдены."

        book = items[0]
        info = book.get('volumeInfo', {})
        title = info.get('title', 'Нет названия')
        authors = ', '.join(info.get('authors', ['Неизвестный автор']))
        link = info.get('infoLink', 'Ссылка отсутствует')

        return f"📖 <b>{title}</b>\n👤 {authors}\n🔗 {link}"

class OpenLibraryAPI:
    def search_by_author(self, author: str):
        search_url = f"https://openlibrary.org/search.json?q=author:{author}&limit=1"
        search_response = requests.get(search_url)
        if search_response.status_code != 200:
            return "Ошибка при запросе к OpenLibrary."

        search_data = search_response.json()
        if not search_data.get("docs"):
            return "Не удалось найти книгу. Попробуйте ещё раз."

        book_data = search_data["docs"][0]
        title = book_data.get("title", "Без названия")
        authors = ", ".join(book_data.get("author_name", ["Неизвестен"]))
        year = book_data.get("first_publish_year", "Неизвестен")
        return f"📚 Книга автора '{author}':\nНазвание: {title}\nАвтор: {authors}\nГод: {year}"
