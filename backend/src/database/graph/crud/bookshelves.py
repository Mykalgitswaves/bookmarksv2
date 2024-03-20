from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.bookshelves import Bookshelf

class BookshelfCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def get_bookshelf(self, bookshelf_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.get_bookshelf_query, bookshelf_id)
        return result
    
    @staticmethod
    def get_bookshelf_query(tx, bookshelf_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})
            MATCH (u:User)-[r:HAS_BOOKSHELF_ACCESS]->(b)
            RETURN b.id as id, 
                   b.title as title, 
                   b.description as description, 
                   b.books as books,
                   b.visibility as visibility,
                   b.img_url as img_url
                   u as user,
                   r as access
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id)
        contributors = set()
        members = set()
        for record in result:
            if record["access"]["type"] == "owner":
                owner = record["user"]["id"]
                contributors.add(owner)
            elif record["access"]["type"] == "contributor":
                contributors.add(record["user"]["id"])
            elif record["access"]["type"] == "member":
                members.add(record["user"]["id"])
        
        bookshelf = Bookshelf(
            id=record["id"],
            title=record["title"],
            description=record["description"],
            books=record["books"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=owner,
            contributors=contributors,
            members=members
        )

        return bookshelf

    def create_bookshelf(self, bookshelf):
        with self.driver.session() as session:
            result = session.write_transaction(self.create_bookshelf_query, bookshelf)
        return result
    
    @staticmethod
    def create_bookshelf_query(tx, bookshelf):
        query = (
            """
            Match (u:User {id: $created_by})
            CREATE (b:Bookshelf {title: $title, 
                                 description: $description, 
                                 created_by: $created_by,
                                 last_edited_date: datetime(),
                                 created_date: datetime(),
                                 visibility: $visibility,
                                 id: randomUUID(),
                                 books: []})
            MERGE (u)-[:HAS_BOOKSHELF_ACCESS {type:"owner", create_date: datetime()}]->(b)
            RETURN b.id as id
            """
        )
        result = tx.run(query, title=bookshelf.title, 
                        description=bookshelf.description, 
                        created_by=bookshelf.created_by,
                        visibility=bookshelf.visibility)
        return result.single()["id"]
    
    def update_books_in_bookshelf(self, books, bookshelf_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_books_in_bookshelf_query, books, bookshelf_id)
        return result
    
    @staticmethod
    def update_books_in_bookshelf_query(tx, books, bookshelf_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})
            SET b.books = $books
            """
        )
        result = tx.run(query, books=books, bookshelf_id=bookshelf_id)
        return result.single()
