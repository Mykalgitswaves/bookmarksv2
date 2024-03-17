from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.authors import Author
from src.models.schemas.books import Book

class AuthorCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def get_author_by_id(self, author_id):
        """
        Pulls all data about an author INCLUDING book info for cards, author info, and friends/influences
        Args:
            author_id
        Returns: Author object, Books corresponding to author
        """
        with self.driver.session() as session:
            author = session.execute_read(self.get_author_by_id_query, author_id)
        return(author)
     
    @staticmethod
    def get_author_by_id_query(tx, author_id):
        query = """
                match (a:Author {id: $author_id})
                match (a)-[w:WROTE]->(b:Book)
                return a.id, a.name, b.id, b.description, b.title, b.publication_year, b.author_names, b.img_url
                """
        result = tx.run(query, author_id=author_id)
        result_list = list(result)

        authors_books = [
            Book(
                author_names=response["b.author_names"],
                id=response["b.id"],
                title=response["b.title"],
                description=response["b.description"],
                publication_year=response["b.publication_year"],
                img_url=response["b.img_url"],
            )
        for response in result_list]

        
        author = Author(
                id=result_list[0]["a.id"],
                name=result_list[0]["a.name"],
                books=authors_books,
            )
        
        return(author)
    
    def get_author_by_name(self,name):
        """
        Checks if an author exists in the DB by name
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_author_by_name_query, name)
        return(result)
    @staticmethod
    def get_author_by_name_query(tx,name):
        query = "match (a:Author {name:$name}) return a.id"
        result = tx.run(query,name=name)
        response = result.single()
        if response:
            return(response['a.id'])
        else:
            return(None)
        
    def search_authors_by_name(self, skip, limit, text):
        """
        Returns a  author object for a small about of author using a text search term
        
        Args:
            skip: index to start at
            limit: index to end at
            text: text to search within the title
        Returns:
            Author: author object with name and id
        """
        with self.driver.session() as session:
            authors = session.execute_write(self.search_authors_by_name_query, skip, limit, text)
        return(authors)
    @staticmethod
    def search_authors_by_name_query(tx, skip, limit, text):
        text = "(?i)" + "".join([f".*{word.lower()}.*" for word in text.split(" ")])
        query = """
                match (a:Author) where a.name =~ $text return a.name, a.id
                SKIP $skip
                LIMIT $limit
                """
        result = tx.run(query, skip=skip, limit=limit, text=text)
        authors = [
                Author(
                    id=response['a.id'],
                    name=response['a.name'],
                )
                for response in result
            ]
        return(authors)
        
    def create_author(self, name, books=[]):
        """
        Creates an author node in the DB

        Args:
            name: Full name of the author
            books:PKs of all book written by the author
        Returns:
            Author: Author object with all related metadata
        """
        with self.driver.session() as session:
            author = session.execute_write(self.create_author_query, name, books)
        return(author)
    @staticmethod
    def create_author_query(tx, name, books):
        # Creates the author node
        query = """
                create (a:Author {id:randomUUID(), name:$name})
                return a.id
                """
        result = tx.run(query, 
                        name=name)
        response = result.single()
        author_id = response["a.id"]

        # Creates the author-book relationships
        query = """
                match (a:Author {id:$author_id})
                match (b:Book {id:$book_id})
                merge (a)-[w:WROTE]->(b)
                """
        for book in books:
            result = tx.run(query, author_id=author_id, book_id=book)
        author = Author(id=author_id, name=name, books=books)
        return(author)