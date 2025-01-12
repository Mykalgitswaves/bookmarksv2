from datetime import datetime, timezone
from neo4j.time import DateTime as Neo4jDateTime
from typing import List, Optional
from datetime import datetime, timedelta

from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas import bookclubs as BookClubSchemas
from src.models.schemas.books import BookPreview
from src.models.schemas.users import Member 
from src.utils.helpers.help import AWARD_CONSTANTS

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
        
        query_just_users = (
            """
            MATCH (b:BookClub {id: $book_club_id})<-[:OWNS_BOOK_CLUB]-(u:User {id: $user_id})
            UNWIND $user_ids AS uid
            MATCH (invited_user:User {id: uid})

            OPTIONAL MATCH (invited_user)-[:IS_MEMBER_OF]->(b)
            OPTIONAL MATCH (invited_user)-[:RECEIVED_INVITE]->(existing_invite:BookClubInvite)-[:INVITE_FOR]->(b)

            WITH b, u, invited_user, existing_invite,
                CASE 
                    WHEN (invited_user)-[:IS_MEMBER_OF]->(b) THEN 'already_member'
                    WHEN existing_invite IS NOT NULL THEN 'invite_already_sent'
                    ELSE 'invite_sent'
                END AS action

            FOREACH (_ IN CASE WHEN action <> 'already_member' THEN [1] ELSE [] END |
                MERGE (invited_user)-[:RECEIVED_INVITE]->(user_invite:BookClubInvite)-[:INVITE_FOR]->(b)
                ON CREATE SET user_invite.id = "club_invite_" + randomUUID(),
                            user_invite.created_date = datetime()
                MERGE (u)-[:SENT_INVITE]->(user_invite)
            )

            RETURN b.id AS book_club_id, 
                   invited_user.id AS user_id, 
                   action
            """)
        
        query_just_emails = (
            """
            MATCH (b:BookClub {id: $book_club_id})<-[:OWNS_BOOK_CLUB]-(u:User {id: $user_id})
            UNWIND $emails AS email

            // Attempt to match an existing user by email
            OPTIONAL MATCH (existing_user:User {email: email})

            // Check if the existing user is a member of the book club
            OPTIONAL MATCH (existing_user)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b)

            // Check if the existing user has already received an invite
            OPTIONAL MATCH (existing_user)-[:RECEIVED_INVITE]->(existing_invite:BookClubInvite)-[:INVITE_FOR]->(b)

            // Check if an InvitedUser node already exists for this email
            OPTIONAL MATCH (invited_user:InvitedUser {email: email})

            // Determine the action to take for each email
            WITH b, u, email, existing_user, existing_invite, invited_user,
                CASE
                    WHEN existing_user IS NOT NULL AND (existing_user)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b) THEN 'already_member'
                    ELSE 'invite_sent'
                END AS action

            // Handle invites for new emails (users not in the system)
            FOREACH (_ IN CASE WHEN action = 'invite_sent' AND existing_user IS NULL THEN [1] ELSE [] END |
                MERGE (new_invited_user:InvitedUser {email: email})
                ON CREATE SET new_invited_user.id = "invited_user_" + randomUUID(),
                            new_invited_user.created_date = datetime()
                MERGE (new_invited_user)-[:RECEIVED_INVITE]->(user_invite_email:BookClubInvite)-[:INVITE_FOR]->(b)
                ON CREATE SET user_invite_email.id = "club_invite_" + randomUUID(),
                            user_invite_email.created_date = datetime()
                MERGE (u)-[:SENT_INVITE]->(user_invite_email)
            )

            // Handle invites for existing users not yet invited
            FOREACH (_ IN CASE WHEN action = 'invite_sent' AND existing_user IS NOT NULL THEN [1] ELSE [] END |
                MERGE (existing_user)-[:RECEIVED_INVITE]->(user_invite_email:BookClubInvite)-[:INVITE_FOR]->(b)
                ON CREATE SET user_invite_email.id = "club_invite_" + randomUUID(),
                            user_invite_email.created_date = datetime()
                MERGE (u)-[:SENT_INVITE]->(user_invite_email)
            )

            // Return the result for each email
            RETURN b.id AS book_club_id, 
                   email, 
                   action
            """)

        query_get_id = (
            """
            UNWIND $user_identifiers as user_identifier
            MATCH (user:InvitedUser|User)
            WHERE user.email = user_identifier or user.id = user_identifier
            MATCH (user)-[:RECEIVED_INVITE]->(user_invite:BookClubInvite)-[:INVITE_FOR]->(b:BookClub {id:$book_club_id})
            RETURN user_identifier,
                   user_invite.id as invite_id
            """)  
        
        invite_statuses = {}
        if invite.user_ids:
            result = tx.run(
                query_just_users,
                book_club_id=invite.book_club_id,
                user_ids=invite.user_ids,
                user_id=invite.user_id
            )

            for response in result:
                if not response.get("user_id"):
                    continue
                invite_statuses.update(
                    {
                        response.get("user_id"): {
                            "status": response.get("action"),
                            "id": response.get("invite_id")
                        }
                    }
                )
            

        if invite.emails:
            result = tx.run(
                query_just_emails,
                book_club_id=invite.book_club_id,
                emails=invite.emails,
                user_id=invite.user_id
            )
            for response in result:
                if not response.get("email"):
                    continue
                invite_statuses.update(
                    {
                        response.get("email"): {
                            "status": response.get("action")
                        }
                    }
                )
        
        user_identifiers = [identifier 
                            for identifier in invite_statuses
                            if invite_statuses[identifier].get("status") in ["invite_sent","invite_already_sent"]]
        
        if user_identifiers:
            result = tx.run(
                query_get_id,
                book_club_id=invite.book_club_id,
                user_identifiers=user_identifiers
            )
            for response in result:
                if response.get("user_identifier") in invite_statuses:
                    invite_statuses[response.get("user_identifier")]['id'] = response.get("invite_id")
                    

        return invite_statuses

    def create_bookclub_invites_dep(
            self,
            invite: BookClubSchemas.BookClubInvite
        ) -> None:
        """
        DEPRECATED
        Creates invites for the bookclub

        Args:
            invite (BookClubSchemas.BookClubInvite): The invite to create
        """
        with self.driver.session() as session:
            result = session.write_transaction(self.create_bookclub_invites_dep_query, invite)
        return result
    
    @staticmethod
    def create_bookclub_invites_dep_query(
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
                MERGE (invited_new_user:InvitedUser {email: email})
                ON CREATE SET invited_new_user.id = "invited_user_" + randomUUID(),
                            invited_new_user.created_date = datetime()
                MERGE (invited_new_user)-[:RECEIVED_INVITE]->(user_invite_email:BookClubInvite)-[:INVITE_FOR]->(b)
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
        
        query_just_users = (
            """
            MATCH (b:BookClub {id: $book_club_id})<-[r:OWNS_BOOK_CLUB]-(u:User {id: $user_id})
            UNWIND $user_ids as user_id
            MATCH (invited_user:User {id: user_id})
            MERGE (invited_user)-[:RECEIVED_INVITE]->(user_invite:BookClubInvite)-[:INVITE_FOR]->(b)
            ON CREATE SET user_invite.id = "club_invite_" + randomUUID(),
                          user_invite.created_date = datetime()
            MERGE (u)-[:SENT_INVITE]->(user_invite)

            RETURN b.id as book_club_id
            """)
        
        query_just_emails = (
            """
            MATCH (b:BookClub {id: $book_club_id})<-[r:OWNS_BOOK_CLUB]-(u:User {id: $user_id})

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
        if not invite.user_ids and not invite.emails:
            return False
        
        elif not invite.user_ids:
            result = tx.run(
                query_just_emails,
                book_club_id=invite.book_club_id,
                emails=invite.emails,
                user_id=invite.user_id
            )

        elif not invite.emails:
            result = tx.run(
                query_just_users,
                book_club_id=invite.book_club_id,
                user_ids=invite.user_ids,
                user_id=invite.user_id
            )

        else:
            result = tx.run(
                query,
                book_club_id=invite.book_club_id,
                user_ids=invite.user_ids,
                user_id=invite.user_id,
                emails=invite.emails
            )
        
        response = result.single()
        if response:
            return response["book_club_id"]
        else:
            return False

    def create_currently_reading_club(
            self,
            currently_reading_obj: BookClubSchemas.StartCurrentlyReading
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_currently_reading_club_query, 
                currently_reading_obj)
        return result
    
    @staticmethod
    def create_currently_reading_club_query(
        tx,
        currently_reading_obj: BookClubSchemas.StartCurrentlyReading
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:OWNS_BOOK_CLUB]-(b:BookClub {id:$book_club_id})
            WITH u, b
            WHERE NOT EXISTS {
                MATCH (b)-[:IS_READING]->(:BookClubBook)
            }
            MATCH (book:Book {id:$book_id})
            CREATE (bc_book:BookClubBook {
                id: "book_club_book_" + randomUUID(),
                chapters: $chapters
            })
            CREATE (bc_book)-[:IS_EQUIVALENT_TO]->(book)
            MERGE (b)-[:IS_READING {
                started_date: datetime(),
                selected_finish_date: $finish_date
            }]->(bc_book)
            WITH b, bc_book
            MATCH (member:User)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b)
            OPTIONAL MATCH (member)-[oldRel:IS_READING_FOR_CLUB]->(old_book:BookClubBook)
            WITH b, bc_book, member, oldRel, old_book
            // If an existing IS_READING_FOR_CLUB relationship is found, delete it and create FINISHED_READING_FOR_CLUB
            FOREACH (_ IN CASE WHEN oldRel IS NOT NULL THEN [1] ELSE [] END |
                DELETE oldRel
                MERGE (member)-[:FINISHED_READING_FOR_CLUB {last_updated: datetime(), finished_by_user: false}]->(old_book)
            )
            MERGE (member)-[:IS_READING_FOR_CLUB {
                last_updated: datetime(),
                current_chapter: 0
            }]->(bc_book)
            WITH b, bc_book
            MATCH (awards:ClubAward)
            MERGE (awards)-[:AWARD_FOR_BOOK {grants_per_member:1000}]->(bc_book)
            RETURN bc_book.id as book_club_book_id
            """
        )
        expected_finish_date = Neo4jDateTime.from_native(currently_reading_obj.expected_finish_date)
        result = tx.run(
            query,
            user_id=currently_reading_obj.user_id,
            book_club_id=currently_reading_obj.id,
            book_id=currently_reading_obj.book['id'],
            chapters=currently_reading_obj.book['chapters'],
            finish_date=expected_finish_date,
        )

        response = result.single()
        
        if not response:
            return
        
        return response.get("book_club_book_id")
    
    def create_currently_reading_club_and_book(
            self,
            currently_reading_obj: BookClubSchemas.StartCurrentlyReading,
            title: str,
            small_img_url: str,
            author_names: List[str]
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_currently_reading_club_and_book_query, 
                currently_reading_obj,
                title,
                small_img_url,
                author_names)
        return result
    
    @staticmethod
    def create_currently_reading_club_and_book_query(
        tx,
        currently_reading_obj: BookClubSchemas.StartCurrentlyReading,
        title: str,
        small_img_url: str,
        author_names: List[str]
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:OWNS_BOOK_CLUB]-(b:BookClub {id:$book_club_id})
            create (book:Book {
                id:"c"+randomUUID(),
                google_id:$book_id, 
                title:$title, 
                small_img_url:$small_img_url, 
                author_names: $author_names
            })
            WITH u, b, book
            WHERE NOT EXISTS {
                MATCH (b)-[:IS_READING]->(:BookClubBook)
            }
            CREATE (bc_book:BookClubBook {
                id: "book_club_book_" + randomUUID(),
                chapters: $chapters
            })
            CREATE (bc_book)-[:IS_EQUIVALENT_TO]->(book)
            MERGE (b)-[:IS_READING {
                started_date: datetime(),
                selected_finish_date: $finish_date
            }]->(bc_book)
            OPTIONAL MATCH (old_member)-[oldRel:IS_READING_FOR_CLUB]->(old_book:BookClubBook)<-[:IS_READING|STOPPED_READING|FINISHED_READING]-(b)
            WITH b, bc_book, old_member, oldRel, old_book
            // If an existing IS_READING_FOR_CLUB relationship is found, delete it and create FINISHED_READING_FOR_CLUB
            FOREACH (_ IN CASE WHEN oldRel IS NOT NULL THEN [1] ELSE [] END |
                DELETE oldRel
                MERGE (old_member)-[:FINISHED_READING_FOR_CLUB {last_updated: datetime(), finished_by_user: false}]->(old_book)
            )
            WITH b, bc_book
            MATCH (member:User)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b)
            MERGE (member)-[:IS_READING_FOR_CLUB {
                last_updated: datetime(),
                current_chapter: 0
            }]->(bc_book)
            WITH b, bc_book
            MATCH (awards:ClubAward)
            MERGE (awards)-[:AWARD_FOR_BOOK {grants_per_member:1000}]->(bc_book)
            RETURN bc_book.id as book_club_book_id
            """
        )

        result = tx.run(
            query,
            user_id=currently_reading_obj.user_id,
            book_club_id=currently_reading_obj.id,
            book_id=currently_reading_obj.book['id'],
            chapters=currently_reading_obj.book['chapters'],
            finish_date=currently_reading_obj.expected_finish_date,
            title=title,
            small_img_url=small_img_url,
            author_names=author_names
        )

        response = result.single()
        
        if not response:
            return
        
        return response.get("book_club_book_id")
    
    def create_update_post(
            self,
            update_data:BookClubSchemas.CreateUpdatePost
    ) -> bool:
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_update_post_query, 
                update_data)
        return result
    
    @staticmethod
    def create_update_post_query(
            tx,
            update_data:BookClubSchemas.CreateUpdatePost
    ) -> bool:
        
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(b:BookClub {id:$book_club_id})
            MATCH (b)-[:IS_READING]->(book:BookClubBook)
            MATCH (u)-[user_reading:IS_READING_FOR_CLUB]->(book)
            CREATE (update:ClubUpdate {
                id: "club_update_" + randomUUID(),
                created_date: datetime(),
                chapter: $chapter,
                deleted: False,
                headline: $headline,
                response: $response,
                quote: $quote,
                likes: 0
            })
            MERGE (u)-[:POSTED]->(update)-[:POST_FOR_CLUB_BOOK]->(book)
            SET user_reading.current_chapter = $chapter,
                user_reading.last_updated = datetime()
            RETURN book.id as book_id
            """
        )

        result = tx.run(
            query,
            user_id=update_data.user['id'],
            book_club_id=update_data.id,
            chapter=update_data.chapter,
            headline=update_data.headline,
            response=update_data.response,
            quote=update_data.quote
        )

        response = result.single()
        return response.get("book_id") is not None
    
    def create_update_post_no_text(
            self,
            update_data:BookClubSchemas.CreateUpdatePost
    ) -> bool:
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_update_post_no_text_query, 
                update_data)
        return result
    
    @staticmethod
    def create_update_post_no_text_query(
            tx,
            update_data:BookClubSchemas.CreateUpdatePost
    ) -> bool:
        
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(b:BookClub {id:$book_club_id})
            MATCH (b)-[:IS_READING]->(book:BookClubBook)
            MATCH (u)-[user_reading:IS_READING_FOR_CLUB]->(book)
            CREATE (update:ClubUpdateNoText {
                id: "club_update_" + randomUUID(),
                created_date: datetime(),
                chapter: $chapter,
                deleted: False,
                likes: 0
            })
            MERGE (u)-[:POSTED]->(update)-[:POST_FOR_CLUB_BOOK]->(book)
            SET user_reading.current_chapter = $chapter,
                user_reading.last_updated = datetime()
            RETURN book.id as book_id
            """
        )

        result = tx.run(
            query,
            user_id=update_data.user['id'],
            book_club_id=update_data.id,
            chapter=update_data.chapter
        )

        response = result.single()
        return response.get("book_id") is not None
    
    
    def create_award_for_post(
            self,
            create_award: BookClubSchemas.CreateAward
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_award_for_post_query, 
                create_award
            )
        return result
    
    @staticmethod
    def create_award_for_post_query(
        tx,
        create_award: BookClubSchemas.CreateAward
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (club)-[:IS_READING]->(book:BookClubBook)
            MATCH (book)<-[award_rel:AWARD_FOR_BOOK]-(award:ClubAward {id:$award_id})
            MATCH (post:ClubUpdate|ClubUpdateNoText {id:$post_id})-[:POST_FOR_CLUB_BOOK]->(book)
            OPTIONAL MATCH (u)-[:GRANTED]->(club_award:ClubAwardForPost)-[:AWARD_FOR_POST]->(post)
            WITH u, award, COUNT(club_award) AS existing_award_count, award_rel, post
                WHERE existing_award_count < 1
                CREATE (created_award:ClubAwardForPost {
                    id: "post_award_" + randomUUID(),
                    created_date: datetime()
                })
                MERGE (u)-[:GRANTED]->(created_award)-[:IS_CHILD_OF]->(award)
                MERGE (created_award)-[:AWARD_FOR_POST]->(post)
            RETURN existing_award_count, award_rel.grants_per_member as grants_per_member
            """
        )

        result = tx.run(
            query,
            user_id=create_award.user_id,
            book_club_id=create_award.book_club_id,
            award_id=create_award.award_id,
            post_id=create_award.post_id
        )

        response = result.single()

        if response:
            if response.get("existing_award_count") <= response.get("grants_per_member"):
                return "award created"
            else:
                return "limit reached"
        else:
            return "unauthorized"
    
    def create_club_notification(
            self, 
            notif: BookClubSchemas.ClubNotificationCreate):
        """
        create a notification to bug users to read a currently reading book inside of a club! NOT EMAILS, 
        these are just for the mobile menu.
        """

        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_club_notification_query,
                sent_by_user_id=notif.sent_by_user_id,
                member_id=notif.member_id,
                book_club_id=notif.book_club_id,
                notification_type=notif.notification_type
            )
        return result
    
    @staticmethod
    def create_club_notification_query(
        tx, 
        sent_by_user_id:str, 
        member_id:str, 
        book_club_id:str, 
        notification_type:str
        ):
        """
        We only want to allow for notifications of a certain type for a 
        certain user to be created within a given interval so users don't feel flooded!
        These should also be an opt in feature for a specific pace of bookclub. 
        Some readers (casuals) don't want to feel stressed or like they are holding up the club. 
        In that case this feature could actually work against them.
        The receiving user can't already have a notification created within the past 7 days. 
        Meaning one notification exists that is greater than the past 7 days.
        """

        query = """
            MATCH (bc:BookClub {id: $book_club_id})<-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(sendingUser:User {id: $sent_by_user_id})
            MATCH (bc)<-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(receivingUser:User {id: $member_id})
            WITH receivingUser, sendingUser, bc
            CREATE (createdClubNotification:ClubNotification {
                id: "club_notification_" + randomUUID(),
                notification_type: $notification_type,
                created_date: datetime(),
                dismissed: false
            })
            MERGE (sendingUser)-[created_notification:CREATED_NOTIFICATION]->(createdClubNotification)
            MERGE (createdClubNotification)-[notification_for_user:NOTIFICATION_FOR_USER]->(receivingUser)
            MERGE (bc)<-[notification_for_club:NOTIFICATION_FOR_CLUB]-(createdClubNotification)
            RETURN createdClubNotification, sendingUser.username as sent_by_user_username, bc.name as book_club_name,
                CASE WHEN createdClubNotification IS NOT NULL THEN true ELSE false END AS createdPost
        """

        result = tx.run(
            query, 
            book_club_id=book_club_id, 
            sent_by_user_id=sent_by_user_id, 
            member_id=member_id,
            notification_type=notification_type
        )

        response = result.single()

        if not response.get('createdPost'):
            return False

        created_notification = response.get('createdClubNotification')

        notification = BookClubSchemas.ClubNotification(
            id=created_notification.get('id'),
            sent_by_user_id=sent_by_user_id,
            notification_type=notification_type,
            member_id=member_id,
            dismissed=created_notification.get('dismissed', False),
            created_date=created_notification.get('created_date'),
            book_club_id=book_club_id,
            sent_by_user_username=response.get('sent_by_user_username'),
        )

        return notification
    
    def create_review_and_finished_reading(
            self,
            review: BookClubSchemas.CreateReviewPost
    ):
        """
        Creates the review in the DB and marks the book as finished reading
        by user
        """
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_review_and_finished_reading_query, 
                review
            )
        return result
    
    @staticmethod
    def create_review_and_finished_reading_query(
        tx,
        review: BookClubSchemas.CreateReviewPost
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (b)-[:IS_READING|FINISHED_READING]->(book:BookClubBook)
            WHERE book.id = $book_club_book_id
            MERGE (r:ClubReview {
            user_id: $user_id,
            book_club_book_id: book.id})
            ON CREATE SET 
                r.id = "club_review_" + randomUUID(),
                r.created_date = datetime(),
                r.headline = $headline,
                r.questions = $questions,
                r.question_ids = $question_ids,
                r.responses = $responses,
                r.rating = $rating,
                r.deleted = False,
                r.likes = 0
            MERGE (u)-[:POSTED]->(r)
            MERGE (r)-[:POST_FOR_CLUB_BOOK]->(book)
            MERGE (u)-[fr:FINISHED_READING_FOR_CLUB]->(book)
            ON CREATE SET
                fr.last_updated = datetime(),
                fr.finished_by_user = True
            WITH u, book
            MATCH (u)-[rr:IS_READING_FOR_CLUB]->(book)
            DELETE rr
            With u
            return u.id as user_id
            """
        )

        result = tx.run(
            query,
            user_id = review.user['id'],
            book_club_id = review.id,
            headline = review.headline,
            questions = review.questions,
            question_ids = review.question_ids,
            responses = review.responses,
            rating = review.rating,
            book_club_book_id = review.book_club_book_id
        )

        response = result.single()

        return bool(response)
    
    def create_finished_reading(
            self,
            user_id: str,
            book_club_id: str,
            rating: Optional[int],
            book_club_book_id: str
    ):
        """
        Creates the review in the DB and marks the book as finished reading
        by user
        """
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_finished_reading_query, 
                user_id,
                book_club_id,
                rating,
                book_club_book_id
            )
        return result
    
    @staticmethod
    def create_finished_reading_query(
        tx,
        user_id,
        book_club_id,
        rating,
        book_club_book_id
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (b)-[:IS_READING|FINISHED_READING]->(book:BookClubBook)
            WHERE book.id = $book_club_book_id
            MERGE (u)-[fr:FINISHED_READING_FOR_CLUB]->(book)
            ON CREATE SET
                fr.last_updated = datetime(),
                fr.finished_by_user = True
                CREATE (r:ClubReviewNoText {
                    id: "club_review_no_text_" + randomUUID(),
                    user_id: $user_id,
                    book_club_book_id: book.id,
                    created_date: datetime(),
                    deleted: False,
                    likes: 0,
                    rating: $rating
                })
                MERGE (u)-[:POSTED]->(r)
                MERGE (r)-[:POST_FOR_CLUB_BOOK]->(book)
            WITH u, book
            MATCH (u)-[rr:IS_READING_FOR_CLUB]->(book)
            DELETE rr
            With u
            return u.id as user_id
            """
        )

        result = tx.run(
            query,
            user_id = user_id,
            book_club_id = book_club_id,
            rating = rating,
            book_club_book_id = book_club_book_id,
        )

        response = result.single()

        return bool(response)
    
    def get_minimal_book_club(
            self,
            book_club_id: str,
            user_id: str
    ):
        """
        Gets a minimal bookclub
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_minimal_book_club_query, 
                book_club_id, 
                user_id
            )
        return result
    
    @staticmethod
    def get_minimal_book_club_query(tx, book_club_id, user_id):
        query = """
            match(b:BookClub {id: $book_club_id})
            match(u:User {id: $user_id})
            OPTIONAL MATCH (b)-[reading:IS_READING]-(book:BookClubBook)
            OPTIONAL MATCH (u)-[user_progress:IS_READING_FOR_CLUB]->(book)
            OPTIONAL MATCH (book)-[:IS_EQUIVALENT_TO]-(actual_book:Book)
            return b.id as book_club_id,
                   b.name as book_club_name,
                   b.description as book_club_description,
                   reading.started_date as started_date,
                   reading.selected_finish_date as expected_finish_date,
                   user_progress.current_chapter as current_chapter,
                   actual_book.title as currently_reading_book_title,
                   actual_book.small_img_url as currently_reading_book_small_img_url,
                   actual_book.id as currently_reading_book_id,
                   book.chapters as total_chapters,
                   book.id as book_club_book_id
        """
        result = tx.run(query, book_club_id=book_club_id, user_id=user_id)
        record = result.single()

        if record.get("currently_reading_book_id"):
            current_book = BookClubSchemas.BookClubCurrentlyReading(
                book_id=record.get("currently_reading_book_id"),
                book_club_book_id=record.get("book_club_book_id"),
                title=record.get("currently_reading_book_title"),
                small_img_url=record.get(
                    "currently_reading_book_small_img_url"),
                author_names=[]
            )
        else:
            current_book = {}

        pace_offset = BookClubSchemas.BaseBookClub.get_pace_offset(record)

        minimal_bookclub = BookClubSchemas.MinimalBookClub(
            book_club_id=record["book_club_id"],
            book_club_name=record["book_club_name"],
            book_club_description=record["book_club_description"],
            pace=pace_offset,
            currently_reading_book=current_book
        )   

        return minimal_bookclub

    def get_members_for_book_club(self, book_club_id, user_id):
        """
        Gets a minimal bookclub
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_members_for_book_club_query, 
                book_club_id, 
                user_id
            )
        return result

    @staticmethod
    def get_members_for_book_club_query(tx, book_club_id, user_id):
        query = """
            MATCH (u:User {id: $user_id})-[:OWNS_BOOK_CLUB|IS_MEMBER_OF]->(b:BookClub {id: $book_club_id})
            MATCH(member:User {disabled: False})-[r:IS_MEMBER_OF]->(b)
                return member.id as id, 
                    member.username as username,
                    member.email as email
        """

        result = tx.run(query, book_club_id=book_club_id, user_id=user_id)
        if not result:
            return False

        members = []

        for record in result:
            member = Member(
                id=record['id'],
                username=record['username'],
                email=record['email'],
            )
            members.append(member)
        return members

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
                   actual_book.author_names as currently_reading_book_author_names,
                   book.chapters as total_chapters,
                   book.id as book_club_book_id
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
                author_names = record.get('currently_reading_book_author_names')
                current_book = BookClubSchemas.BookClubCurrentlyReading(
                    book_id=record.get("currently_reading_book_id"),
                    book_club_book_id=record.get("book_club_book_id"),
                    title=record.get("currently_reading_book_title"),
                    small_img_url=record.get(
                        "currently_reading_book_small_img_url"),
                    author_names=author_names if author_names else [],
                )
            else:
                current_book = None
            
            # Calculate the pace offset if all the required fields are present
            pace_offset = BookClubSchemas.BaseBookClub.get_pace_offset(record)

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
                   actual_book.author_names as currently_reading_book_author_names,
                   book.chapters as total_chapters,
                   book.id as book_club_book_id
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
                # Author names will get but might return None
                author_names = record.get('currently_reading_book_author_names')
                current_book = BookClubSchemas.BookClubCurrentlyReading(
                    book_id=record.get("currently_reading_book_id"),
                    book_club_book_id=record.get("book_club_book_id"),
                    title=record.get("currently_reading_book_title"),
                    small_img_url=record.get(
                        "currently_reading_book_small_img_url"),
                    author_names=author_names if author_names else [],
                )
            else:
                current_book = None

            # Calculate the pace offset if all the required fields are present
            pace_offset = BookClubSchemas.BaseBookClub.get_pace_offset(record)

            book_clubs.append(
                BookClubSchemas.BookClubPreview(
                    book_club_id=record["book_club_id"],
                    book_club_name=record["book_club_name"],
                    pace=pace_offset,
                    currently_reading_book=current_book
                )
            )
        
        return book_clubs
    
    
    def get_invites_for_book_club(
        self,
        user_id,
        book_club_id
    ) -> List[BookClubSchemas.BookClubInvite]:
        """
        Gets all bookclub invites sent from a particular club
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_invites_for_book_club_query,
                user_id=user_id, 
                book_club_id=book_club_id
            )
        return result
    

    @staticmethod
    def get_invites_for_book_club_query(
        tx, 
        user_id, 
        book_club_id
    ):
        query = """
            MATCH (u:User {id: $user_id})-[:OWNS_BOOK_CLUB]->(bc:BookClub {id: $book_club_id})
            MATCH (invited_user:User)-[:RECEIVED_INVITE]->(i:BookClubInvite)-[:INVITE_FOR]->(bc)
            RETURN invited_user.id as invited_user_id,
                invited_user.username as invited_user_username,
                invited_user.email as invited_user_email,
                i.id as invite_id,
                i.created_date as datetime_invited
        """
        result = tx.run(
                query,
                user_id=user_id,
                book_club_id=book_club_id
            )
    
        invites = []
        
        for record in result:
            invite = BookClubSchemas.BookClubInviteAdminPreview(
                        invite_id=record["invite_id"],
                        invited_user={
                            "id": record["invited_user_id"],
                            "username": record.get('invited_user_username', ''),
                            "email":record.get('invited_user_email', 'no email for this invite'),
                        },
                        datetime_invited=record["datetime_invited"],
                    )
            invites.append(invite)
        return invites
        

    def get_book_club_invites(
            self,
            invite_params: BookClubSchemas.BookClubList
        ) -> List[BookClubSchemas.BookClubInvitePreview]:
        """
        Gets all the invites sent to the user

        Args:
            invite_params (BookClubSchemas.BookClubList): The search 
            parameters

        Returns:
            A list of the book club invites
        """

        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_book_club_invites_query, 
                invite_params)
        return result
    
    @staticmethod
    def get_book_club_invites_query(
        tx,
        invite_params: BookClubSchemas.BookClubList
        ) -> List[BookClubSchemas.BookClubInvitePreview]:

        query = (
            """
            MATCH (u:User {id: $user_id})-[:RECEIVED_INVITE]->(i:BookClubInvite)-[:INVITE_FOR]->(b:BookClub)
            MATCH (owner:User)-[:OWNS_BOOK_CLUB]->(b)
            OPTIONAL MATCH (u)-[owner_friend:FRIENDED]-(owner)
            WITH i, b, owner, owner_friend
            OPTIONAL MATCH (u)-[mutual_friend:FRIENDED]-(mutual:User)-[user_member:IS_MEMBER_OF]->(b)
            WITH i, b, owner, owner_friend, count(mutual) as num_mutual_friends
            RETURN i.id as invite_id,
                   b.id as book_club_id,
                   b.name as book_club_name,
                   owner.username as book_club_owner_name,
                   num_mutual_friends,
                   owner_friend IS NOT NULL as is_owner_friend,
                   i.created_date as datetime_invited
            """
        )

        query_w_limit = (
            """
            MATCH (u:User {id: $user_id})-[:RECEIVED_INVITE]->(i:BookClubInvite)-[:INVITE_FOR]->(b:BookClub)
            MATCH (owner:User)-[:OWNS_BOOK_CLUB]->(b)
            OPTIONAL MATCH (u)-[owner_friend:FRIENDED]-(owner)
            WITH i, b, owner, owner_friend
            OPTIONAL MATCH (u)-[mutual_friend:FRIENDED]-(mutual:User)-[user_member:IS_MEMBER_OF]->(b)
            WITH i, b, owner, owner_friend, count(mutual) as num_mutual_friends
            RETURN i.id as invite_id,
                   b.id as book_club_id,
                   b.name as book_club_name,
                   owner.username as book_club_owner_name,
                   num_mutual_friends,
                   owner_friend IS NOT NULL as is_owner_friend,
                   i.created_date as datetime_invited
            LIMIT $limit
            """
        )

        if invite_params.limit:
            result = tx.run(
                query_w_limit,
                user_id=invite_params.user_id,
                limit=invite_params.limit
            )
        else:
            result = tx.run(
                query,
                user_id=invite_params.user_id
            )

        invites = []
        for record in result:
            
            invite = BookClubSchemas.BookClubInvitePreview(
                        invite_id=record["invite_id"],
                        book_club_id=record["book_club_id"],
                        book_club_name=record["book_club_name"],
                        book_club_owner_name=record["book_club_owner_name"],
                        num_mutual_friends=record["num_mutual_friends"],
                        datetime_invited=record["datetime_invited"]
                    )
            
            if record["is_owner_friend"]:
                invite.num_mutual_friends += 1

            invites.append(invite)

        return invites

    def get_user_pace(
            self,
            book_club_id: str,
            user_id: str
    ) -> BookClubSchemas.BookClubPaces:
        """
        Gets the pace of the user in the book club

        Args:
            book_club_id (str): The id of the book club
            user_id (str): The id of the user
        
        Returns:
            pace: The pace of the user in the book club
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_user_pace_query, 
                book_club_id, 
                user_id
            )
        return result
    
    @staticmethod
    def get_user_pace_query(tx, book_club_id, user_id):

        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (b)-[club_reading:IS_READING]->(book:BookClubBook)
            MATCH (u)-[user_reading:IS_READING_FOR_CLUB]->(book)
            MATCH (:User)-[members_reading:IS_READING_FOR_CLUB]->(book)
            return user_reading.current_chapter as current_chapter,
                   club_reading.started_date as started_date,
                   club_reading.selected_finish_date as expected_finish_date,
                   book.chapters as total_chapters,
                   avg(members_reading.current_chapter) as average_member_chapter
            """
        )

        result = tx.run(
                query,
                book_club_id=book_club_id,
                user_id=user_id
            )
        
        response = result.single()

        if response:
            paces = BookClubSchemas.BookClubPaces(
                user_pace=response.get("current_chapter"),
                total_chapters=response.get("total_chapters"),
                club_pace=round(response.get("average_member_chapter",0)),
                expected_pace=BookClubSchemas.BaseBookClub.get_pace_offset(
                    response)
            )
            return paces
        
    def get_member_paces(
            self,
            book_club_id:str,
            user_id:str
    ) -> List[dict]:
        """
        Gets the current chapter of each member in the club

        Args:
            book_club_id: The id of the book club to get

        Returns:
            member_paces (array): an array, where each object is a dictionary which
            contains the following values. The array is sorted by member_pace 
            descending:
                id (str): the uuid of the member
                username (str): the username of the member
                pace (int):  the current chapter of the member
                is_current_user (bool): Flag for if this member is the current user
        """

        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_member_paces_query, 
                book_club_id, 
                user_id
            )
        return result
    
    @staticmethod
    def get_member_paces_query(
        tx,
        book_club_id: str,
        user_id: str
    ):
        
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[club_reading:IS_READING]->(book:BookClubBook)
            MATCH (u)-[user_reading:IS_READING_FOR_CLUB]->(book)
            MATCH (members:User)-[members_reading:IS_READING_FOR_CLUB]->(book)
            return  u.id as user_id,
                    members,
                    members_reading
            """
        )

        
        result = tx.run(
            query,
            book_club_id=book_club_id,
            user_id=user_id
        )
        member_paces = []
        for response in result:
            member_pace = {
                "id": response.get("members", {}).get('id'),
                "username":response.get("members", {}).get("username"),
                "pace":response.get("members_reading", {}).get("current_chapter"),
                "is_current_user": response.get("members", {}).get("id") == user_id
            }

            member_paces.append(member_pace)
        
        member_paces = sorted(member_paces, key=lambda member: member['pace'], reverse=True)
        
        return member_paces
        
    def get_book_club_feed(
            self,
            book_club_id: str,
            user_id: str,
            skip: int,
            limit: int,
            filter: bool
    ) -> List[BookClubSchemas.UpdatePost]:
        """
        Gets the book club feed for the user
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_book_club_feed_query, 
                book_club_id, 
                user_id,
                skip,
                limit,
                filter
            )
        return result
    
    @staticmethod
    def get_book_club_feed_query(
        tx,
        book_club_id: str,
        user_id: str,
        skip: int,
        limit: int,
        filter: bool,
    ):
        
        query = (
            """
            MATCH (cu:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (b)-[:IS_READING]->(book:BookClubBook)
            MATCH (post {deleted:false})-[:POST_FOR_CLUB_BOOK]->(book)
            WHERE post:ClubUpdate OR post:ClubUpdateNoText
            match (post)<-[pr:POSTED]-(u:User)
            optional match (cu)-[lr:LIKES]->(post)
            optional match (any)-[nl:LIKES]->(post)
            optional match (book)-[br:IS_EQUIVALENT_TO]-(canon_book:Book)
            optional match (comments:Comment {deleted:false})<-[:HAS_COMMENT]-(post)
            optional match (post)<-[:AWARD_FOR_POST]-(post_award:ClubAwardForPost)
            optional match award_long = (award_user:User)-[:GRANTED]->(post_award)-[:IS_CHILD_OF]->(award:ClubAward)
            RETURN post, labels(post), u.username, canon_book, u.id,
            CASE WHEN lr IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
            CASE WHEN u.id = $user_id THEN true ELSE false END AS posted_by_current_user,
            count(comments) as num_comments,
            count(nl) as num_likes,
            collect(award_long) as awards
            order by post.created_date desc
            skip $skip
            limit $limit
            """
        )
        
        query_w_filter = (
            """
            MATCH (cu:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (b)-[club_reading:IS_READING]->(book:BookClubBook)
            MATCH (cu)-[user_reading:IS_READING_FOR_CLUB]->(book:BookClubBook)
            MATCH (post:ClubUpdate|ClubUpdateNoText {deleted:false})-[:POST_FOR_CLUB_BOOK]->(book)
            WHERE post.chapter <= user_reading.current_chapter
            match (post)<-[pr:POSTED]-(u:User)
            optional match (cu)-[lr:LIKES]->(post)
            optional match (book)-[br:IS_EQUIVALENT_TO]-(canon_book:Book)
            optional match (comments:Comment {deleted:false})<-[:HAS_COMMENT]-(post)
            optional match (post)<-[:AWARD_FOR_POST]-(post_award:ClubAwardForPost)
            optional match award_long = (award_user:User)-[:GRANTED]->(post_award)-[:IS_CHILD_OF]->(award:ClubAward)
            RETURN post, labels(post), u.username, canon_book, u.id, user_reading.current_chapter,
            CASE WHEN lr IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
            CASE WHEN u.id = $user_id THEN true ELSE false END AS posted_by_current_user,
            post.likes as num_likes,
            count(comments) as num_comments,
            collect(award_long) as awards
            order by post.created_date desc
            skip $skip
            limit $limit
            """
        )
    
        if filter:
            result = tx.run(
                query_w_filter,
                book_club_id=book_club_id,
                user_id=user_id,
                skip=skip,
                limit=limit
            )
        else:
            result = tx.run(
                query,
                book_club_id=book_club_id,
                user_id=user_id,
                skip=skip,
                limit=limit
            )
        
        posts = []           

        for response in result:
            book = BookPreview(
                id=response['canon_book'].get("id"),
                title=response['canon_book'].get("title"),
                small_img_url=response['canon_book'].get("small_img_url"),
                google_id=response['canon_book'].get("google_id")
            )

            awards = {}
            if response.get("awards"):
                for award in response.get("awards"):
                    _user_id = award.start_node['id']
                    parent_award = award.end_node
                    cls = AWARD_CONSTANTS.get(parent_award.get("name"))
                    parent_award_id = parent_award.get("id")
                    if parent_award_id not in awards:
                        awards[parent_award_id] = {
                            "name": parent_award.get("name",""),
                            "type": parent_award.get("type",""),
                            "description": parent_award.get("description",""),
                            "num_grants": 1,
                            "cls": cls,
                            "granted_by_current_user": False,
                        }
                    else:
                        awards[parent_award_id]['num_grants'] += 1

                    if user_id == _user_id:
                        awards[parent_award_id]['granted_by_current_user'] = True

            if response.get("labels(post)") == ["ClubUpdate"]:
                post = BookClubSchemas.UpdatePost(
                    id=response['post'].get("id"),
                    headline=response['post'].get("headline", ""),
                    response=response['post'].get("response"),
                    quote=response['post'].get("quote"),
                    chapter=response['post'].get("chapter"),
                    created_date=response['post'].get("created_date"),
                    user_id=response.get("u.id"),
                    user_username=response.get("u.username"),
                    liked_by_current_user=response.get("liked_by_current_user"),
                    likes=response.get("num_likes"),
                    posted_by_current_user=response.get("posted_by_current_user"),
                    num_comments=response.get("num_comments"),
                    book=book,
                    awards=awards
                )

            elif response.get("labels(post)") == ["ClubUpdateNoText"]:
                post = BookClubSchemas.UpdatePostNoText(
                    id=response['post'].get("id"),
                    chapter=response['post'].get("chapter"),
                    created_date=response['post'].get("created_date"),
                    user_id=response.get("u.id"),
                    user_username=response.get("u.username"),
                    liked_by_current_user=response.get("liked_by_current_user"),
                    posted_by_current_user=response.get("posted_by_current_user"),
                    num_comments=response.get("num_comments"),
                    book=book,
                    awards=awards
                )

            posts.append(post)
            
        return posts
    
    def get_book_club_finished_feed(
            self,
            book_club_id: str,
            user_id: str,
            skip: int,
            limit: int
    ) -> List[BookClubSchemas.UpdatePost]:
        """
        Gets the book club feed for the user
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_book_club_finished_feed_query, 
                book_club_id, 
                user_id,
                skip,
                limit
            )
        return result
    
    @staticmethod
    def get_book_club_finished_feed_query(
        tx,
        book_club_id: str,
        user_id: str,
        skip: int,
        limit: int
    ):
        
        query = (
            """
            MATCH (cu:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (b)-[:IS_READING]->(book:BookClubBook)
            MATCH (cu)-[:FINISHED_READING_FOR_CLUB]->(book)
            MATCH (post {deleted:false})-[:POST_FOR_CLUB_BOOK]->(book)
            WHERE post:ClubUpdate OR post:ClubUpdateNoText or post:ClubReview or post:ClubReviewNoText
            match (post)<-[pr:POSTED]-(u:User)
            optional match (cu)-[lr:LIKES]->(post)
            optional match (any)-[nl:LIKES]->(post)
            optional match (book)-[br:IS_EQUIVALENT_TO]-(canon_book:Book)
            optional match (comments:Comment {deleted:false})<-[:HAS_COMMENT]-(post)
            optional match (post)<-[:AWARD_FOR_POST]-(post_award:ClubAwardForPost)
            optional match award_long = (award_user:User)-[:GRANTED]->(post_award)-[:IS_CHILD_OF]->(award:ClubAward)
            RETURN post, labels(post), u.username, canon_book, u.id,
            CASE WHEN lr IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
            CASE WHEN u.id = $user_id THEN true ELSE false END AS posted_by_current_user,
            count(comments) as num_comments,
            count(nl) as num_likes,
            collect(award_long) as awards
            order by post.created_date desc
            skip $skip
            limit $limit
            """
        )
    
        result = tx.run(
            query,
            book_club_id=book_club_id,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        posts = []           

        for response in result:
            book = BookPreview(
                id=response['canon_book'].get("id"),
                title=response['canon_book'].get("title"),
                small_img_url=response['canon_book'].get("small_img_url"),
                google_id=response['canon_book'].get("google_id")
            )

            awards = {}
            if response.get("awards"):
                for award in response.get("awards"):
                    _user_id = award.start_node['id']
                    parent_award = award.end_node
                    cls = AWARD_CONSTANTS.get(parent_award.get("name"))
                    parent_award_id = parent_award.get("id")
                    if parent_award_id not in awards:
                        awards[parent_award_id] = {
                            "name": parent_award.get("name",""),
                            "type": parent_award.get("type",""),
                            "description": parent_award.get("description",""),
                            "num_grants": 1,
                            "cls": cls,
                            "granted_by_current_user": False,
                        }
                    else:
                        awards[parent_award_id]['num_grants'] += 1

                    if user_id == _user_id:
                        awards[parent_award_id]['granted_by_current_user'] = True

            if response.get("labels(post)") == ["ClubUpdate"]:
                post = BookClubSchemas.UpdatePost(
                    id=response['post'].get("id"),
                    headline=response['post'].get("headline", ""),
                    response=response['post'].get("response"),
                    quote=response['post'].get("quote"),
                    chapter=response['post'].get("chapter"),
                    created_date=response['post'].get("created_date"),
                    user_id=response.get("u.id"),
                    user_username=response.get("u.username"),
                    liked_by_current_user=response.get("liked_by_current_user"),
                    likes=response.get("num_likes"),
                    posted_by_current_user=response.get("posted_by_current_user"),
                    num_comments=response.get("num_comments"),
                    book=book,
                    awards=awards
                )

            elif response.get("labels(post)") == ["ClubUpdateNoText"]:
                post = BookClubSchemas.UpdatePostNoText(
                    id=response['post'].get("id"),
                    chapter=response['post'].get("chapter"),
                    created_date=response['post'].get("created_date"),
                    user_id=response.get("u.id"),
                    user_username=response.get("u.username"),
                    liked_by_current_user=response.get("liked_by_current_user"),
                    likes=response.get("num_likes"),
                    posted_by_current_user=response.get("posted_by_current_user"),
                    num_comments=response.get("num_comments"),
                    book=book,
                    awards=awards
                )
                
            elif response.get("labels(post)") == ["ClubReview"]:
                post = BookClubSchemas.ReviewPost(
                    id=response['post'].get("id"),
                    created_date=response['post'].get("created_date"),
                    user_id=response.get("u.id"),
                    user_username=response.get("u.username"),
                    likes=response.get("num_likes"),
                    liked_by_current_user=response.get("liked_by_current_user"),
                    posted_by_current_user=response.get("posted_by_current_user"),
                    num_comments=response.get("num_comments"),
                    headline=response['post'].get('headline'),
                    questions=response['post'].get('questions'),
                    question_ids=response['post'].get('question_ids'),
                    responses=response['post'].get('responses'),
                    rating=response['post'].get('rating'),
                    book=book,
                    awards=awards
                )
                
            elif response.get("labels(post)") == ["ClubReviewNoText"]:
                post = BookClubSchemas.ReviewPostNoText(
                    id=response['post'].get("id"),
                    created_date=response['post'].get("created_date"),
                    user_id=response.get("u.id"),
                    user_username=response.get("u.username"),
                    likes=response.get("num_likes"),
                    liked_by_current_user=response.get("liked_by_current_user"),
                    posted_by_current_user=response.get("posted_by_current_user"),
                    num_comments=response.get("num_comments"),
                    rating=response['post'].get('rating'),
                    book=book,
                    awards=awards
                )

            posts.append(post)
            
        return posts

    def get_awards(
            self,
            book_club_id: str,
            user_id: str,
            current_uses: bool
    ) -> List:
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_awards_query, 
                book_club_id,
                user_id,
                current_uses
            )
        return result

    @staticmethod
    def get_awards_query(
            tx,
            book_club_id: str,
            user_id: str,
            current_uses: bool
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (club)-[:IS_READING]->(book:BookClubBook)
            MATCH (award:ClubAward)-[award_rel:AWARD_FOR_BOOK]->(book)
            RETURN award,
                   award_rel.grants_per_member as allowed_uses
            """
        )

        query_w_current_uses = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (club)-[:IS_READING]->(book:BookClubBook)
            MATCH (award:ClubAward)-[award_rel:AWARD_FOR_BOOK]->(book)
            OPTIONAL MATCH (award)<-[:IS_CHILD_OF]-(post_award:ClubAwardForPost)<-[:GRANTED]-(u)
            RETURN award,
                   award_rel.grants_per_member as allowed_uses,
                   count(post_award) as current_uses
            """
        )

        if current_uses:
            result = tx.run(
                query_w_current_uses,
                book_club_id=book_club_id,
                user_id=user_id
            )
        else:
            result = tx.run(
                query,
                book_club_id=book_club_id,
                user_id=user_id
            )
        
        awards = []
        for response in result:
            award_response = response['award']
            awards.append(
                BookClubSchemas.Award(
                    id=award_response['id'],
                    name=award_response['name'],
                    type=award_response.get('type'),
                    description=award_response.get('description'),
                    allowed_uses=response.get('allowed_uses'),
                    current_uses=response.get('current_uses')
                )
            )

        return awards
                
    def get_awards_with_grants(
            self,
            book_club_id: str,
            user_id: str,
            current_uses: bool,
            post_id: str
    ) -> List:
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_awards_with_grants_query, 
                book_club_id,
                user_id,
                current_uses,
                post_id
            )
        return result

    @staticmethod
    def get_awards_with_grants_query(
            tx,
            book_club_id: str,
            user_id: str,
            current_uses: bool,
            post_id: str
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (club)-[:IS_READING]->(book:BookClubBook)
            MATCH (award:ClubAward)-[award_rel:AWARD_FOR_BOOK]->(book)
            OPTIONAL MATCH (post:ClubUpdate|ClubUpdateNoText {id:$post_id})
                <-[:AWARD_FOR_POST]-(post_award)
                -[:IS_CHILD_OF]->(award)
            OPTIONAL MATCH (post_award)<-[:GRANTED]-(grant_user:User)
            RETURN award,
                   award_rel.grants_per_member as allowed_uses,
                   collect({post_award: post_award, grant_user: grant_user}) AS post_awards
            """
        )

        query_w_current_uses = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (club)-[:IS_READING]->(book:BookClubBook)
            MATCH (award:ClubAward)-[award_rel:AWARD_FOR_BOOK]->(book)
            OPTIONAL MATCH (award)<-[:IS_CHILD_OF]-(user_grants:ClubAwardForPost)<-[:GRANTED]-(u)
            OPTIONAL MATCH (post:ClubUpdate|ClubUpdateNoText {id:$post_id})
                <-[:AWARD_FOR_POST]-(post_award)
                -[:IS_CHILD_OF]->(award)
            OPTIONAL MATCH (post_award)<-[:GRANTED]-(grant_user:User)
            WITH award, award_rel, user_grants, grant_user, post_award
            RETURN award,
                   award_rel.grants_per_member as allowed_uses,
                   count(user_grants) as current_uses,
                   collect({post_award: post_award, grant_user: grant_user}) AS post_awards
            """
        )

        if current_uses:
            result = tx.run(
                query_w_current_uses,
                book_club_id=book_club_id,
                user_id=user_id,
                post_id=post_id
            )
        else:
            result = tx.run(
                query,
                book_club_id=book_club_id,
                user_id=user_id,
                post_id=post_id
            )
        awards = []
        for response in result:
            award_response = response['award']
            cls = AWARD_CONSTANTS.get(award_response['name'])
            award = BookClubSchemas.AwardWithGrants(
                    id=award_response['id'],
                    name=award_response['name'],
                    type=award_response.get('type'),
                    description=award_response.get('description'),
                    allowed_uses=response.get('allowed_uses'),
                    current_uses=response.get('current_uses'),
                    grants=[],
                    cls=cls
                )
            for grant in response.get("post_awards",[]):
                if grant.get("post_award"):
                    award.grants.append(
                        {
                            "granted_date":grant.get("post_award").get("created_date").to_native(),
                            "user": {
                                "id": grant.get("grant_user").get("id"),
                                "username":  grant.get("grant_user").get("username")
                            }
                        }
                    )
            awards.append(award)


        return awards

    def get_book_club_name_and_current_book(
            self,
            book_club_id: str    
        ):
        """
        Get the name of the book club and the current book being read
        
        Args:
            book_club_id (str): The id of the book club

        Returns:
            {
                book_club_name (str): The name of the book club
                current_book (BookPreview): The current book being read
            }
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_book_club_name_and_current_book_query, 
                book_club_id
            )
        return result
    
    @staticmethod
    def get_book_club_name_and_current_book_query(
        tx,
        book_club_id: str
    ):
        query = (
            """
            MATCH (b:BookClub {id: $book_club_id})
            OPTIONAL MATCH (b)-[:IS_READING]->(book:BookClubBook)
            OPTIONAL MATCH (book)-[:IS_EQUIVALENT_TO]-(actual_book:Book)
            RETURN b.name as book_club_name,
                   actual_book.id as book_id,
                   actual_book.title as book_title,
                   actual_book.small_img_url as book_small_img_url,
                   actual_book.author_names as book_author_names
            """
        )

        result = tx.run(
            query,
            book_club_id=book_club_id
        )

        response = result.single()

        if not response:
            return {
                "book_club_name": None,
                "current_book": None
            }

        if response.get("book_id"):
            book = BookPreview(
                id=response.get("book_id"),
                title=response.get("book_title"),
                small_img_url=response.get("book_small_img_url")
            )

            return {
                "book_club_name": response.get("book_club_name"),
                "current_book": book
            }
        else:
            return {
                "book_club_name": response.get("book_club_name"),
                "current_book": None
            }
        
    def get_currently_reading_book_or_none(
        self,
        user_id: str,
        book_club_id: str,
    ):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_currently_reading_book_or_none_query,
                user_id=user_id,
                book_club_id=book_club_id,
            )
        return result
    
    @staticmethod
    def get_currently_reading_book_or_none_query(tx, user_id, book_club_id):
        query = """
        MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(bc:BookClub {id: $book_club_id})
        OPTIONAL MATCH (bc)-[:IS_READING]->(currentlyReadingBook:BookClubBook)
        OPTIONAL MATCH (currentlyReadingBook)-[:IS_EQUIVALENT_TO]-(actualCurrentlyReadingBook:Book)
        WITH bc, 
            currentlyReadingBook, 
            actualCurrentlyReadingBook, 
            u
        OPTIONAL MATCH (bc)-[:FINISHED_READING]->(finishedBook:BookClubBook)
        WHERE currentlyReadingBook IS NULL
        WITH bc, 
            currentlyReadingBook, 
            actualCurrentlyReadingBook, 
            finishedBook
        ORDER BY finishedBook.last_updated DESC
        WITH bc, 
            currentlyReadingBook, 
            actualCurrentlyReadingBook, 
            head(collect(finishedBook)) AS latestFinishedBook
        OPTIONAL MATCH (latestFinishedBook)-[:IS_EQUIVALENT_TO]-(actualFinishedBook:Book)
        RETURN 
        coalesce(actualCurrentlyReadingBook.id, actualFinishedBook.id) AS book_id,
        bc.id AS book_club_id,
        coalesce(actualCurrentlyReadingBook.title, actualFinishedBook.title) AS title,
        coalesce(actualCurrentlyReadingBook.small_img_url, actualFinishedBook.small_img_url) AS small_img_url,
        coalesce(actualCurrentlyReadingBook.author_names, actualFinishedBook.author_names) AS author_names,
        coalesce(currentlyReadingBook.chapters, latestFinishedBook.chapters) AS chapters,
        coalesce(currentlyReadingBook.id, latestFinishedBook.id) AS book_club_book_id
        """

        result = tx.run(
            query,
            user_id=user_id,
            book_club_id=book_club_id,
        )

        if result:
            record = result.single()
            if record.get("book_id"):
                current_book = BookClubSchemas.BookClubCurrentlyReading(
                    book_id=record.get("book_id"),
                    title=record.get("title"),
                    small_img_url=record.get("small_img_url", ""),
                    author_names=record.get("author_names", []),
                    chapters=record.get("chapters", 0),
                    book_club_book_id=record.get("book_club_book_id")
                )
                return current_book
            else: 
                return None
        else:
            return "No book club found"
        
    def get_notifications_for_user_by_club(self, user_id:str):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_notifications_for_user_by_club_query,
                user_id=user_id,
            )
        return result
    
    @staticmethod
    def get_notifications_for_user_by_club_query(tx, user_id:str):
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (clubNotification:ClubNotification {dismissed: false})-[:NOTIFICATION_FOR_USER]->(u)
        OPTIONAL MATCH (clubNotification)-[:NOTIFICATION_FOR_CLUB]->(b:BookClub)
        OPTIONAL MATCH (sentBy:User)-[:CREATED_NOTIFICATION]->(clubNotification)
        OPTIONAL MATCH (b)-[:IS_READING]->(bcb:BookClubBook)-[:IS_EQUIVALENT_TO]->(book:Book)
        RETURN clubNotification.id as notification_id,
                book.title as currently_reading_book_for_club_title,
                clubNotification.notification_type as notification_type,
                clubNotification.created_date as created_date,
                sentBy.id as sent_by_id,
                sentBy.username as sent_by_username,
                b.id as book_club_id,
                b.name as book_club_name
        """

        result = tx.run(query, user_id=user_id)
        
        notifications = {}

        for response in result:
            club_id = response.get('book_club_id')
            notification = BookClubSchemas.ClubNotification(
                id=response.get('notification_id'),
                notification_type=response.get('notification_type'),
                created_date=response.get('created_date'),
                member_id=user_id,
                sent_by_user_id=response.get('sent_by_id'),
                sent_by_user_username=response.get('sent_by_username'),
                book_club_id=club_id,
                dismissed=False,
            )

            if not club_id in notifications:
                notifications[club_id] = {}
                notifications[club_id]['book_club_name'] = response.get('book_club_name')
                notifications[club_id]['currently_reading_book_title'] = response.get('currently_reading_book_for_club_title')
                notifications[club_id]['notifications'] = []

            notifications[club_id]['notifications'].append(notification)
        
        for key, _ in notifications.items():
           notifications[key]['notifications'] = sorted(
               notifications[key]['notifications'], key=lambda n: n.created_date
           )
           
        return notifications
    
    def get_notification_eligibility(
            self,
            notif: BookClubSchemas.ClubNotificationCreate
    ):
        """
        Returns true if the outgoing notification is eligible to be sent.
        Some criteria are:
            Too soon after the last notification
            Club has notifications disabled (future state)
            User has notifications disabled (future state)
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_notification_eligibility_query,
                notif
            )
        return result
    
    @staticmethod
    def get_notification_eligibility_query(
        tx, 
        notif: BookClubSchemas.ClubNotificationCreate
        ):
        query = (
            """
            Match (bc:BookClub {id: $book_club_id})<-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(sending_u:User {id: $sent_user_id})
            Match (bc)<-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(receiving_u:User {id: $receiving_user_id})
            OPTIONAL MATCH (receiving_u)<-[:NOTIFICATION_FOR_USER]-(notif:ClubNotification)-[:NOTIFICATION_FOR_CLUB]->(bc)
            WHERE notif.created_date > datetime() - duration('P1D')
            OPTIONAL MATCH (sending_u)-[:CREATED_NOTIFICATION]->(notif)
            return notif,
                   receiving_u.id as receiving_user_id
            """
        )

        result = tx.run(
            query,
            book_club_id=notif.book_club_id,
            sent_user_id=notif.sent_by_user_id,
            receiving_user_id=notif.member_id
        )

        # If this function returns nothing, the notification is ineligible
        # If a notification is returned, then we check if it was within the last 2 minutes
        # If it was, then the notification is ineligible

        eligible = False
        for response in result:
            if response.get("receiving_user_id"):
                eligible = True

            if response.get("notif"):
                if response.get("notif").get("created_date") > (datetime.now(timezone.utc) - timedelta(minutes=2)):
                    eligible = False
                    break
        return eligible
    
    def get_afterward_user_stats(
        self,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_afterward_user_stats_query,
                book_club_id,
                book_club_book_id,
                user_id
            )
        return result

    @staticmethod
    def get_afterward_user_stats_query(
        tx,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[fr:FINISHED_READING]->(book:BookClubBook {id: $book_club_book_id})
            MATCH (u)-[:POSTED]->(post:ClubUpdate|ClubUpdateNoText)-[:POST_FOR_CLUB_BOOK]->(book)
            WITH u, book, fr, COUNT(post) as num_updates
            MATCH (u)-[:GRANTED]->(award:ClubAwardForPost)
                -[:AWARD_FOR_POST]->()-[:POST_FOR_CLUB_BOOK]->(book)
            WITH u, book, fr, num_updates, COUNT(award) as num_awards
            MATCH (u)-[u_fr:FINISHED_READING_FOR_CLUB]->(book)
            RETURN num_updates,
                   num_awards,
                   fr.started_date as start_date,
                   u_fr.last_updated as finish_date
            """
        )
        result = tx.run(
            query,
            book_club_id=book_club_id,
            book_club_book_id=book_club_book_id,
            user_id=user_id
        )
        
        response = result.single()
        
        if not response:
            return
        
        start_date = response.get("start_date")
        finish_date = response.get("finish_date")
        
        days = (finish_date - start_date).days
        
        print(days)
        
        return {
            "days":days,
            "updates": response.get("num_updates"),
            "awards": response.get("num_awards")
        }
    
    def get_afterward_friend_thoughts(
        self,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_afterward_friend_thoughts_query,
                book_club_id,
                book_club_book_id,
                user_id
            )
        return result

    @staticmethod
    def get_afterward_friend_thoughts_query(
        tx,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[fr:FINISHED_READING]->(book:BookClubBook {id: $book_club_book_id})
            MATCH (member:User)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b)
            MATCH (member)-[:POSTED]->(review:ClubReview|ClubReviewNoText)-[:POST_FOR_CLUB_BOOK]->(book)
            RETURN member.id as user_id,
                   member.username as user_username,
                   review.headline as headline,
                   review.rating as rating
            """
        )
        result = tx.run(
            query,
            book_club_id=book_club_id,
            book_club_book_id=book_club_book_id,
            user_id=user_id
        )
        
        thoughts = [
            {
                "user":{
                    "id": response['user_id'],
                    "username": response["user_username"],
                    "is_current_user": response['user_id'] == user_id
                },
                "review":{
                    "headline": response.get("headline"),
                    "rating": response.get("rating")
                }
            }
            for response in result
        ]

        return thoughts
    
    def get_afterward_consensus(
        self,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_afterward_consensus_query,
                book_club_id,
                book_club_book_id,
                user_id
            )
        return result

    @staticmethod
    def get_afterward_consensus_query(
        tx,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[fr:FINISHED_READING]->(books:BookClubBook)
            MATCH (member:User)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b)
            OPTIONAL MATCH (member)-[:POSTED]->(review:ClubReview|ClubReviewNoText)-[:POST_FOR_CLUB_BOOK]->(books)
            RETURN books.id as book_club_book_id,
            collect({
                        user_id: member.id,
                        user_username: member.username,
                        rating: review.rating
                    }) AS reviews
            limit 5
            """
        )
        result = tx.run(
            query,
            book_club_id=book_club_id,
            user_id=user_id
        )

        loved = []
        liked = []
        disliked = []
        current_user_rating = None
        total_is_same_as_longest = 0

        for response in result:
            book_loved = []
            book_liked = []
            book_disliked = []
            if response.get("book_club_book_id") == book_club_book_id:
                for review in response.get("reviews",[]):
                    rating = review.get("rating")

                    if review.get("user_id") == user_id:
                        current_user_rating = rating
                        
                    # Skip users who have not reviewed
                    if not rating:
                        continue

                    if rating == 2:
                        loved.append(
                            {
                                "user":{
                                    "id": review.get("user_id"),
                                    "username": review.get("user_username"),
                                }
                            }
                        )
                    elif rating == 1:
                        liked.append(
                            {
                                "user":{
                                    "id": review.get("user_id"),
                                    "username": review.get("user_username"),
                                }
                            }
                        )
                    else:
                        disliked.append(
                            {
                                "user":{
                                    "id": review.get("user_id"),
                                    "username": review.get("user_username"),
                                }
                            }
                        )

                rating_groups = {
                    2: loved,
                    1: liked,
                    0: disliked
                }

                # Find the rating corresponding to the longest array
                longest_rating = max(rating_groups, key=lambda rating: len(rating_groups[rating]))

                # Compare the current_user_rating with the longest_rating
                is_same_as_longest = current_user_rating == longest_rating

                if is_same_as_longest:
                    total_is_same_as_longest += 1

            else:
                for review in response.get("reviews",[]):
                    rating = review.get("rating")

                    if review.get("user_id") == user_id:
                        book_current_user_rating = rating
                    # Skip users who have not reviewed
                    if not rating:
                        continue

                    if rating == 2:
                        book_loved.append(
                            {
                                "user":{
                                    "id": review.get("user_id"),
                                    "username": review.get("user_username"),
                                }
                            }
                        )
                    elif rating == 1:
                        book_liked.append(
                            {
                                "user":{
                                    "id": review.get("user_id"),
                                    "username": review.get("user_username"),
                                }
                            }
                        )
                    else:
                        book_disliked.append(
                            {
                                "user":{
                                    "id": review.get("user_id"),
                                    "username": review.get("user_username"),
                                }
                            }
                        )
                
                rating_groups = {
                    2: book_loved,
                    1: book_liked,
                    0: book_disliked
                }

                # Find the rating corresponding to the longest array
                book_longest_rating = max(rating_groups, key=lambda rating: len(rating_groups[rating]))

                # Compare the current_user_rating with the longest_rating
                book_is_same_as_longest = book_current_user_rating == book_longest_rating

                if book_is_same_as_longest:
                    total_is_same_as_longest += 1


        longest_rating_map = ["disliked","liked","loved"]
        longest_rating_text = longest_rating_map[longest_rating]

        if is_same_as_longest:
            num_times_result = total_is_same_as_longest
        else:
            num_times_result = 5 - total_is_same_as_longest

        return {
            "loved":loved,
            "liked":liked,
            "disliked":disliked,
            "group_consensus":{
                "majority": longest_rating_text,
                "user_agreed_with_majority": is_same_as_longest,
                "num_times_result": num_times_result
            }
        }        
    
    def get_afterward_highlights(
            self,
            book_club_id: str,
            book_club_book_id: str,
            user_id: str
            ):
        
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_afterward_highlights_query,
                book_club_id,
                book_club_book_id,
                user_id
            )
        return result

    @staticmethod
    def get_afterward_highlights_query(
        tx,
        book_club_id: str,
        book_club_book_id: str,
        user_id: str
    ):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[fr:FINISHED_READING]->(book:BookClubBook {id: $book_club_book_id})
            MATCH (u)-[:POSTED]->(post:ClubUpdate|ClubUpdateNoText)-[:POST_FOR_CLUB_BOOK]->(book)
            OPTIONAL MATCH (award:ClubAward {type: 'Commendable'})<-[:IS_CHILD_OF]-(post_award:ClubAwardForPost)-[:AWARD_FOR_POST]->(post)
            WITH post, 
                 COUNT(post_award) AS commendable_award_count, 
                 COLLECT({
                    id: award.id,
                    name: award.name,
                    type: award.type,
                    description: award.description
                 }) as commendable_awards
            ORDER BY commendable_award_count DESC
            LIMIT 1
            WITH collect(
                {post: post, 
                commendable_awards: commendable_awards,
                commendable_award_count: commendable_award_count
                }) AS top_commendable_posts

            MATCH (u:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[:FINISHED_READING]->(book:BookClubBook {id: $book_club_book_id})
            MATCH (u)-[:POSTED]->(post:ClubUpdate|ClubUpdateNoText)-[:POST_FOR_CLUB_BOOK]->(book)
            OPTIONAL MATCH (award:ClubAward {type: 'Questionable'})<-[:IS_CHILD_OF]-(post_award:ClubAwardForPost)-[:AWARD_FOR_POST]->(post)
            WITH top_commendable_posts, 
                 post, 
                 COUNT(post_award) AS questionable_award_count,
                 COLLECT({
                    id: award.id,
                    name: award.name,
                    type: award.type,
                    description: award.description
                 }) as questionable_awards
            ORDER BY questionable_award_count DESC
            LIMIT 1
            RETURN top_commendable_posts, 
                   collect({
                        post: post, 
                        questionable_awards: questionable_awards,
                        questionable_award_count: questionable_award_count
                        }) AS top_questionable_posts
            """
        )

        result = tx.run(
            query,
            book_club_id=book_club_id,
            book_club_book_id=book_club_book_id,
            user_id=user_id
        )

        response = result.single()
        
        top_commendable_posts = response.get("top_commendable_posts") 
        if top_commendable_posts:
            top_commendable_post = top_commendable_posts[0]
            top_commendable_post_obj = top_commendable_post.get("post")

            awards = {}
            if top_commendable_post.get("commendable_awards") and top_commendable_post.get("commendable_award_count"):
                for award in top_commendable_post.get("commendable_awards"):
                    cls = AWARD_CONSTANTS.get(award.get("name"))
                    parent_award_id = award.get("id")
                    if parent_award_id not in awards:
                        awards[parent_award_id] = {
                            "name": award.get("name",""),
                            "type": award.get("type",""),
                            "description": award.get("description",""),
                            "num_grants": 1,
                            "cls": cls
                        }
                    else:
                        awards[parent_award_id]['num_grants'] += 1

            agreed_post = {
                "id": top_commendable_post_obj['id'],
                "created_date": top_commendable_post_obj['created_date'].to_native(),
                "headline": top_commendable_post_obj.get("headline"),
                "response": top_commendable_post_obj.get("response"),
                "likes": top_commendable_post_obj.get("likes",0),
                "awards": awards
            }

        else:
            agreed_post = {}

        top_questionable_posts = response.get("top_questionable_posts") 
        if top_questionable_posts:
            top_questionable_post = top_questionable_posts[0]
            top_questionable_post_obj = top_questionable_post.get("post")

            awards = {}
            if top_questionable_post.get("questionable_awards") and top_questionable_post.get("questionable_award_count"):
                for award in top_questionable_post.get("questionable_awards"):
                    cls = AWARD_CONSTANTS.get(award.get("name"))
                    parent_award_id = award.get("id")
                    if parent_award_id not in awards:
                        awards[parent_award_id] = {
                            "name": award.get("name",""),
                            "type": award.get("type",""),
                            "description": award.get("description",""),
                            "num_grants": 1,
                            "cls": cls
                        }
                    else:
                        awards[parent_award_id]['num_grants'] += 1

            controversial_post = {
                "id": top_questionable_post_obj['id'],
                "created_date": top_questionable_post_obj['created_date'].to_native(),
                "headline": top_questionable_post_obj.get("headline"),
                "response": top_questionable_post_obj.get("response"),
                "likes": top_questionable_post_obj.get("likes",0),
                "awards": awards
            }

        else:
            controversial_post = {}

        print(agreed_post)
        print(controversial_post)

        return {
            "agreed_post": agreed_post,
            "controversial_post": controversial_post
        }

        
    def search_users_not_in_club(
            self, 
            search_param: BookClubSchemas.BookClubInviteSearch
        ) -> None:
        """
        Searches for users not in the club

        Args:
            search_param (BookClubSchemas.BookClubInviteSearch): The search 
            parameters
        
        Returns:
            users: an array of users that match the search string. User 
            information contains:
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
        CALL db.index.fulltext.queryNodes('userFullText', $search_query + "*")
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
    
    
    def update_accept_book_club_invite(
            self,
            invite: BookClubSchemas.BookClubInviteResponse
    ) -> bool:
        """
        Accepts the book club invite

        Args:
            invite (BookClubSchemas.BookClubInviteResponse): The invite 
            response
        
        Returns:
            True if the invite was accepted, False otherwise
        """
        with self.driver.session() as session:
            result = session.write_transaction(
                self.update_accept_book_club_invite_query, 
                invite)
        return result
    
    @staticmethod
    def update_accept_book_club_invite_query(
        tx,
        invite: BookClubSchemas.BookClubInviteResponse
        ) -> bool:

        query = (
            """
            MATCH (u:User {id: $user_id})-[:RECEIVED_INVITE]->(i:BookClubInvite {id: $invite_id})-[:INVITE_FOR]->(b:BookClub)
            OPTIONAL MATCH (b)-[:IS_READING]->(book:BookClubBook)
            MERGE (u)-[:IS_MEMBER_OF]->(b)
            FOREACH (_ IN CASE WHEN book IS NOT NULL THEN [1] ELSE [] END |
                MERGE (u)-[reading:IS_READING_FOR_CLUB]->(book)
                ON CREATE SET 
                    reading.last_updated = datetime(),
                    reading.current_chapter = 0
            )
            DETACH DELETE i
            RETURN count(i) as deleted
            """
        )

        result = tx.run(
            query,
            user_id=invite.user_id,
            invite_id=invite.invite_id
        )

        response = result.single()
        if response["deleted"] == 1:
            return True
        else:
            return False
        
    def update_decline_book_club_invite(
            self,
            invite: BookClubSchemas.BookClubInviteResponse
    ) -> bool:
        """
        declines the book club invite

        Args:
            invite (BookClubSchemas.BookClubInviteResponse): The invite
            response
        
        Returns:
            True if the invite was declined, False otherwise
        """
        with self.driver.session() as session:
            result = session.write_transaction(
                self.update_decline_book_club_invite_query, 
                invite)
        return result
    
    @staticmethod
    def update_decline_book_club_invite_query(
        tx,
        invite: BookClubSchemas.BookClubInviteResponse
        ) -> bool:

        query = (
            """
            MATCH (u:User {id: $user_id})-[:RECEIVED_INVITE]->(i:BookClubInvite {id: $invite_id})-[:INVITE_FOR]->(b:BookClub)
            DETACH DELETE i
            RETURN count(i) as deleted
            """
        )

        result = tx.run(
            query,
            user_id=invite.user_id,
            invite_id=invite.invite_id
        )

        response = result.single()
        if response["deleted"] == 1:
            return True
        else:
            return False
        
    def update_finished_reading(
        self,
        book_club_id: str,
        user_id: str
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.update_finished_reading_query, 
                book_club_id,
                user_id)
        return result
    
    @staticmethod
    def update_finished_reading_query(
        tx,
        book_club_id: str,
        user_id: str
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[reading:IS_READING]->(bc_book:BookClubBook)
            CREATE (b)-[finished:FINISHED_READING {
                started_date: reading.started_date,
                selected_finish_date: reading.selected_finish_date,
                actual_finish_date: datetime()
            }]->(bc_book)
            DELETE reading
            RETURN bc_book.id as book_id
            """
        )

        result = tx.run(
            query,
            user_id=user_id,
            book_club_id=book_club_id
        )

        response=result.single()
        return response.get("book_id") is not None
    
    def update_stopped_reading(
        self,
        book_club_id: str,
        user_id: str
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.update_stopped_reading_query, 
                book_club_id,
                user_id)
        return result
    
    @staticmethod
    def update_stopped_reading_query(
        tx,
        book_club_id: str,
        user_id: str
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:OWNS_BOOK_CLUB]->(b:BookClub {id:$book_club_id})
            MATCH (b)-[reading:IS_READING]->(bc_book:BookClubBook)
            CREATE (b)-[stopped:STOPPED_READING {
                started_date: reading.started_date,
                selected_finish_date: reading.selected_finish_date,
                actual_finish_date: datetime()
            }]->(bc_book)
            WITH bc_book, reading
            MATCH (member:User)-[member_reading:IS_READING_FOR_CLUB]->(bc_book)
            CREATE (member)-[member_stopped:STOPPED_READING_FOR_CLUB {
                last_updated: member_reading.last_updated,
                current_chapter: member_reading.current_chapter
            }]->(bc_book)
            DELETE reading, member_reading
            RETURN bc_book.id as book_id
            """
        )

        result = tx.run(
            query,
            user_id=user_id,
            book_club_id=book_club_id
        )

        response=result.single()
        return response.get("book_id") is not None
    
    def delete_book_club_data(
        self,
        user_id: str
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.delete_book_club_data_query,
                user_id)
        return result
    
    @staticmethod
    def delete_book_club_data_query(
        tx,
        user_id: str
    ):
        query = (
            """
            MATCH (user:User {id:$user_id})-[:OWNS_BOOK_CLUB]->(b:BookClub)
            OPTIONAL MATCH (b)-[:HAS_PACE]->(pace:BookClubPace)
            OPTIONAL MATCH (b)-[]->(book:BookClubBook)
            OPTIONAL MATCH (b)-[]-(invites:BookClubInvite)
            OPTIONAL MATCH (invites)-[]-(test_emails:InvitedUser)
            OPTIONAL MATCH (user)-[]-(awards:ClubAwardForPost)
            OPTIONAL MATCH (b)-[]-(posts:ClubUpdate|ClubUpdateNoText|ClubReview|ClubReviewNoText)
            DETACH DELETE pace, book, b, invites, test_emails, awards, posts
            return user.id as user_id
            """
        )

        result = tx.run(
            query,
            user_id=user_id
        )

        response = result.single()
        return response.get("user_id") is not None
    
    def delete_award_for_post(
            self,
            delete_award: BookClubSchemas.DeleteAward
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.delete_award_for_post_query, 
                delete_award
            )
        return result
    
    @staticmethod
    def delete_award_for_post_query(
        tx,
        delete_award: BookClubSchemas.DeleteAward
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (club)-[:IS_READING]->(book:BookClubBook)
            MATCH (book)<-[award_rel:AWARD_FOR_BOOK]-(award:ClubAward {id:$award_id})
            MATCH (post:ClubUpdate|ClubUpdateNoText {id:$post_id})-[:POST_FOR_CLUB_BOOK]->(book)
            MATCH (u)-[:GRANTED]->(club_award:ClubAwardForPost)-[:IS_CHILD_OF]->(award)
            DETACH DELETE club_award
            RETURN award.id as award_id
            """
        )

        result = tx.run(
            query,
            user_id=delete_award.user_id,
            book_club_id=delete_award.book_club_id,
            award_id=delete_award.award_id,
            post_id=delete_award.post_id
        )

        response = result.single()

        if response.get("award_id"):
            return True
        else:
            return False
        
    def delete_award_for_post_by_id(
            self,
            delete_award: BookClubSchemas.DeleteAward
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.delete_award_for_post_by_id_query, 
                delete_award
            )
        return result
    
    @staticmethod
    def delete_award_for_post_by_id_query(
        tx,
        delete_award: BookClubSchemas.DeleteAward
    ):
        query = (
            """
            MATCH (u:User {id:$user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club:BookClub {id:$book_club_id})
            MATCH (u)-[:GRANTED]->(club_award:ClubAwardForPost {id:$award_id})
            DETACH DELETE club_award
            RETURN club.id as club_id
            """
        )

        result = tx.run(
            query,
            user_id=delete_award.user_id,
            book_club_id=delete_award.book_club_id,
            award_id=delete_award.award_id
        )

        response = result.single()

        if response.get("club_id"):
            return True
        else:
            return False
        
    def delete_member_from_book_club(
            self, 
            current_user_id:str, 
            member_id_to_remove:str, 
            book_club_id:str):
        """
        Removes a member from a book club. Can only be done by the owner of the 
        book club

        Args:
            current_user_id (str): The id of the user performing the action
            member_id_to_remove (str): The id of the user to remove
            book_club_id (str): The id of the book club to remove the user from

        Returns:
            bool: True if the user was removed, False otherwise
        """
        with self.driver.session() as session:
            result = session.write_transaction(
                self.delete_member_from_book_club_query, 
                current_user_id=current_user_id,
                member_id_to_remove=member_id_to_remove,
                book_club_id=book_club_id,
            )
        return result

    @staticmethod
    def delete_member_from_book_club_query(tx, current_user_id, member_id_to_remove, book_club_id) -> int:
        query = """
            MATCH (u:User {id: $current_user_id})-[:OWNS_BOOK_CLUB]-(bc:BookClub {id: $book_club_id})
            MATCH (bc)<-[rr:IS_MEMBER_OF]-(memberToRemove:User {id: $member_id_to_remove})
            OPTIONAL MATCH (memberToRemove)-[r:IS_READING_FOR_CLUB]->(book:BookClubBook)
            DELETE rr, r
            RETURN memberToRemove.id
        """
        
        result = tx.run(query,
            current_user_id=current_user_id,
            member_id_to_remove=member_id_to_remove,
            book_club_id=book_club_id
        )
        if result:
            return True
        else:
            return False
        
    def update_club_notification_to_dismissed(self, member_id:str, notification_id:str):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.update_club_notification_to_dismissed_query,
                member_id=member_id,
                notification_id=notification_id
            )
        return result
    
    @staticmethod
    def update_club_notification_to_dismissed_query(tx, member_id:str, notification_id:str) -> bool:
        query = """
            
        """