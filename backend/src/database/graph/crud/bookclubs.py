from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas import bookclubs as BookClubSchemas

class BookClubCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def create_bookclub(
            self, 
            book_club: BookClubSchemas.BookClubCreate
        ) -> None:
        """
        Creates a bookclub for the current user. 
        Args:
            bookclub (BookClubSchemas.BookClubCreate): The bookclub to create
        """
        with self.driver.session() as session:
            result = session.write_transaction(self.create_bookclub_query, book_club)
        return result
    
    @staticmethod
    def create_bookclub_query(
        tx, 
        book_club: BookClubSchemas.BookClubCreate
        ) -> None:
        
        query_with_pace = (
            """
            MATCH (u:User {id: $user_id})
            CREATE (b:BookClub {
                id: "book_club_" + randomUUID(),
                created_date: datetime(),
                name: $name,
                description: $description
            })
            CREATE (p:BookClubPace {
                num_books: $num_books,
                num_time_period: $num_time_period,
                time_period: $time_period,
                last_edited_date: datetime()
            })
            CREATE (u)-[:OWNS_BOOK_CLUB]->(b)
            CREATE (b)-[:HAS_PACE]->(p)
            return b.id as book_club_id
            """)
        
        query_without_pace = (
            """
            MATCH (u:User {id: $user_id})
            CREATE (b:BookClub {
                id: "book_club_" + randomUUID(),
                created_date: datetime(),
                name: $name,
                description: $description
            })
            CREATE (u)-[:OWNS_BOOK_CLUB]->(b)
            return b.id as book_club_id
            """)


        if book_club.book_club_pace:
            result = tx.run(
                query_with_pace, 
                user_id=book_club.user_id,
                name=book_club.name,
                description=book_club.description,
                num_books=book_club.book_club_pace.get("num_books", 0),
                num_time_period=book_club.book_club_pace.get("num_time_period", 0),
                time_period=book_club.book_club_pace.get("time_period", "days"))
        else:
            result = tx.run(
                query_without_pace, 
                user_id=book_club.user_id,
                name=book_club.name,
                description=book_club.description)
            
        response = result.single()

        if not response:
            return False
        else:
            return response["book_club_id"]

        