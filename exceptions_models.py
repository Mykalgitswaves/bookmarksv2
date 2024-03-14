class ReorderException(Exception):
    def __str__(self):
        print('Reorder failed, change was not processed.')
        return 'Reorder failed, change was not processed.'
    
class InvalidDataError(Exception):
    def __str__(self):
        print('Cannot reorder. Current, next or previous data was not provided.')
        return 'Cannot reorder. Current, next or previous data was not provided.'
    
class BookAlreadyExists(Exception):
    def __str__(self):
        print('Book already exists.')
        return 'Book already exists.'

class BookNotInShelf(Exception):
    def __str__(self):
        print('One of the books is not in shelf.')
        return 'One of the books is not in shelf.'
    
class MissingDataError(Exception):
    def __str__(self):
        print('Missing data.')
        return 'Missing data.'
    
class EmptyShelfError(Exception):
    def __str__(self):
        print('Shelf is empty.')
        return 'Shelf is empty.'
    
class InvalidAuthorPermission(Exception):
    def __str__(self):
        print('Invalid author permission.')
        return 'Invalid author permission.'