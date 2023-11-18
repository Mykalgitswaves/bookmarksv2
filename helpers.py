import time

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"{func.__name__} took {execution_time:.6f} seconds to execute")
        return result
    return wrapper

def find_book_by_isbn(driver, isbn:str):
    if len(str(isbn)) == 13:
        db_book = driver.find_book_by_isbn13(isbn)
    elif len(str(isbn)) == 10:
        db_book = driver.find_book_by_isbn10(isbn)
    else:
        print(f"UNKNOWN IDENTIFIER {str(isbn)}")
        return(None)

    return(db_book)