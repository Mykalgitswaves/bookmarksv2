BOOKCLUBS_INDEX = (
"""
Create FULLTEXT INDEX bookclubsFullText
for (n:BookClub)
on each [n.name, n.description]    
"""
)

BOOKSHELVES_INDEX = (
"""
Create FULLTEXT INDEX bookshelvesFullText
for (n:Bookshelf)
on each [n.title, n.description]    
"""
)