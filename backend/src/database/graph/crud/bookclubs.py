from datetime import datetime
from neo4j.time import DateTime as Neo4jDateTime
from typing import List

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

    def create_bookclub_invites(
            self,
            invite: BookClubSchemas.BookClubInvite
        ) -> None:
        """
        Creates invites for the bookclub

        Args:
            invite (BookClubSchemas.BookClubInvite): The invite to create
        """
        with self.driver.session() as session:
            result = session.write_transaction(self.create_bookclub_invites_query, invite)
        return result
    
    @staticmethod
    def create_bookclub_invites_query(
        tx, 
        invite: BookClubSchemas.BookClubInvite
        ) -> None:
        
        query = (
            """
            MATCH (b:BookClub {id: $book_club_id})<-[r:OWNS_BOOK_CLUB]-(u:User {id: $user_id})
            UNWIND $user_ids as user_id
            MATCH (invited_user:User {id: user_id})
            MERGE (invited_user)-[:RECEIVED_INVITE]->(user_invite:BookClubInvite)-[:INVITE_FOR]->(b)
            ON CREATE SET user_invite.id = "club_invite_" + randomUUID(),
                          user_invite.created_date = datetime()
            MERGE (u)-[:SENT_INVITE]->(user_invite)

            WITH b, u
            UNWIND $emails as email
            OPTIONAL MATCH (existing_user:User {email: email})

            FOREACH (_ IN CASE WHEN existing_user IS NULL THEN [1] ELSE [] END |
                MERGE (invited_user:InvitedUser {email: email})
                ON CREATE SET invited_user.id = "invited_user_" + randomUUID(),
                            invited_user.created_date = datetime()
                MERGE (invited_user)-[:RECEIVED_INVITE]->(user_invite_email:BookClubInvite)-[:INVITE_FOR]->(b)
                ON CREATE SET user_invite_email.id = "club_invite_" + randomUUID(),
                              user_invite_email.created_date = datetime()
                MERGE (u)-[:SENT_INVITE]->(user_invite_email)
            )

            FOREACH (_ IN CASE WHEN existing_user IS NOT NULL THEN [1] ELSE [] END |
                MERGE (existing_user)-[:RECEIVED_INVITE]->(user_invite_email:BookClubInvite)-[:INVITE_FOR]->(b)
                ON CREATE SET user_invite_email.id = "club_invite_" + randomUUID(),
                              user_invite_email.created_date = datetime()
                MERGE (u)-[:SENT_INVITE]->(user_invite_email)
            )

            RETURN b.id as book_club_id
            """)

        result = tx.run(
            query,
            book_club_id=invite.book_club_id,
            user_ids=invite.user_ids,
            emails=invite.emails,
            user_id=invite.user_id
        )
        
        response = result.single()
        if response:
            return response["book_club_id"]
        else:
            return False
        
    def get_owned_book_clubs(
            self,
            book_club_param: BookClubSchemas.BookClubList
    ) -> List[BookClubSchemas.BookClubPreview]:
        """
        Get the book clubs owned by the user

        Args:
            book_club_param (BookClubSchemas.BookClubList): The search 
            parameters
        
        Returns:
            book_clubs: an array of book clubs owned by the user. Book club 
            information contains:
                book_club_id(str): Id of the book club
                book_club_name(str): Name of the book club
                pace(int): Pace of the book club
                currently_reading_book(list): List of books currently being 
                read
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_owned_book_clubs_query, 
                book_club_param)
        return result
    
    @staticmethod
    def get_owned_book_clubs_query(
        tx,
        book_club_param: BookClubSchemas.BookClubList
        ) -> List[BookClubSchemas.BookClubPreview]:
        
        query = (
            """
            MATCH (u:User {id: $user_id})-[:OWNS_BOOK_CLUB]->(b:BookClub)
            OPTIONAL MATCH (b)-[reading:IS_READING]-(book:BookClubBook)
            OPTIONAL MATCH (u)-[user_progress:IS_READING_FOR_CLUB]->(book)
            OPTIONAL MATCH (book)-[:IS_EQUIVALENT_TO]-(actual_book:Book)
            return b.id as book_club_id,
                   b.name as book_club_name,
                   reading.started_date as started_date,
                   reading.selected_finish_date as expected_finish_date,
                   user_progress.current_chapter as current_chapter,
                   actual_book.title as currently_reading_book_title,
                   actual_book.small_img_url as currently_reading_book_small_img_url,
                   actual_book.id as currently_reading_book_id,
                   book.chapters as total_chapters
            """
        )

        query_w_limit = (
            """
            MATCH (u:User {id: $user_id})-[:OWNS_BOOK_CLUB]->(b:BookClub)
            OPTIONAL MATCH (b)-[reading:IS_READING]-(book:BookClubBook)
            OPTIONAL MATCH (u)-[user_progress:IS_READING_FOR_CLUB]->(book)
            OPTIONAL MATCH (book)-[:IS_EQUIVALENT_TO]-(actual_book:Book)
            return b.id as book_club_id,
                   b.name as book_club_name,
                   reading.started_date as started_date,
                   reading.selected_finish_date as expected_finish_date,
                   user_progress.current_chapter as current_chapter,
                   actual_book.title as currently_reading_book_title,
                   actual_book.small_img_url as currently_reading_book_small_img_url,
                   actual_book.id as currently_reading_book_id,
                   book.chapters as total_chapters
            LIMIT $limit
            """
        )

        if book_club_param.limit:
            result = tx.run(
                query_w_limit,
                user_id=book_club_param.user_id,
                limit=book_club_param.limit
            )
        else:
            result = tx.run(
                query,
                user_id=book_club_param.user_id
            )

        book_clubs = []
        for record in result:
            # Get the currently reading book if it exists
            if record.get("currently_reading_book_id"):
                current_book = BookClubSchemas.BookClubCurrentlyReading(
                    book_id=record.get("currently_reading_book_id"),
                    title=record.get("currently_reading_book_title"),
                    small_img_url=record.get(
                        "currently_reading_book_small_img_url")
                )
            else:
                current_book = None

            # Calculate the pace offset if all the required fields are present
            if (
                record.get("expected_finish_date") 
                and record.get("total_chapters") 
                and record.get("current_chapter")
            ):
                started_date = record.get("started_date")
                expected_finish_date = record.get("expected_finish_date")
                total_chapters = record.get("total_chapters")
                current_chapter = record.get("current_chapter")

                if isinstance(started_date, Neo4jDateTime):
                    started_date = started_date.to_native()

                if isinstance(expected_finish_date, Neo4jDateTime):
                    expected_finish_date = expected_finish_date.to_native()

                current_date = datetime.now()

                # Calculate total reading duration in days
                total_days = (expected_finish_date - started_date).days
                # Calculate elapsed days since the start
                elapsed_days = (current_date - started_date).days

                # Calculate expected chapters by the current date
                expected_chapters = (elapsed_days / total_days) * total_chapters

                # Calculate offset from the expected chapter
                pace_offset = current_chapter - round(expected_chapters)

            else:
                pace_offset = None

            book_clubs.append(
                BookClubSchemas.BookClubPreview(
                    book_club_id=record["book_club_id"],
                    book_club_name=record["book_club_name"],
                    pace=pace_offset,
                    currently_reading_book=current_book
                )
            )
        
        return book_clubs
    
    def get_member_book_clubs(
            self,
            book_club_param: BookClubSchemas.BookClubList
    ) -> List[BookClubSchemas.BookClubPreview]:
        """
        Get the book clubs where user is a member

        Args:
            book_club_param (BookClubSchemas.BookClubList): The search 
            parameters
        
        Returns:
            book_clubs: an array of book clubs where user is a member. 
            Book club information contains:
                book_club_id(str): Id of the book club
                book_club_name(str): Name of the book club
                pace(int): Pace of the book club
                currently_reading_book(list): List of books currently being 
                read
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_member_book_clubs_query, 
                book_club_param)
        return result
    
    @staticmethod
    def get_member_book_clubs_query(
        tx,
        book_club_param: BookClubSchemas.BookClubList
        ) -> List[BookClubSchemas.BookClubPreview]:
        
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF]->(b:BookClub)
            OPTIONAL MATCH (b)-[reading:IS_READING]-(book:BookClubBook)
            OPTIONAL MATCH (u)-[user_progress:IS_READING_FOR_CLUB]->(book)
            OPTIONAL MATCH (book)-[:IS_EQUIVALENT_TO]-(actual_book:Book)
            return b.id as book_club_id,
                   b.name as book_club_name,
                   reading.started_date as started_date,
                   reading.selected_finish_date as expected_finish_date,
                   user_progress.current_chapter as current_chapter,
                   actual_book.title as currently_reading_book_title,
                   actual_book.small_img_url as currently_reading_book_small_img_url,
                   actual_book.id as currently_reading_book_id,
                   book.chapters as total_chapters
            """
        )

        query_w_limit = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF]->(b:BookClub)
            OPTIONAL MATCH (b)-[reading:IS_READING]-(book:BookClubBook)
            OPTIONAL MATCH (u)-[user_progress:IS_READING_FOR_CLUB]->(book)
            OPTIONAL MATCH (book)-[:IS_EQUIVALENT_TO]-(actual_book:Book)
            return b.id as book_club_id,
                   b.name as book_club_name,
                   reading.started_date as started_date,
                   reading.selected_finish_date as expected_finish_date,
                   user_progress.current_chapter as current_chapter,
                   actual_book.title as currently_reading_book_title,
                   actual_book.small_img_url as currently_reading_book_small_img_url,
                   actual_book.id as currently_reading_book_id,
                   book.chapters as total_chapters
            LIMIT $limit
            """
        )

        if book_club_param.limit:
            result = tx.run(
                query_w_limit,
                user_id=book_club_param.user_id,
                limit=book_club_param.limit
            )
        else:
            result = tx.run(
                query,
                user_id=book_club_param.user_id
            )

        book_clubs = []
        for record in result:
            # Get the currently reading book if it exists
            if record.get("currently_reading_book_id"):
                current_book = BookClubSchemas.BookClubCurrentlyReading(
                    book_id=record.get("currently_reading_book_id"),
                    title=record.get("currently_reading_book_title"),
                    small_img_url=record.get(
                        "currently_reading_book_small_img_url")
                )
            else:
                current_book = None

            # Calculate the pace offset if all the required fields are present
            if (
                record.get("expected_finish_date") 
                and record.get("total_chapters") 
                and record.get("current_chapter")
            ):
                started_date = record.get("started_date")
                expected_finish_date = record.get("expected_finish_date")
                total_chapters = record.get("total_chapters")
                current_chapter = record.get("current_chapter")

                if isinstance(started_date, Neo4jDateTime):
                    started_date = started_date.to_native()

                if isinstance(expected_finish_date, Neo4jDateTime):
                    expected_finish_date = expected_finish_date.to_native()

                current_date = datetime.now()

                # Calculate total reading duration in days
                total_days = (expected_finish_date - started_date).days
                # Calculate elapsed days since the start
                elapsed_days = (current_date - started_date).days

                # Calculate expected chapters by the current date
                expected_chapters = (elapsed_days / total_days) * total_chapters

                # Calculate offset from the expected chapter
                pace_offset = current_chapter - round(expected_chapters)

            else:
                pace_offset = None

            book_clubs.append(
                BookClubSchemas.BookClubPreview(
                    book_club_id=record["book_club_id"],
                    book_club_name=record["book_club_name"],
                    pace=pace_offset,
                    currently_reading_book=current_book
                )
            )
        
        return book_clubs

    def search_users_not_in_club(
            self, 
            search_param: BookClubSchemas.BookClubInviteSearch
        ) -> None:
        """
        Searches for users not in the club

        Args:
            search_param (BookClubSchemas.BookClubInviteSearch): The search parameters
        
        Returns:
            users: an array of users that match the search string. User information
            contains:
                user_id(str): Id of the user
                user_username(str): username of the user
        """
        with self.driver.session() as session:
            result = session.read_transaction(self.search_users_not_in_club_query, search_param)
        return result
    
    @staticmethod
    def search_users_not_in_club_query(
        tx,
        search_param: BookClubSchemas.BookClubInviteSearch
        ) -> None:

        query = (
        """
        CALL db.index.fulltext.queryNodes('userFullText', $search_query)
        YIELD node, score
        WHERE NOT (node)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(:BookClub {id: $book_club_id})
        RETURN node, score
        ORDER BY score DESC
        LIMIT $limit
        """)

        result = tx.run(
            query,
            search_query=search_param.param,
            book_club_id=search_param.book_club_id,
            limit=search_param.limit
        )

        users = []
        for record in result:
            print(record)
            users.append({
                "user_id": record["node"]["id"],
                "user_username": record["node"]["username"]
            })
        
        return users