from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.genres import Genre

class GenreCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def get_genre_by_name(self, name:str):
        """
        Checks if a genre exists in the DB by name
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_genre_by_name_query, name)
        return(result)
    
    @staticmethod
    def get_genre_by_name_query(tx,name):
        query = "match (g:Genre {name:$name}) return g.id"
        result = tx.run(query,name=name)
        response = result.single()
        if response:
            return(response['g.id'])
        else:
            return(None)
        
    def search_genres_by_name(self, skip, limit, text):
        """
        Returns a  genre object for a small about of genre using a text search term
        
        Args:
            skip: index to start at
            limit: index to end at
            text: text to search within the title
        Returns:
            Genre: genre objects with name and id
        """
        with self.driver.session() as session:
            genres = session.execute_read(self.search_genres_by_name_query, skip, limit, text)
        return(genres)
    
    @staticmethod
    def search_genres_by_name_query(tx, skip, limit, text):
        text = "(?i)" + "".join([f".*{word.lower()}.*" for word in text.split(" ")])
        query = """
                match (g:Genre) where g.name =~ $text return g.name, g.id
                SKIP $skip
                LIMIT $limit
                """
        result = tx.run(query, skip=skip, limit=limit, text=text)
        genres = [
                Genre(
                    id=response['g.id'],
                    name=response['g.name'],
                )
                for response in result
            ]
        return(genres)
        
    def create_genre(self,name):
        """
        Creates a genre in the DB
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_genre_query, name)
        return(result)
    
    @staticmethod
    def create_genre_query(tx,name):
        query = "create (g:Genre {id:randomUUID(), name:$name}) return g.id"
        result = tx.run(query,name=name)
        response = result.single()
        return(response['g.id'])