BOOKCLUBS_INDEX = (
"""
Create FULLTEXT INDEX bookclubsFullText
for (n:BookClub)
on each [n.title, n.description]    
"""
)