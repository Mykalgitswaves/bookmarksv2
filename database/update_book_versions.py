import neo4j
from db_helpers import Neo4jDriver
from api.books_api import book_versions
from api.books_api.add_book import pull_google_book_or_add_isbn

def main():
    driver = Neo4jDriver()
    books = driver.get_all_books()
    
    for book in books:
        if not driver.check_if_version_or_canon(book["id"]):
            print(book['id'])
            continue
        print(book['id'])
        if book["isbn13"]:
            response = book_versions.pull_versions(book["isbn13"])
        elif book["isbn10"]:
            response = book_versions.pull_versions(book["isbn10"])
        else:
            continue

        response = response.json()
        if response['numFound'] != 0:
            versions = response['docs'][0]['isbn']
            for version in versions:
                version_book = pull_google_book_or_add_isbn(str(version), driver)
                if version_book:
                    if version_book.id != book['id'] and driver.check_if_version_or_canon(version_book.id):
                        version_book.add_canon_version(book["id"], driver)

            

if __name__ == "__main__":
    main()