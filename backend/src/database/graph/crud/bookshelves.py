import datetime
from collections import Counter

from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.bookshelves import (
    Bookshelf, 
    MinimalBookshelf,
    BookshelfPage,
    BookshelfPreview, 
    BookshelfBook,
    BookshelfContributor,
    BookshelfMember,
    BookshelfFollower,
    CurrentlyReadingBookPreview,
    CurrentlyReadingBookshelfPreview,
    CurrentlyReadingUpdatePreview,
    CurrentlyReadingUpdateFilter,
    BookshelfProgressBar
)
from src.models.schemas.users import UserId

class BookshelfCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def get_bookshelf(self, bookshelf_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_bookshelf_query, bookshelf_id)
        return result
    
    @staticmethod
    def get_bookshelf_query(tx, bookshelf_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})
            OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(bb:Book)
            MATCH (u:User)-[r:HAS_BOOKSHELF_ACCESS]->(b)
            OPTIONAL MATCH (follower:User)-[follows_rel:FOLLOWS_SHELF]->(b)
            RETURN b.id as id, 
                   b.title as title, 
                   b.description as description, 
                   b.books as book_ids,
                   b.visibility as visibility,
                   b.img_url as img_url,
                   u as user,
                   r as access,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(follower.id) as followers,
                   collect(rr) as book_note_for_shelves
            """
        )

        result = tx.run(query, bookshelf_id=bookshelf_id)
        contributors = set()
        members = set()
        book_objects = []
      
        for record in result:
            if record["access"]["type"] == "owner":
                owner = record["user"]["id"]
                owner_username = record["user"]["username"]
                contributors.add(owner)
            elif record["access"]["type"] == "contributor":
                contributors.add(record["user"]["id"])
            elif record["access"]["type"] == "member":
                members.add(record["user"]["id"])


        book_map = {
        book_id: {
            'item': book,
            'description': note_for_shelf.get('note_for_shelf', None)
        }
        for book_id, book, note_for_shelf in zip(record["book_object_ids"], record["books"], record["book_note_for_shelves"])
}
        
        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=owner,
            created_by_username=owner_username,
            contributors=contributors,
            members=members,
            follower_count=len(record["followers"])
        )

        return bookshelf
    
    def get_bookshelves_created_by_user(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_bookshelves_created_by_user_query, user_id)
        return result
    
    @staticmethod
    def get_bookshelves_created_by_user_query(tx, user_id):
        query = (
            """
            MATCH (b:Bookshelf)<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            OPTIONAL MATCH (b)-[:CONTAINS_BOOK]->(bb:Book)
            OPTIONAL MATCH (uu:User)-[:HAS_BOOKSHELF_ACCESS {type: "member"}]->(b)
            OPTIONAL MATCH (follower:User)-[follows_rel:FOLLOWS_SHELF]->(b)
            RETURN b.id as id, 
                b.title as title, 
                b.description as description, 
                b.books as book_ids,
                b.visibility as visibility,
                b.img_url as img_url,
                b.created_by as created_by,
                u.username as created_by_username,
                count(bb) as book_count,
                count(uu) as member_count,
                count(follower) as follower_count,
                collect(bb.id) as book_object_ids,
                collect(bb.small_img_url) as book_img_urls
            """
        )

        result = tx.run(query, user_id=user_id)
        bookshelves = []
        for record in result:
            book_map = dict(zip(record["book_object_ids"], record["book_img_urls"]))
            first_four_books_imgs = []
            for key in record["book_ids"][:4]:
                first_four_books_imgs.append(book_map[key])
                
            bookshelf = BookshelfPreview(
                id=record["id"],
                title=record["title"],
                book_ids=record["book_ids"],
                description=record["description"],
                visibility=record["visibility"],
                img_url=record["img_url"],
                created_by=record["created_by"],
                created_by_username=record["created_by_username"],
                books_count=record["book_count"],
                book_img_urls=first_four_books_imgs,
                member_count=record["member_count"],
                follower_count=record["follower_count"]
            )
            bookshelves.append(bookshelf)
        return bookshelves
    
    def get_explore_bookshelves_for_user(self, user_id, skip, limit):
        """
        Get all public bookshelves that the user's friends have created, contributed to, are members of, or follow.
        """
        with self.driver.session() as session:
            result = session.read_transaction(self.get_explore_bookshelves_for_user_query, user_id, skip, limit)
        return result
    
    @staticmethod
    def get_explore_bookshelves_for_user_query(tx, user_id, skip, limit):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:FRIENDED {status:"friends"}]-(friend:User)
            MATCH (b:Bookshelf {visibility: "public"})<-[r:HAS_BOOKSHELF_ACCESS]-(friend)
            where not (b)-[:HAS_BOOKSHELF_ACCESS]-(u) and
            not (b)-[:FOLLOWS_SHELF]-(u) and 
            b.visibility = "public"
            with b, friend, r
            Match (b)-[:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(owner:User)
            OPTIONAL MATCH (b)-[:CONTAINS_BOOK]->(bb:Book)

            RETURN b as bookshelf,
                friend as friend,
                r as friend_access,
                collect(bb.id) as book_object_ids,
                collect(bb.small_img_url) as book_img_urls,
                count(bb) as book_count,
                owner.id as created_by,
                owner.username as created_by_username

            SKIP $skip
            LIMIT $limit
            """
        )
        result = tx.run(query, user_id=user_id, skip=skip, limit=limit)
        bookshelf_list = []
        
        for response in result:
            book_map = dict(zip(response["book_object_ids"], response["book_img_urls"]))
            first_four_books_imgs = []
            for key in response["bookshelf"]["books"][:4]:
                first_four_books_imgs.append(book_map[key])
                
            bookshelf = BookshelfPreview(
                id=response["bookshelf"]["id"],
                title=response["bookshelf"]["title"],
                book_ids=response["bookshelf"]["books"],
                description=response["bookshelf"]["description"],
                visibility=response["bookshelf"]["visibility"],
                img_url=response["bookshelf"]["img_url"],
                created_by=response["created_by"],
                created_by_username=response["created_by_username"],
                books_count=response["book_count"],
                book_img_urls=first_four_books_imgs,
                member_count=0,
                follower_count=0
            )
            
            bookshelf_list.append(bookshelf)
        
        return bookshelf_list

    def get_bookshelves_contributed_to_by_user(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_bookshelves_contributed_to_by_user_query, user_id)
        return result
    
    @staticmethod
    def get_bookshelves_contributed_to_by_user_query(tx, user_id):
        query = (
            """
            MATCH (b:Bookshelf)<-[r:HAS_BOOKSHELF_ACCESS {type: "contributor"}]-(u:User {id: $user_id})
            MATCH (owner:User)-[:HAS_BOOKSHELF_ACCESS {type: "owner"}]->(b)
            OPTIONAL MATCH (b)-[:CONTAINS_BOOK]->(bb:Book)
            OPTIONAL MATCH (uu:User)-[:HAS_BOOKSHELF_ACCESS {type: "member"}]->(b)
            OPTIONAL MATCH (follower:User)-[follows_rel:FOLLOWS_SHELF]->(b)
            RETURN b.id as id, 
                b.title as title, 
                b.description as description, 
                b.books as book_ids,
                b.visibility as visibility,
                b.img_url as img_url,
                b.created_by as created_by,
                owner.username as created_by_username,
                count(bb) as book_count,
                count(uu) as member_count,
                count(follower) as follower_count,
                collect(bb.id) as book_object_ids,
                collect(bb.small_img_url) as book_img_urls
            """
        )

        result = tx.run(query, user_id=user_id)
        bookshelves = []
        for record in result:
            book_map = dict(zip(record["book_object_ids"], record["book_img_urls"]))
            first_four_books_imgs = []
            for key in record["book_ids"][:4]:
                first_four_books_imgs.append(book_map[key])
                
            bookshelf = BookshelfPreview(
                id=record["id"],
                title=record["title"],
                book_ids=record["book_ids"],
                description=record["description"],
                visibility=record["visibility"],
                img_url=record["img_url"],
                created_by=record["created_by"],
                created_by_username=record["created_by_username"],
                books_count=record["book_count"],
                book_img_urls=first_four_books_imgs,
                member_count=record["member_count"],
                follower_count=record["follower_count"]
            )
            bookshelves.append(bookshelf)
        return bookshelves
    
    def get_minimal_shelves_for_user(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_minimal_shelves_for_user_query, user_id)
        return result

    @staticmethod
    def get_minimal_shelves_for_user_query(tx, user_id):
        query = (
            """
            MATCH (b:Bookshelf)<-[r:HAS_BOOKSHELF_ACCESS]-(u:User {id: $user_id})
            WHERE r.type IN ["owner", "contributor"]
            RETURN b.id as id,
                b.title as title,
                b.visibility as visibility
            """
        )
        result = tx.run(query, user_id=user_id)
        bookshelves = []
        for record in result:
            bookshelf = MinimalBookshelf(
                id=record["id"],
                title=record["title"],
                visibility=record["visibility"]
            )
            bookshelves.append(bookshelf)

        return bookshelves
    
    def get_update_previews_for_currently_reading_shelf_by_range(
            self, 
            update_filters: CurrentlyReadingUpdateFilter
        ):
        """Gets all the updates for a specific book within a range of pages any shelf.
        
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_update_previews_for_currently_reading_shelf_by_range_query,
                update_filters
            )
        return result
    
    @staticmethod
    def get_update_previews_for_currently_reading_shelf_by_range_query(
        tx, 
        update_filters: CurrentlyReadingUpdateFilter
    ):
        query = (
            """
            MATCH (p:Update {deleted:false})<-[pr:POSTED]-(u:User {id: $user_id})
            MATCH (p)-[br:POST_FOR_BOOK]-(b:Book {id: $book_id}) 
            WHERE p.page >= $starting_page_for_range AND p.page <= $end_of_range
            WITH p, COUNT(p) AS total_count
            ORDER BY p.page 
            LIMIT $updates_per_page
            RETURN 
                p.page,
                p.headline,
                p.id,
                p.created_date,
                total_count
            """
        )
        result = tx.run(query, 
            user_id=update_filters.user_id,
            book_id=update_filters.book_id,
            starting_page_for_range=update_filters.starting_page_for_range,
            end_of_range=update_filters.starting_page_for_range+update_filters.size_of_range,
            updates_per_page=update_filters.updates_per_page
        )
        
        updates = []
        for record in result:
            update = CurrentlyReadingUpdatePreview(
                id=record['p.id'],
                page=record.get('p.page', 0),
                headline=record.get('p.headline', ''),
                created_date=record['p.created_date'],
                user= UserId(id=update_filters.user_id)
            )
            updates.append(update)

        
        try:
            additional_updates_not_shown = max(record['total_count']-update_filters.updates_per_page, 0)
        except:
            additional_updates_not_shown = 0 

        return {
            "updates": updates,
            "additional_updates_not_shown": additional_updates_not_shown
        }

    def get_updates_progress_bar(
            self,
            user_id: str,
            book_id: str
    ):
        """
        Gets the progress bar for a specific book and user.
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                self.get_updates_progress_bar_query,
                user_id,
                book_id
            )
        return result
    
    @staticmethod
    def get_updates_progress_bar_query(tx, user_id, book_id):
        query = (
            """
            MATCH (b:Book {id: $book_id})
            OPTIONAL MATCH (b)<-[:POST_FOR_BOOK]-(p:Update {deleted:false})<-[pr:POSTED]-(u:User {id: $user_id})
            RETURN 
                COLLECT(p.page) AS post_pages,
                b.pages AS total_pages
            """
        )
        result = tx.run(query, user_id=user_id, book_id=book_id)
        record = result.single()
        page_values = record.get("post_pages", [])
        total_pages = record.get("total_pages", 0)

        page_dist = Counter(page_values)
        
        # Initialize the array with zeros
        weights = [0] * 10
        
        # Fill in the weights from the dictionary
        for page, num_posts in page_dist.items():
            norm_page = min(page, total_pages - 1)
            index = int(norm_page // (total_pages / 10))
            weights[index] += int(num_posts)
        max_weight = max(weights)
        if max_weight != 0:
            norm_weights = [weight / max_weight for weight in weights]
        else:
            norm_weights = weights

        progress_bar = BookshelfProgressBar(
            weights=norm_weights,
            total_pages=total_pages,
            default_page_range=total_pages/6
        )
        
        return progress_bar

    def get_bookshelves_member_of_by_user(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_bookshelves_member_of_by_user_query, user_id)
        return result
    
    @staticmethod
    def get_bookshelves_member_of_by_user_query(tx, user_id):
        query = (
            """
            MATCH (b:Bookshelf)<-[r:HAS_BOOKSHELF_ACCESS {type: "member"}]-(u:User {id: $user_id})
            MATCH (owner:User)-[:HAS_BOOKSHELF_ACCESS {type: "owner"}]->(b)
            OPTIONAL MATCH (b)-[:CONTAINS_BOOK]->(bb:Book)
            OPTIONAL MATCH (uu:User)-[:HAS_BOOKSHELF_ACCESS {type: "member"}]->(b)
            OPTIONAL MATCH (follower:User)-[follows_rel:FOLLOWS_SHELF]->(b)
            RETURN b.id as id, 
                b.title as title, 
                b.description as description, 
                b.books as book_ids,
                b.visibility as visibility,
                b.img_url as img_url,
                b.created_by as created_by,
                owner.username as created_by_username,
                count(bb) as book_count,
                count(uu) as member_count,
                count(follower) as follower_count,
                collect(bb.id) as book_object_ids,
                collect(bb.small_img_url) as book_img_urls
            """
        )

        result = tx.run(query, user_id=user_id)
        bookshelves = []
        for record in result:
            book_map = dict(zip(record["book_object_ids"], record["book_img_urls"]))
            first_four_books_imgs = []
            for key in record["book_ids"][:4]:
                first_four_books_imgs.append(book_map[key])
                
            bookshelf = BookshelfPreview(
                id=record["id"],
                title=record["title"],
                book_ids=record["book_ids"],
                description=record["description"],
                visibility=record["visibility"],
                img_url=record["img_url"],
                created_by=record["created_by"],
                created_by_username=record["created_by_username"],
                books_count=record["book_count"],
                book_img_urls=first_four_books_imgs,
                member_count=record["member_count"],
                follower_count=record["follower_count"]
            )
            bookshelves.append(bookshelf)
        return bookshelves
    
    def get_bookshelf_contributors(self, bookshelf_id, current_user_id):
        with self.driver.session() as session:
            contributors, contributor_ids = session.read_transaction(self.get_bookshelf_contributors_query, bookshelf_id, current_user_id)
        return contributors, contributor_ids
    
    @staticmethod
    def get_bookshelf_contributors_query(tx, bookshelf_id, current_user_id):
        query = (
            """
            match (currentUser:User {id:$current_user_id})
            MATCH (bookshelf:Bookshelf {id:$bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS]-(user:User)
            where r.type in ["owner", "contributor"]
            OPTIONAL MATCH (currentUser)<-[incomingFriendStatus:FRIENDED]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingFriendStatus:FRIENDED]->(user)
            OPTIONAL MATCH (currentUser)<-[incomingBlockStatus:BLOCKED]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingBlockStatus:BLOCKED]->(user)
            OPTIONAL MATCH (currentUser)<-[incomingFollowStatus:FOLLOWS]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingFollowStatus:FOLLOWS]->(user)
            RETURN user, currentUser,
                incomingFriendStatus.status AS incomingFriendStatus,
                incomingBlockStatus,
                incomingFollowStatus,
                outgoingFriendStatus.status AS outgoingFriendStatus,
                outgoingBlockStatus,
                outgoingFollowStatus,
                r.type as accessType
            """
        )
        result = tx.run(query, 
                        bookshelf_id=bookshelf_id,
                        current_user_id=current_user_id)
        
        contributors = []
        contributor_ids = []

        for response in result:
            if 'profile_img_url' in response['user']:
                profile_img_url = response['user']['profile_img_url']
            else:
                profile_img_url = None

            if response['incomingFriendStatus'] == 'friends' or response['outgoingFriendStatus'] == 'friends':
                relationship_to_current_user = 'friend'
            elif response['incomingFriendStatus'] == 'pending':
                relationship_to_current_user = 'anonymous_user_friend_requested'
            elif response['outgoingFriendStatus'] == 'pending':
                relationship_to_current_user = 'current_user_friend_requested'
            elif response['incomingBlockStatus']:
                relationship_to_current_user = 'current_user_blocked_by_anonymous_user'
            elif response['outgoingBlockStatus']:
                relationship_to_current_user = 'anonymous_user_blocked_by_current_user'
            elif response['user']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'stranger'

            contributors.append(BookshelfContributor(
                id=response['user']['id'],
                username=response['user']['username'],
                created_date=response['user']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user,
                full_name=response['user']['full_name'],
                role=response['accessType']
            ))

            contributor_ids.append(response['user']['id'])

        
        return contributors, contributor_ids
    
    def get_bookshelf_members(self, bookshelf_id, current_user_id):
        with self.driver.session() as session:
            members, member_ids = session.read_transaction(self.get_bookshelf_members_query, bookshelf_id, current_user_id)
        return members, member_ids
    
    @staticmethod
    def get_bookshelf_members_query(tx, bookshelf_id, current_user_id):
        query = (
            """
            match (currentUser:User {id:$current_user_id})
            MATCH (bookshelf:Bookshelf {id:$bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS]-(user:User)
            where r.type = "member"
            OPTIONAL MATCH (currentUser)<-[incomingFriendStatus:FRIENDED]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingFriendStatus:FRIENDED]->(user)
            OPTIONAL MATCH (currentUser)<-[incomingBlockStatus:BLOCKED]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingBlockStatus:BLOCKED]->(user)
            OPTIONAL MATCH (currentUser)<-[incomingFollowStatus:FOLLOWS]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingFollowStatus:FOLLOWS]->(user)
            RETURN user, currentUser,
                incomingFriendStatus.status AS incomingFriendStatus,
                incomingBlockStatus,
                incomingFollowStatus,
                outgoingFriendStatus.status AS outgoingFriendStatus,
                outgoingBlockStatus,
                outgoingFollowStatus
            """
        )
        result = tx.run(query, 
                        bookshelf_id=bookshelf_id,
                        current_user_id=current_user_id)
        
        members = []
        member_ids = []

        for response in result:
            if 'profile_img_url' in response['user']:
                profile_img_url = response['user']['profile_img_url']
            else:
                profile_img_url = None

            if response['incomingFriendStatus'] == 'friends' or response['outgoingFriendStatus'] == 'friends':
                relationship_to_current_user = 'friend'
            elif response['incomingFriendStatus'] == 'pending':
                relationship_to_current_user = 'anonymous_user_friend_requested'
            elif response['outgoingFriendStatus'] == 'pending':
                relationship_to_current_user = 'current_user_friend_requested'
            elif response['incomingBlockStatus']:
                relationship_to_current_user = 'current_user_blocked_by_anonymous_user'
            elif response['outgoingBlockStatus']:
                relationship_to_current_user = 'anonymous_user_blocked_by_current_user'
            elif response['user']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'stranger'

            members.append(BookshelfMember(
                id=response['user']['id'],
                username=response['user']['username'],
                created_date=response['user']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user,
                full_name=response['user']['full_name'],
                role = "member"
            ))

            member_ids.append(response['user']['id'])

        return members, member_ids
    
    def get_bookshelf_followers(self, bookshelf_id, current_user_id):
        with self.driver.session() as session:
            followers = session.read_transaction(self.get_bookshelf_followers_query, bookshelf_id, current_user_id)
        return followers
    
    @staticmethod
    def get_bookshelf_followers_query(tx, bookshelf_id, current_user_id):
        query = (
            """
            match (currentUser:User {id:$current_user_id})
            MATCH (bookshelf:Bookshelf {id:$bookshelf_id})<-[r:FOLLOWS_SHELF]-(user:User)
            OPTIONAL MATCH (currentUser)<-[incomingFriendStatus:FRIENDED]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingFriendStatus:FRIENDED]->(user)
            OPTIONAL MATCH (currentUser)<-[incomingBlockStatus:BLOCKED]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingBlockStatus:BLOCKED]->(user)
            OPTIONAL MATCH (currentUser)<-[incomingFollowStatus:FOLLOWS]-(user)
            OPTIONAL MATCH (currentUser)-[outgoingFollowStatus:FOLLOWS]->(user)
            RETURN user, currentUser,
                incomingFriendStatus.status AS incomingFriendStatus,
                incomingBlockStatus,
                incomingFollowStatus,
                outgoingFriendStatus.status AS outgoingFriendStatus,
                outgoingBlockStatus,
                outgoingFollowStatus
            """
        )
        result = tx.run(query, 
                        bookshelf_id=bookshelf_id,
                        current_user_id=current_user_id)
        
        followers = []

        for response in result:
            if 'profile_img_url' in response['user']:
                profile_img_url = response['user']['profile_img_url']
            else:
                profile_img_url = None

            if response['incomingFriendStatus'] == 'friends' or response['outgoingFriendStatus'] == 'friends':
                relationship_to_current_user = 'friend'
            elif response['incomingFriendStatus'] == 'pending':
                relationship_to_current_user = 'anonymous_user_friend_requested'
            elif response['outgoingFriendStatus'] == 'pending':
                relationship_to_current_user = 'current_user_friend_requested'
            elif response['incomingBlockStatus']:
                relationship_to_current_user = 'current_user_blocked_by_anonymous_user'
            elif response['outgoingBlockStatus']:
                relationship_to_current_user = 'anonymous_user_blocked_by_current_user'
            elif response['user']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'stranger'

            followers.append(BookshelfFollower(
                id=response['user']['id'],
                username=response['user']['username'],
                created_date=response['user']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user,
                full_name=response['user']['full_name'],
                role="follower"
            ))

        return followers

    def get_user_want_to_read(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_want_to_read_query, user_id)
        return result
    
    @staticmethod
    def get_user_want_to_read_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:WantToReadShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u as user,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(rr) as book_note_for_shelves
            """
        )
        
        result = tx.run(query, user_id=user_id)

        book_objects = []

        record = result.single()

        book_map = {
        book_id: {
            'item': book,
            'description': note_for_shelf.get('note_for_shelf', None)
        }
        for book_id, book, note_for_shelf in zip(record["book_object_ids"], record["books"], record["book_note_for_shelves"])
}     

        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["user"]["id"],
            created_by_username=record["user"]["username"],
            contributors=set([record["user"]["id"]])
        )

        return bookshelf
    
    def get_user_want_to_read_by_shelf_id(self, bookshelf_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_want_to_read_by_shelf_id_query, bookshelf_id)
        return result
    
    @staticmethod
    def get_user_want_to_read_by_shelf_id_query(tx, bookshelf_id):
        query = (
            """
            MATCH (u:User)-[:HAS_READING_FLOW_SHELF]->(shelf:WantToReadShelf {id: $bookshelf_id})
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u as user,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(rr) as book_note_for_shelves
            """
        )
        
        result = tx.run(query, bookshelf_id=bookshelf_id)
        book_objects = []

        record = result.single()

        book_map = {
        book_id: {
            'item': book,
            'description': note_for_shelf.get('note_for_shelf', None)
        }
        for book_id, book, note_for_shelf in zip(record["book_object_ids"], record["books"], record["book_note_for_shelves"])
}
        
        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["user"]["id"],
            created_by_username=record["user"]["username"],
            contributors=set([record["user"]["id"]])
        )

        return bookshelf
    
    def get_user_want_to_read_preview(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_want_to_read_preview_query, user_id)
        return result
    
    @staticmethod
    def get_user_want_to_read_preview_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:WantToReadShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u.id as created_by,
                   u.username as created_by_username,
                   collect(bb.id) as book_object_ids,
                   collect(bb.small_img_url) as book_img_urls,
                   count(bb) as book_count
            """
        )

        result = tx.run(query, user_id=user_id)
        record = result.single()
        
        book_map = dict(zip(record["book_object_ids"], record["book_img_urls"]))
        first_four_books_imgs = []
        for key in record["book_ids"][:4]:
            first_four_books_imgs.append(book_map[key])
            
        bookshelf = BookshelfPreview(
            id=record["id"],
            title=record["title"],
            book_ids=record["book_ids"],
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["created_by"],
            created_by_username=record["created_by_username"],
            books_count=record["book_count"],
            book_img_urls=first_four_books_imgs
        )

        return bookshelf

    def get_user_currently_reading(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_currently_reading_query, user_id)
        return result
    
    @staticmethod
    def get_user_currently_reading_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u as user,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(rr) as book_relationships
            """
        )
        
        result = tx.run(query, user_id=user_id)

        book_objects = []

        record = result.single()

        book_map = {
            book_id: {
                'item': book,
                'description': book_relationship.get('note_for_shelf', None),
                'current_page': book_relationship.get('current_page', 0),
            }
            
            for book_id, book, book_relationship in zip(record["book_object_ids"], record["books"], record["book_relationships"])
        }

        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description,
                current_page=book_map[key]["current_page"],
                total_pages=book.get('pages', 0),
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["user"]["id"],
            created_by_username=record["user"]["username"],
            contributors=set([record["user"]["id"]])
        )

        return bookshelf
    
    def get_user_currently_reading_by_shelf_id(self, bookshelf_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_currently_reading_by_shelf_id_query, bookshelf_id)
        return result
    
    @staticmethod
    def get_user_currently_reading_by_shelf_id_query(tx, bookshelf_id):
        query = (
            """
            MATCH (u:User)-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf {id: $bookshelf_id})
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u as user,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(rr) as book_relationships,
                   
            """
        )
        
        result = tx.run(query, bookshelf_id=bookshelf_id)
        book_objects = []

        record = result.single()
        
        book_map = {
        book_id: {
            'item': book,
            'description': note_for_shelf.get('note_for_shelf', None)
        }
        for book_id, book, note_for_shelf in zip(record["book_object_ids"], record["books"], record["book_note_for_shelves"])
}
        
        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["user"]["id"],
            created_by_username=record["user"]["username"],
            contributors=set([record["user"]["id"]])
        )

        return 
    
    def get_user_currently_reading_preview(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_currently_reading_preview_query, user_id)
        return result
    
    @staticmethod
    def get_user_currently_reading_preview_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u.id as created_by,
                   u.username as created_by_username,
                   collect(bb.id) as book_object_ids,
                   collect(bb.small_img_url) as book_img_urls,
                   count(bb) as book_count
            """
        )

        result = tx.run(query, user_id=user_id)
        record = result.single()
        
        book_map = dict(zip(record["book_object_ids"], record["book_img_urls"]))
        first_four_books_imgs = []
        for key in record["book_ids"][:4]:
            first_four_books_imgs.append(book_map[key])
            
        bookshelf = BookshelfPreview(
            id=record["id"],
            title=record["title"],
            book_ids=record["book_ids"],
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["created_by"],
            created_by_username=record["created_by_username"],
            books_count=record["book_count"],
            book_img_urls=first_four_books_imgs
        )

        return bookshelf
    
    def get_user_currently_reading_front_page(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_currently_reading_front_page_query, user_id)
        return result
    
    @staticmethod
    def get_user_currently_reading_front_page_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u.id as created_by,
                   u.username as created_by_username,
                   collect(bb.title) as book_titles,
                   collect(bb.id) as book_object_ids,
                   collect(bb.small_img_url) as book_small_img_urls,
                   collect(bb.pages) as book_page_counts,
                   count(bb) as book_count,
                   collect(rr) as book_relationships
            """
        )

        result = tx.run(query, user_id=user_id)
        record = result.single()
        
        book_list = []
            
        for book_id, book_title, book_small_image_url, book_rel, total_pages in zip(record["book_object_ids"], 
                                                                                    record["book_titles"],
                                                                                    record["book_small_img_urls"], 
                                                                                    record["book_relationships"],
                                                                                    record["book_page_counts"]):
            book_list.append(
                CurrentlyReadingBookPreview(
                id=book_id,
                title=book_title,  
                small_img_url=book_small_image_url,
                note_for_shelf=book_rel.get('note_for_shelf', None),
                current_page=book_rel.get('current_page', 0), 
                total_pages=total_pages,
                last_updated=book_rel.get(
                    'last_updated', 
                    book_rel.get(
                        'create_date',
                        datetime.datetime.min.replace(
                            tzinfo=datetime.timezone.utc
                            )
                        )  # Default to datetime.min if last_updated is None
                    )
                )
            )
            
        sorted_book_list = sorted(book_list, key=lambda x: x.last_updated, reverse=True)
        first_four_books = sorted_book_list[:4]
        
        bookshelf = CurrentlyReadingBookshelfPreview(
            id=record["id"],
            title=record["title"],
            description=record["description"],
            books=first_four_books,
            visibility=record["visibility"]
            )

        return bookshelf
    
    def get_user_finished_reading(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_finished_reading_query, user_id)
        return result
    
    @staticmethod
    def get_user_finished_reading_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:FinishedReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u as user,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(rr) as book_note_for_shelves
            """
        )
        
        result = tx.run(query, user_id=user_id)

        book_objects = []

        record = result.single()

        book_map = {
        book_id: {
            'item': book,
            'description': note_for_shelf.get('note_for_shelf', None)
        }
        for book_id, book, note_for_shelf in zip(record["book_object_ids"], record["books"], record["book_note_for_shelves"])
}
        
        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["user"]["id"],
            created_by_username=record["user"]["username"],
            contributors=set([record["user"]["id"]])
        )

        return bookshelf
    
    def get_user_finished_reading_by_shelf_id(self, bookshelf_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_finished_reading_by_shelf_id_query, bookshelf_id)
        return result
    
    @staticmethod
    def get_user_finished_reading_by_shelf_id_query(tx, bookshelf_id):
        query = (
            """
            MATCH (u:User)-[:HAS_READING_FLOW_SHELF]->(shelf:FinishedReadingShelf {id: $bookshelf_id})
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u as user,
                   collect(bb.id) as book_object_ids,
                   collect(bb) as books,
                   collect(rr) as book_note_for_shelves
            """
        )
        
        result = tx.run(query, bookshelf_id=bookshelf_id)
        book_objects = []

        record = result.single()

        book_map = {
        book_id: {
            'item': book,
            'description': note_for_shelf.get('note_for_shelf', None)
        }
        for book_id, book, note_for_shelf in zip(record["book_object_ids"], record["books"], record["book_note_for_shelves"])
}
        
        for ix, key in enumerate(record["book_ids"]):
            book = book_map[key]["item"]
            description = book_map[key]["description"]
            if "author_names" not in book:
                book.__setattr__("author_names", ["Unknown Author"])
            book_objects.append(BookshelfBook(
                id=book["id"],
                order=ix,
                title=book["title"],
                authors=book["author_names"],
                small_img_url=book["small_img_url"],
                note_for_shelf=description
            ))
        
        bookshelf = BookshelfPage(
            id=record["id"],
            title=record["title"],
            books=book_objects,
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["user"]["id"],
            created_by_username=record["user"]["username"],
            contributors=set([record["user"]["id"]])
        )

        return bookshelf
    
    def get_user_finished_reading_preview(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self.get_user_finished_reading_preview_query, user_id)
        return result
    
    @staticmethod
    def get_user_finished_reading_preview_query(tx, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:FinishedReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(bb:Book)
            RETURN shelf.id as id, 
                   shelf.title as title, 
                   shelf.description as description, 
                   shelf.books as book_ids,
                   shelf.visibility as visibility,
                   shelf.img_url as img_url,
                   u.id as created_by,
                   u.username as created_by_username,
                   collect(bb.id) as book_object_ids,
                   collect(bb.small_img_url) as book_img_urls,
                   count(bb) as book_count
            """
        )

        result = tx.run(query, user_id=user_id)
        record = result.single()
        
        book_map = dict(zip(record["book_object_ids"], record["book_img_urls"]))
        first_four_books_imgs = []
        for key in record["book_ids"][:4]:
            first_four_books_imgs.append(book_map[key])
            
        bookshelf = BookshelfPreview(
            id=record["id"],
            title=record["title"],
            book_ids=record["book_ids"],
            description=record["description"],
            visibility=record["visibility"],
            img_url=record["img_url"],
            created_by=record["created_by"],
            created_by_username=record["created_by_username"],
            books_count=record["book_count"],
            book_img_urls=first_four_books_imgs
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
    
    def create_book_in_bookshelf_rel(self, book_to_add, bookshelf_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.create_book_in_bookshelf_rel_query, book_to_add, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def create_book_in_bookshelf_rel_query(tx, book_to_add, bookshelf_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})
            match (book:Book {id: $book_id})
            with b, book
            OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
            WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
            MERGE (b)-[r:CONTAINS_BOOK]->(book)
            ON CREATE SET 
                b.books = COALESCE(b.books, []) + $book_id, 
                b.last_edited_date = datetime(),
                r.create_date = datetime(),
                r.added_by_id = $user_id,
                r.note_for_shelf = $note_for_shelf
            RETURN NOT relationshipExists AS wasAdded
            """
        )
        result = tx.run(query, book_id=book_to_add.id, 
                        title=book_to_add.title, 
                        small_img_url=book_to_add.small_img_url,
                        author_names=book_to_add.authors,
                        note_for_shelf=book_to_add.note_for_shelf,
                        bookshelf_id=bookshelf_id, 
                        user_id=user_id)
        response = result.single()
        if not response:
            return False
        return response['wasAdded']
    
    def create_book_in_bookshelf_rel_and_book(self, book_to_add, bookshelf_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.create_book_in_bookshelf_rel_and_book_query, book_to_add, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def create_book_in_bookshelf_rel_and_book_query(tx, book_to_add, bookshelf_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})
            create (book:Book {id:"c"+randomUUID(),
                                google_id:$book_id, 
                                title:$title, 
                                small_img_url:$small_img_url, 
                                author_names: $author_names})
            with b, book
            OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
            WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
            MERGE (b)-[r:CONTAINS_BOOK]->(book)
            ON CREATE SET 
                b.books = COALESCE(b.books, []) + book.id, 
                b.last_edited_date = datetime(),
                r.create_date = datetime(),
                r.added_by_id = $user_id,
                r.note_for_shelf = $note_for_shelf
            RETURN NOT relationshipExists AS wasAdded,
                     book.id as id
            """
        )
        result = tx.run(query, book_id=book_to_add.id, 
                        title=book_to_add.title, 
                        small_img_url=book_to_add.small_img_url,
                        author_names=book_to_add.authors,
                        note_for_shelf=book_to_add.note_for_shelf,
                        bookshelf_id=bookshelf_id, 
                        user_id=user_id)
        response = result.single()
        if not response:
            return False
        if response['wasAdded']:
            return response['id']
        return False
    
    def create_book_in_reading_flow_bookshelf_rel(
            self, 
            book_to_add,
            bookshelf_type,
            user_id):
        
        with self.driver.session() as session:
            result = session.write_transaction(self.create_book_in_reading_flow_bookshelf_rel_query, book_to_add, bookshelf_type, user_id)
        return result
    
    @staticmethod
    def create_book_in_reading_flow_bookshelf_rel_query(
        tx, 
        book_to_add, 
        bookshelf_type,
        user_id):
        if bookshelf_type == "want_to_read":
            query = (
                """
                MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:WantToReadShelf)
                match (book:Book {id:$book_id})
                with b, book
                OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
                WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
                MERGE (b)-[r:CONTAINS_BOOK]->(book)
                ON CREATE SET 
                    b.books = COALESCE(b.books, []) + $book_id, 
                    b.last_edited_date = datetime(),
                    r.create_date = datetime(),
                    r.added_by_id = $user_id,
                    r.note_for_shelf = $note_for_shelf
                RETURN NOT relationshipExists AS wasAdded,
                       b.id as bookshelf_id
                """
            )
        elif bookshelf_type == "currently_reading":
            query = (
                """
                MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:CurrentlyReadingShelf)
                match (book:Book {id:$book_id})
                with b, book
                OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
                WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
                MERGE (b)-[r:CONTAINS_BOOK]->(book)
                ON CREATE SET 
                    b.books = COALESCE(b.books, []) + $book_id, 
                    b.last_edited_date = datetime(),
                    r.create_date = datetime(),
                    r.last_updated = datetime(),
                    r.added_by_id = $user_id,
                    r.note_for_shelf = $note_for_shelf
                RETURN NOT relationshipExists AS wasAdded,
                       b.id as bookshelf_id
                """
            )
        elif bookshelf_type == "finished_reading":
            query = (
                """
                MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:FinishedReadingShelf)
                match (book:Book {id:$book_id})
                with b, book
                OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
                WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
                MERGE (b)-[r:CONTAINS_BOOK]->(book)
                ON CREATE SET 
                    b.books = COALESCE(b.books, []) + $book_id, 
                    b.last_edited_date = datetime(),
                    r.create_date = datetime(),
                    r.added_by_id = $user_id,
                    r.note_for_shelf = $note_for_shelf
                RETURN NOT relationshipExists AS wasAdded,
                       b.id as bookshelf_id
                """
            )
        else:
            return False
        
        result = tx.run(
            query,
            book_id=book_to_add.id,
            note_for_shelf=book_to_add.note_for_shelf, 
            user_id=user_id)
        response = result.single()
        
        return response.get('wasAdded',False), response.get('bookshelf_id','')
    
    def create_book_in_reading_flow_bookshelf_rel_with_shelf_id(
            self, 
            book_to_add,
            bookshelf_id,
            user_id):
        
        with self.driver.session() as session:
            result = session.write_transaction(self.create_book_in_reading_flow_bookshelf_rel_with_shelf_id_query, book_to_add, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def create_book_in_reading_flow_bookshelf_rel_with_shelf_id_query(
        tx, 
        book_to_add, 
        bookshelf_id,
        user_id):

        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b: {id: $bookshelf_id})
            match (book:Book {id:$book_id})
            with b, book
            OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
            WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
            MERGE (b)-[r:CONTAINS_BOOK]->(book)
            ON CREATE SET 
                b.books = COALESCE(b.books, []) + $book_id, 
                b.last_edited_date = datetime(),
                r.create_date = datetime(),
                r.added_by_id = $user_id,
                r.note_for_shelf = $note_for_shelf
            RETURN NOT relationshipExists AS wasAdded
            """
        )
        
        result = tx.run(
            query,
            book_id=book_to_add.id,
            note_for_shelf=book_to_add.note_for_shelf,
            bookshelf_id=bookshelf_id,
            user_id=user_id)
        response = result.single()
        if not response:
            return False
        return response['wasAdded']
    
    def create_book_in_reading_flow_bookshelf_rel_and_book(
            self, 
            book_to_add,
            bookshelf_type,
            user_id):
        
        with self.driver.session() as session:
            result = session.write_transaction(self.create_book_in_reading_flow_bookshelf_rel_and_book_query, book_to_add, bookshelf_type, user_id)
        return result
    
    @staticmethod
    def create_book_in_reading_flow_bookshelf_rel_and_book_query(
        tx,
        book_to_add,
        bookshelf_type,
        user_id):

        if bookshelf_type == "want_to_read":
            query = (
                """
                MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:WantToReadShelf)
                create (book:Book {id:"c"+randomUUID(),
                                    google_id:$book_id, 
                                    title:$title, 
                                    small_img_url:$small_img_url, 
                                    author_names: $author_names})
                with b, book
                OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
                WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
                MERGE (b)-[r:CONTAINS_BOOK]->(book)
                ON CREATE SET 
                    b.books = COALESCE(b.books, []) + book.id, 
                    b.last_edited_date = datetime(),
                    r.create_date = datetime(),
                    r.added_by_id = $user_id,
                    r.note_for_shelf = $note_for_shelf
                RETURN NOT relationshipExists AS wasAdded,
                        book.id as id,
                        b.id as bookshelf_id
                """
            )
        elif bookshelf_type == "currently_reading":
            query = (
                """
                MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:CurrentlyReadingShelf)
                create (book:Book {id:"c"+randomUUID(),
                                    google_id:$book_id, 
                                    title:$title, 
                                    small_img_url:$small_img_url, 
                                    author_names: $author_names})
                with b, book
                OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
                WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
                MERGE (b)-[r:CONTAINS_BOOK]->(book)
                ON CREATE SET 
                    b.books = COALESCE(b.books, []) + book.id, 
                    b.last_edited_date = datetime(),
                    r.create_date = datetime(),
                    r.last_updated = datetime(),
                    r.added_by_id = $user_id,
                    r.note_for_shelf = $note_for_shelf
                RETURN NOT relationshipExists AS wasAdded,
                        book.id as id,
                        b.id as bookshelf_id
                """
            )
        elif bookshelf_type == "finished_reading":
            query = (
                """
                MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:FinishedReadingShelf)
                create (book:Book {id:"c"+randomUUID(),
                                    google_id:$book_id, 
                                    title:$title, 
                                    small_img_url:$small_img_url, 
                                    author_names: $author_names})
                with b, book
                OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
                WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
                MERGE (b)-[r:CONTAINS_BOOK]->(book)
                ON CREATE SET 
                    b.books = COALESCE(b.books, []) + book.id, 
                    b.last_edited_date = datetime(),
                    r.create_date = datetime(),
                    r.added_by_id = $user_id,
                    r.note_for_shelf = $note_for_shelf
                RETURN NOT relationshipExists AS wasAdded,
                        book.id as id,
                        b.id as bookshelf_id
                """
            )
        else:
            return False
        
        result = tx.run(
            query,
            book_id=book_to_add.id,
            title=book_to_add.title,
            small_img_url=book_to_add.small_img_url,
            author_names=book_to_add.authors,
            note_for_shelf=book_to_add.note_for_shelf,
            user_id=user_id)

        response = result.single()
        
        if response.get('wasAdded'):
            return response['id'], response['bookshelf_id']
        return False, False
    
    def create_book_in_reading_flow_bookshelf_rel_with_shelf_id_and_book(
            self, 
            book_to_add,
            bookshelf_id,
            user_id):
        
        with self.driver.session() as session:
            result = session.write_transaction(self.create_book_in_reading_flow_bookshelf_rel_with_shelf_id_and_book_query, book_to_add, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def create_book_in_reading_flow_bookshelf_rel_with_shelf_id_and_book_query(
        tx,
        book_to_add,
        bookshelf_id,
        user_id):

        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b: {id: $bookshelf_id})
            create (book:Book {id:"c"+randomUUID(),
                                google_id:$book_id, 
                                title:$title, 
                                small_img_url:$small_img_url, 
                                author_names: $author_names})
            with b, book
            OPTIONAL MATCH (b)-[rr:CONTAINS_BOOK]->(book)
            WITH b, book, rr, EXISTS((b)-[:CONTAINS_BOOK]->(book)) AS relationshipExists
            MERGE (b)-[r:CONTAINS_BOOK]->(book)
            ON CREATE SET 
                b.books = COALESCE(b.books, []) + book.id, 
                b.last_edited_date = datetime(),
                r.create_date = datetime(),
                r.added_by_id = $user_id,
                r.note_for_shelf = $note_for_shelf
            RETURN NOT relationshipExists AS wasAdded,
                    book.id as id
            """
        )

        result = tx.run(
            query,
            book_id=book_to_add.id,
            bookshelf_id=bookshelf_id,
            title=book_to_add.title,
            small_img_url=book_to_add.small_img_url,
            author_names=book_to_add.authors,
            note_for_shelf=book_to_add.note_for_shelf,
            user_id=user_id)

        response = result.single()
        if not response:
            return False
        if response['wasAdded']:
            return response['id']
        return False
    
    def create_follow_bookshelf_rel(self, bookshelf_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.create_follow_bookshelf_rel_query, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def create_follow_bookshelf_rel_query(tx, bookshelf_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id, visibility: "public"})
            MATCH (u:User {id: $user_id, disabled: false})
            MERGE (u)-[r:FOLLOWS_SHELF {created_date: datetime()}]->(b)
            RETURN b.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def update_bookshelf_contributors(self, bookshelf_id, contributor_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_bookshelf_contributors_query, bookshelf_id, contributor_id, user_id)
        return result
    
    @staticmethod
    def update_bookshelf_contributors_query(tx, bookshelf_id, contributor_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            MATCH (c:User {id: $contributor_id})
            WHERE NOT EXISTS {
                MATCH (bb)<-[rrr:HAS_BOOKSHELF_ACCESS {type: "contributor"}]-(uu:User)
                WITH bb, COUNT(uu) AS contributorCount
                WHERE contributorCount >= 5
                RETURN bb
            }
            MERGE (c)-[rr:HAS_BOOKSHELF_ACCESS]->(b)
            set rr.type = "contributor", rr.create_date = datetime()
            RETURN c.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, contributor_id=contributor_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def update_bookshelf_members(self, bookshelf_id, member_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_bookshelf_members_query, bookshelf_id, member_id, user_id)
        return result
    
    @staticmethod
    def update_bookshelf_members_query(tx, bookshelf_id, member_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            MATCH (c:User {id: $member_id})
            MERGE (c)-[rr:HAS_BOOKSHELF_ACCESS]->(b)
            ON CREATE
                set rr.type = "member", rr.create_date = datetime()
            RETURN rr.type as type
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, member_id=member_id, user_id=user_id)
        response = result.single()
        return response['type'] == "member"
        
    
    def update_books_in_bookshelf(self, books, bookshelf_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_books_in_bookshelf_query, books, bookshelf_id)
        return result
    
    @staticmethod
    def update_books_in_bookshelf_query(tx, books, bookshelf_id):
        query = (
            """
            MATCH (b {id: $bookshelf_id})
            SET b.books = $books, b.last_edited_date = datetime()
            RETURN b.id as id
            """
        )
        result = tx.run(query, books=books, bookshelf_id=bookshelf_id)
        response = result.single()
        return response is not None
    
    def update_bookshelf_title(self, bookshelf_id, title, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_bookshelf_title_query, bookshelf_id, title, user_id)
        return result
    
    @staticmethod
    def update_bookshelf_title_query(tx, bookshelf_id, title, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            SET b.title = $title, b.last_edited_date = datetime()
            RETURN b.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, title=title, user_id=user_id)
        response = result.single()
        return response is not None
    
    def update_bookshelf_description(self, bookshelf_id, description, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_bookshelf_description_query, bookshelf_id, description, user_id)
        return result
    
    @staticmethod
    def update_bookshelf_description_query(tx, bookshelf_id, description, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            SET b.description = $description, b.last_edited_date = datetime()
            RETURN b.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, description=description, user_id=user_id)
        response = result.single()
        return response is not None
    
    def update_bookshelf_visibility(self, bookshelf_id, visibility, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_bookshelf_visibility_query, bookshelf_id, visibility, user_id)
        return result
    
    @staticmethod
    def update_bookshelf_visibility_query(tx, bookshelf_id, visibility, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            SET b.visibility = $visibility, b.last_edited_date = datetime()
            RETURN b.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, visibility=visibility, user_id=user_id)
        response = result.single()
        return response is not None
    
    def update_book_note_for_shelf(self, bookshelf_id, book_id, note_for_shelf, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_book_note_for_shelf_query, bookshelf_id, book_id, note_for_shelf, user_id)
        return result
    
    @staticmethod
    def update_book_note_for_shelf_query(tx, bookshelf_id, book_id, note_for_shelf, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS]-(u:User {id: $user_id})
            where r.type in ["owner", "contributor"]
            MATCH (b)-[rr:CONTAINS_BOOK]->(book:Book {id: $book_id})
            SET rr.note_for_shelf = $note_for_shelf, b.last_edited_date = datetime()
            RETURN b.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, book_id=book_id, note_for_shelf=note_for_shelf, user_id=user_id)
        response = result.single()
        return response is not None

    def update_book_note_for_shelf_reading_flow(self, bookshelf_id, book_id, note_for_shelf, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.update_book_note_for_shelf_reading_flow_query, bookshelf_id, book_id, note_for_shelf, user_id)
        return result
    
    @staticmethod
    def update_book_note_for_shelf_reading_flow_query(tx, bookshelf_id, book_id, note_for_shelf, user_id):
        query = (
            """
            MATCH (b {id: $bookshelf_id})<-[r:HAS_READING_FLOW_SHELF]-(u:User {id: $user_id})
            MATCH (b)-[rr:CONTAINS_BOOK]->(book:Book {id: $book_id})
            SET rr.note_for_shelf = $note_for_shelf, b.last_edited_date = datetime(), rr.last_updated = datetime()
            RETURN b.id as id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, book_id=book_id, note_for_shelf=note_for_shelf, user_id=user_id)
        response = result.single()
        return response is not None    
    
    def update_currently_reading_page(
        self,
        user_id,
        book_id,
        new_current_page):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.update_currently_reading_page_query,
                user_id,
                book_id,
                new_current_page)
        return result
    
    @staticmethod
    def update_currently_reading_page_query(
        tx,
        user_id,
        book_id,
        new_current_page):
        
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(b:CurrentlyReadingShelf)
            MATCH (b)-[r:CONTAINS_BOOK]->(book:Book {id: $book_id})
            set r.current_page = $new_current_page
            set r.last_updated = datetime()
            return book
            """
        )
        
        result = tx.run(query,
                        user_id=user_id,
                        book_id=book_id,
                        new_current_page=new_current_page)
        response = result.single()
        return response is not None
        
    
    def delete_book_from_bookshelf(self, book_to_remove, books, bookshelf_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_book_from_bookshelf_query, book_to_remove, books, bookshelf_id)
        return result
    
    @staticmethod
    def delete_book_from_bookshelf_query(tx, book_to_remove, books, bookshelf_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})-[r:CONTAINS_BOOK]->(book:Book {id: $book_to_remove})
            SET b.books = $books, b.last_edited_date = datetime()
            DELETE r
            return b.id
            """
        )
        result = tx.run(query, book_to_remove=book_to_remove, books=books, bookshelf_id=bookshelf_id)
        response = result.single()
        return response is not None
    
    def delete_bookshelf(self, bookshelf_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_bookshelf_query, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def delete_bookshelf_query(tx, bookshelf_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            DETACH DELETE b
            return u.id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_bookshelf_contributor(self, bookshelf_id, contributor_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_bookshelf_contributor_query, bookshelf_id, contributor_id, user_id)
        return result
    
    @staticmethod
    def delete_bookshelf_contributor_query(tx, bookshelf_id, contributor_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            MATCH (c:User {id: $contributor_id})-[rr:HAS_BOOKSHELF_ACCESS {type:"contributor"}]->(b)
            DELETE rr
            return b.id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, contributor_id=contributor_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_bookshelf_member(self, bookshelf_id, member_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_bookshelf_member_query, bookshelf_id, member_id, user_id)
        return result
    
    @staticmethod
    def delete_bookshelf_member_query(tx, bookshelf_id, member_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:HAS_BOOKSHELF_ACCESS {type: "owner"}]-(u:User {id: $user_id})
            MATCH (c:User {id: $member_id})-[rr:HAS_BOOKSHELF_ACCESS {type:"member"}]->(b)
            DELETE rr
            return b.id
            """
        )
        print(bookshelf_id, member_id, user_id)
        result = tx.run(query, bookshelf_id=bookshelf_id, member_id=member_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_follow_bookshelf_rel(self, bookshelf_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_follow_bookshelf_rel_query, bookshelf_id, user_id)
        return result
    
    @staticmethod
    def delete_follow_bookshelf_rel_query(tx, bookshelf_id, user_id):
        query = (
            """
            MATCH (b:Bookshelf {id: $bookshelf_id})<-[r:FOLLOWS_SHELF]-(u:User {id: $user_id})
            DELETE r
            return b.id
            """
        )
        result = tx.run(query, bookshelf_id=bookshelf_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_book_from_want_to_read(self, book_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_book_from_want_to_read_query, book_id, user_id)
        return result
    
    @staticmethod
    def delete_book_from_want_to_read_query(tx, book_id, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:WantToReadShelf)
            MATCH (shelf)-[r:CONTAINS_BOOK]->(book:Book {id: $book_id})
            DELETE r
            SET shelf.books = [book_id IN shelf.books WHERE book_id <> $book_id]
            return shelf.id
            """
        )
        result = tx.run(query, book_id=book_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_book_from_currently_reading(self, book_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_book_from_currently_reading_query, book_id, user_id)
        return result
    
    @staticmethod
    def delete_book_from_currently_reading_query(tx, book_id, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf)
            MATCH (shelf)-[r:CONTAINS_BOOK]->(book:Book {id: $book_id})
            DELETE r
            SET shelf.books = [book_id IN shelf.books WHERE book_id <> $book_id]
            return shelf.id
            """
        )
        result = tx.run(query, book_id=book_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_book_from_finished_reading(self, book_id, user_id):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_book_from_finished_reading_query, book_id, user_id)
        return result
    
    @staticmethod
    def delete_book_from_finished_reading_query(tx, book_id, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf:FinishedReadingShelf)
            MATCH (shelf)-[r:CONTAINS_BOOK]->(book:Book {id: $book_id})
            DELETE r
            SET shelf.books = [book_id IN shelf.books WHERE book_id <> $book_id]
            return shelf.id
            """
        )
        result = tx.run(query, book_id=book_id, user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_book_from_bookshelf_with_validate(
            self,
            book_id,
            bookshelf_id,
            user_id
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.delete_book_from_bookshelf_with_validate_query,
                book_id,
                bookshelf_id,
                user_id
            )
        return result
    
    @staticmethod
    def delete_book_from_bookshelf_with_validate_query(
        tx, 
        book_id, 
        bookshelf_id, 
        user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_BOOKSHELF_ACCESS {type: "owner"}]->(shelf:Bookshelf {id: $bookshelf_id})
            MATCH (shelf)-[r:CONTAINS_BOOK]->(book:Book {id: $book_id})
            DELETE r
            SET shelf.books = [book_id IN shelf.books WHERE book_id <> $book_id]
            return shelf.id
            """
        )
        result = tx.run(
            query, 
            book_id=book_id, 
            bookshelf_id=bookshelf_id,
            user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_book_from_reading_flow_bookshelf_with_validate(
            self,
            book_id,
            bookshelf_id,
            user_id
    ):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.delete_book_from_reading_flow_bookshelf_with_validate_query,
                book_id,
                bookshelf_id,
                user_id
            )
        return result
    
    @staticmethod
    def delete_book_from_reading_flow_bookshelf_with_validate_query(tx, book_id, bookshelf_id, user_id):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_READING_FLOW_SHELF]->(shelf)
            WHERE shelf.id = $bookshelf_id
            AND (
                shelf:CurrentlyReadingShelf OR 
                shelf:FinishedReadingShelf OR 
                shelf:WantToReadShelf
            )
            MATCH (shelf)-[r:CONTAINS_BOOK]->(book:Book {id: $book_id})
            DELETE r
            SET shelf.books = [book_id IN shelf.books WHERE book_id <> $book_id]
            return shelf.id
            """
        )
        result = tx.run(
            query, 
            book_id=book_id, 
            bookshelf_id=bookshelf_id,
            user_id=user_id)
        response = result.single()
        return response is not None
    
    def delete_book_shelf_data_for_user(self, user_id:str):
        with self.driver.session() as session:
            result = session.write_transaction(self.delete_book_shelf_data_for_user_query, user_id)
        return result
    
    @staticmethod
    def delete_book_shelf_data_for_user_query(tx, user_id:str):
        query = (
            """
            MATCH (u:User {id: $user_id})-[:HAS_BOOKSHELF_ACCESS {type:"owner"}]->(shelf:Bookshelf)
            DETACH DELETE shelf
            """
        )
        result = tx.run(query, user_id=user_id)
        return True
