from src.database.graph.crud.books import BookCRUDRepositoryGraph

def find_book_by_isbn(isbn:str, book_repo: BookCRUDRepositoryGraph):
    if len(str(isbn)) == 13:
        db_book = book_repo.get_book_by_isbn13(isbn)
    elif len(str(isbn)) == 10:
        db_book = book_repo.get_book_by_isbn10(isbn)
    else:
        # print(f"UNKNOWN IDENTIFIER {str(isbn)}")
        return(None)

    return(db_book)