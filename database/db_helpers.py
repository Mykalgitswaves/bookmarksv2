from neo4j import GraphDatabase
from fastapi import HTTPException
import uuid
import json
import sys
sys.path.append('./')
from helpers import timing_decorator 

class User():
    def __init__(self, user_id: str, 
                 username="", 
                 created_date="", 
                 post_ids=[],
                 friends=[],
                 liked_posts=[],
                 email="",
                 full_name="",
                 hashed_password="",
                 disabled=False,
                 user_type="Standard",
                 followers=[],
                 following=[],
                 profile_img_url="",
                 bio="",
                 relationship_to_current_user='self'):
        self.user_id = user_id
        self.posts = post_ids
        self.friends = friends
        self.liked_posts = liked_posts
        self.username = username
        self.created_date = created_date
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.disabled=disabled
        self.user_type=user_type
        self.followers=followers
        self.following=following
        self.profile_img_url=profile_img_url
        self.bio = bio
        self.relationship_to_current_user = relationship_to_current_user 

    def add_favorite_genre(self, genre_id,driver):
        """
        Adds a favorite genre relationship to the database
        
        Args:
            genre_id: PK of the genre to favorite
        Returns:
            None
        """
        if genre_id not in self.genres:
            driver.add_favorite_genre(self.user_id, genre_id)
            self.genres.append(genre_id)
        else:
            raise Exception("This relationship already exists")
        
    def add_favorite_author(self, author_id, driver):
        """
        Adds a favorite author relationship to the database
        
        Args:
            author_id: PK of the author to favorite
        Returns:
            None
        """
        if author_id not in self.authors:
            driver.add_favorite_author(self.user_id, author_id)
            self.authors.append(author_id)
        else:
            raise Exception("This relationship already exists")
        
    def add_liked_post(self, review_id, driver):
        """
        Adds a liked review relationship to the database
        
        Args:
            review_id: PK of the review to like
        Returns:
            None
        """
        if review_id not in self.liked_reviews:
            driver.add_liked_post(self.user_id, review_id)
            self.liked_reviews.append(review_id)
        else:
            raise Exception("This relationship already exists")
        
    def add_to_read(self, book_id, driver):
        """
        Adds a book to the user's to read list in db. Deletes all other relationships to this book
        
        Args:
            book_id: PK of book to add to to read
        Returns:
            None
        """
        if book_id not in self.want_to_read:
            driver.add_to_read(self.user_id, book_id)
            self.want_to_read.append(book_id)
        else:
            raise Exception("This relationship already exists")
        
    def add_is_reading(self, book_id, driver):
        """
        Adds a book to the user's currently reading list in db. Deletes all other relationships to this book
        
        Args:
            book_id: PK of book to add to to read
        Returns:
            None
        """
        if book_id not in self.reading:
            driver.add_reading(self.user_id, book_id)
            self.reading.append(book_id)
        else:
            raise Exception("This relationship already exists")
        
    def update_username(self,new_username,driver):
        """
        Updates the username of a user
        """
        result=driver.update_username(new_username=new_username,user_id=self.user_id)
        if result.status_code == 200:
            self.username=new_username
        
        return result
    
    def update_bio(self,new_bio,driver):
        """
        Updates the bio of a user
        """
        driver.update_bio(new_bio=new_bio,user_id=self.user_id)
        self.bio=new_bio

    def update_password(self,new_password,driver):
        """
        Updates a users password
        """
        driver.update_password(new_password,self.id)
        self.hashed_password = new_password 

    def send_friend_request(self,friend_id, driver):
            result = driver.send_friend_request(self.user_id,friend_id)
            return result
    
    def unsend_friend_request(self,friend_id,driver):
        result = driver.unsend_friend_request(self.user_id,friend_id)
        return result
    
    def accept_friend_request(self,friend_id,driver):
        result = driver.accept_friend_request(friend_id,self.user_id)
        return(result)
    
    def decline_friend_request(self,friend_id,driver):
        result = driver.decline_friend_request(friend_id,self.user_id)
        return(result)
    
    def remove_friend(self,friend_id,driver):
        result = driver.remove_friend(self.user_id,friend_id)
        return(result)

    def follow_user(self,followed_user_id,driver):
        result = driver.follow_user(self.user_id,followed_user_id)
        return(result)
    
    def unfollow_user(self,unfollowed_user_id,driver):
        result = driver.unfollow_user(self.user_id,unfollowed_user_id)
        return(result)
    
    def block_user(self,blocked_user_id,driver):
        result = driver.block_user(self.user_id,blocked_user_id)
        return(result)

    def unblock_user(self,unblocked_user_id,driver):
        result = driver.unblock_user(self.user_id,unblocked_user_id)
        return(result)
    
    def get_posts(self,driver):
        output = driver.pull_all_reviews_by_user(self.username)
        return(output)

class Review():
    def __init__(self, 
                 post_id, 
                 book, 
                 created_date="", 
                 user_id="", 
                 user_username="",
                 book_title="", 
                 book_small_img="", 
                 comments=[], 
                 likes=0,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_comments=0):
        
        self.id = post_id
        self.created_date = created_date
        self.user_username = user_username
        self.user_id = user_id
        self.book = book
        self.book_title = book_title
        self.book_small_img = book_small_img
        self.comments = comments
        self.likes = likes
        self.liked_by_current_user = liked_by_current_user
        self.posted_by_current_user = posted_by_current_user
        self.num_comments = num_comments


class ReviewPost(Review):
    def __init__(self, 
                 post_id, 
                 book, 
                 questions, 
                 question_ids, 
                 responses, 
                 spoilers, 
                 headline="", 
                 created_date="", 
                 user_username="", 
                 user_id="",
                 book_small_img="",
                 book_title="",
                 comments=[],
                 likes=0,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_comments=0):
        
        super().__init__(post_id,
                         book, 
                         created_date, 
                         user_id, 
                         user_username,
                         book_title,
                         book_small_img,
                         comments,
                         likes,
                         liked_by_current_user,
                         posted_by_current_user,
                         num_comments)
        
        self.headline = headline
        self.questions = questions
        self.question_ids = question_ids
        self.responses = responses
        self.spoilers = spoilers

    def create_post(self,driver):
        created_date, id = driver.create_review(self)
        self.id = id
        self.created_date = created_date
    

class UpdatePost(Review):
    def __init__(self, 
                 post_id, 
                 book, 
                 page, 
                 response, 
                 spoiler, 
                 headline="", 
                 created_date="", 
                 user_id="", 
                 user_username="",
                 book_small_img="",
                 book_title="",
                 comments=[],
                 likes=0,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_comments=0):
        
        super().__init__(post_id, 
                         book, 
                         created_date, 
                         user_id, 
                         user_username,
                         book_title,
                         book_small_img,
                         comments,
                         likes,
                         liked_by_current_user,
                         posted_by_current_user,
                         num_comments)
        
        self.page = page
        self.headline = headline
        self.response = response
        self.spoiler = spoiler

    def create_post(self,driver):
        created_date, id = driver.create_update(self)
        self.id = id
        self.created_date = created_date


class ComparisonPost(Review):
    def __init__(self, 
                 post_id, 
                 compared_books, 
                 comparators:list, 
                 comparator_ids:list, 
                 responses:list, 
                 book_specific_headlines:list, 
                 created_date="", 
                 user_id="", 
                 user_username="", 
                 book_small_img=["",""], 
                 book_title=["",""],
                 comments=[],
                 likes=0,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_comments=0):
        
        super().__init__(post_id, 
                         compared_books, 
                         created_date, 
                         user_id, 
                         user_username, 
                         book_title, 
                         book_small_img,
                         comments,
                         likes,
                         liked_by_current_user,
                         posted_by_current_user,
                         num_comments)
        
        self.compared_books = compared_books
        self.comparators = comparators
        self.comparator_ids = comparator_ids
        self.responses = responses
        self.book_specific_headlines = book_specific_headlines
 
    def create_post(self, driver):
        created_date, id = driver.create_comparison(self)
        self.id = id
        self.created_date = created_date


class RecommendationFriend(Review):
    def __init__(self, 
                 post_id, 
                 book, 
                 to_user_username, 
                 from_user_text, 
                 to_user_text, 
                 created_date="", 
                 user_id="", 
                 user_username="",
                 book_small_img="",
                 book_title="",
                 comments=[],
                 likes=0,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_comments=0):
        
        super().__init__(post_id, 
                         book, 
                         created_date, 
                         user_id, 
                         user_username,
                         book_title,
                         book_small_img,
                         comments,
                         likes,
                         liked_by_current_user,
                         posted_by_current_user,
                         num_comments)
        
        self.to_user_username = to_user_username
        self.from_user_text = from_user_text
        self.to_user_text = to_user_text

    def create_post(self,driver):
        created_date, id = driver.create_recommendation_post(self)
        self.id = id
        self.created_date = created_date


class MilestonePost(Review):
    def __init__(self, 
                 post_id, 
                 book, 
                 num_books:int, 
                 created_date="", 
                 user_id="", 
                 user_username="",
                 book_small_img="",
                 book_title="",
                 comments=[],
                 likes=0,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_comments=0):
        
        super().__init__(post_id, 
                         book, 
                         created_date, 
                         user_id, 
                         user_username,
                         book_title,
                         book_small_img,
                         comments,
                         likes,
                         liked_by_current_user,
                         posted_by_current_user,
                         num_comments)
        
        self.num_books = num_books

    def create_post(self,driver):
        created_date, id = driver.create_milestone(self)
        self.id = id
        self.created_date = created_date



class Book():
    def __init__(self, 
                 book_id, 
                 gr_id=None, 
                 img_url="", 
                 small_img_url="", 
                 pages=None, 
                 publication_year=None, 
                 lang="", 
                 title="", 
                 description="", 
                 isbn13=None,
                 isbn10=None,
                 genres=[], 
                 authors=[], 
                 tags=[], 
                 reviews=[], 
                 genre_names=[], 
                 author_names=[], 
                 google_id="",
                 in_database=True):
        
        self.id = book_id
        self.gr_id = gr_id
        self.img_url = img_url
        self.small_img_url = small_img_url
        self.pages = pages
        self.publication_year = publication_year
        self.lang = lang
        self.title = title
        self.description = description 
        self.genres = genres
        self.genre_names = genre_names
        self.authors = authors
        self.author_names = author_names
        self.tags = tags
        self.reviews = reviews
        self.isbn13 = isbn13
        self.isbn10 = isbn10
        self.in_database = in_database
        self.google_id = google_id

    def add_tag(self,tag_id, driver):
        """
        Adds a tag to the book
        
        Args:
            tag_id: PK of tag to add
        Returns:
            None
        """
        if tag_id not in self.tags:
            driver.add_book_tag(self.id, tag_id)
            self.tags.append(tag_id)
        else:
            raise Exception("This relationship already exists")
    def add_to_db(self, driver):
        book = driver.create_book(self.title,self.img_url,self.pages,self.publication_year,self.lang,self.description,self.genres,
                           self.authors,self.isbn13, self.isbn10, self.small_img_url,self.author_names,self.genre_names,self.google_id,self.gr_id)
        self.id = book.id
    def add_canon_version(self, canon_book_id:str, driver):
        driver.create_canon_book_relationship(canon_book_id,self.id)

        
class Author():
    def __init__(self, author_id, full_name, books=[]):
        self.id=author_id
        self.full_name=full_name
        self.books=books

class Genre():
    def __init__(self, genre_id, name, books=[]):
        self.id = genre_id
        self.name = name
        self.books = books

class Tag():
    def __init__(self, tag_id, name, books=[]):
        self.id = tag_id
        self.name = name
        self.books = books

class Comment():
    def __init__(self, 
                 comment_id, 
                 post_id, 
                 replied_to, 
                 text, 
                 username,
                 user_id,
                 created_date="", 
                 likes=0, 
                 pinned=False,
                 liked_by_current_user=False,
                 posted_by_current_user=False,
                 num_replies=0):
        self.id = comment_id
        self.post_id = post_id
        self.replied_to = replied_to
        self.text = text
        self.username = username
        self.user_id = user_id
        self.created_date = created_date
        self.likes = likes
        self.pinned = pinned
        self.liked_by_current_user = liked_by_current_user
        self.posted_by_current_user = posted_by_current_user
        self.num_replies = num_replies

    def create_comment(self, driver):
        comment_id, created_date = driver.create_comment(self)
        self.id = comment_id
        self.created_date = created_date


class Neo4jDriver():
    def __init__(self):
        with open("config.json","r") as f:
            CONFIG = json.load(f)
        uri = CONFIG["uri"]
        self.driver = GraphDatabase.driver(uri, auth = (CONFIG["username"],CONFIG["password"]))

    def pull_user_node(self,user_id:int) -> User:
        """
        Pulls all records for a user from their ID
        
        Args:
            user_id: PK for identifying the user
        Returns:
            User object with all records
        """
        with self.driver.session() as session:
            user = session.execute_write(self.pull_user_node_query, user_id)
            # print(user.books, user.reviews, user.want_to_read, user.authors, user.genres, user.reading, user.friends, user.username, user.created_date)
        return(user)
    @staticmethod
    def pull_user_node_query(tx,user_id): # TODO: Honestly redo this whole query shits garbage
        # TODO: 
        query = """
                match (u:User {id: $user_id})-[r]-(b) return TYPE(r),Labels(b),b.id,u.username,u.created_date,u.email,u.disabled
                """
        result = tx.run(query, user_id=user_id)
        user = User(user_id=user_id)
        for response in result:
            if response["TYPE(r)"] == "WROTE_REVIEW":
                user.reviews.append(response["b.id"])
            elif response["TYPE(r)"] == "TO_READ":
                user.want_to_read.append(response["b.id"])
            elif response["TYPE(r)"] == "IS_READING":
                user.reading.append(response["b.id"])
            elif response["TYPE(r)"] == "LIKES":
                if response["Labels(b)"] == ["Author"]:
                    user.authors.append(response["b.id"]) 
                elif response["Labels(b)"] == ["Genre"]:
                    user.genres.append(response["b.id"])
                elif response["Labels(b)"] == ["Review"]: # TODO: Fix this for new review types
                    user.liked_reviews.append(response["b.id"])
            elif response["TYPE(r)"] == "HAS_FRIEND":
                user.friends.append(response["b.id"])
            elif response["u.username"]:
                user.username = response["u.username"]
            elif response["u.created_date"]:
                user.created_date = response["u.created_date"]
            elif response["u.disabled"]:
                user.disabled = response["u.disabled"]
            elif response["u.email"]:
                user.email = response["u.email"]
        query = """
                match (uu:User {id: $user_id})-[rr:WROTE_REVIEW]-()-[ro:IS_REVIEW_OF]-(bb) return bb.id
                """
        result = tx.run(query, user_id=user_id)
        if result:
            for response in result:
                user.books.append(response["bb.id"])

        return(user)
    def add_favorite_genre(self, user_id, genre_id):
        """
        Adds a favorite genre for a user
        
        Args:
            user_id: users PK
            genre_id: genre's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_favorite_genre_query, user_id, genre_id)
    @staticmethod
    def add_favorite_genre_query(tx, user_id, genre_id):
        query = """
                match (uu:User {id: $user_id}) match (gg:Genre {id: $genre_id}) merge (uu)-[rr:LIKES]->(gg)
                """
        result = tx.run(query, user_id=user_id,genre_id=genre_id)
    def add_favorite_author(self, user_id, author_id):
        """
        Adds a favorite author for a user
        
        Args:
            user_id: users PK
            author_id: author's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_favorite_author_query, user_id, author_id)
    @staticmethod
    def add_favorite_author_query(tx, user_id, author_id):
        query = """
                match (uu:User {id: $user_id}) match (aa:Author {id: $author_id}) merge (uu)-[rr:LIKES]->(aa)
                """
        result = tx.run(query, user_id=user_id, author_id=author_id)
    def add_liked_post(self, username, post_id):
        """
        Adds a liked post for a user
        
        Args:
            username: users PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_liked_post_query, username, post_id)    
    @staticmethod
    def add_liked_post_query(tx, username, post_id):
        query = """
                match (uu:User {username: $username}) 
                match (rr {id: $post_id}) 
                with uu, rr
                where not exists ((uu)-[:LIKES]-(rr))
                    create (uu)-[ll:LIKES {created_date:datetime()}]->(rr)
                    set rr.likes = rr.likes + 1
                """
        result = tx.run(query, username=username, post_id=post_id)
    def add_to_read(self,user_id,book_id):
        """
        Adds a book to a users to_read. Deletes all other relationships to this book
        
        Args:
            user_id: users PK
            book_id: book's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_to_read_query, user_id, book_id)
    @staticmethod
    def add_to_read_query(tx, user_id, book_id):
        query = """
                match (uu:User {id: $user_id}) match (bb:Book {id: $book_id}) match (uu)-[old_r]->(bb) delete old_r merge (uu)-[tt:TO_READ]->(bb) 
                """
        result = tx.run(query, user_id=user_id, book_id=book_id)
    def add_reading(self,user_id,book_id):
        """
        Adds a book to a users currently reading. Deletes all other relationships to this book
        Args:
            user_id: users PK
            book_id: book's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_to_read_query, user_id, book_id)
    @staticmethod
    def add_reading_query(tx, user_id, book_id):
        query = """
                match (uu:User {id: $user_id}) match (bb:Book {id: $book_id}) match (uu)-[old_r]->(bb) delete old_r merge (uu)-[tt:IS_READING]->(bb) 
                """
        result = tx.run(query, user_id=user_id, book_id=book_id)

    def create_user(self, username, password):
        """
        Creates a new user in the database from a username. TODO: Add uniqueness constraint for usernames
        Args:
            username: Username for the new user
        Returns:
            User: user object for the created user
        """
        user_id = str(uuid.uuid4())
        with self.driver.session() as session:
            user = session.execute_write(self.create_user_query, username, user_id, password)
        return(user)
    @staticmethod
    def create_user_query(tx, username, user_id, password):
        query = """
                create (u:User {id:$user_id,username:$username,password:$password,created_date:datetime(),disabled:False}) return u.created_date
                """
        result = tx.run(query, user_id=user_id, username=username, password=password)
        response = result.single()
        user = User(user_id=user_id,username=username, hashed_password=password, disabled=False)
        user.created_date = response['u.created_date']
        return(user)

    def put_name_on_user(self, username, full_name):
        """
        Decorates a user instance with a name.
        Args:
            username: username for user.
            full_name: String for new full_name property on user instance
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.put_name_on_user_query, username, full_name)
    @staticmethod
    def put_name_on_user_query(tx, username, full_name):
        """
        Finds user by username and sets a full_name on user instance
        """
        query = """
                match (u:User {username:$username})
                set u.full_name = $full_name
                return u
                """
        result = tx.run(query, username=username, full_name=full_name)
        return result.single()
    
    def pull_book_node(self,book_id):
        """
        Pulls all the data from a book in the DB

        Args:
            book_id: PK of the book to pull
        Returns:
            Book: book object containing all the metadata
        """
        with self.driver.session() as session:
            book = session.execute_read(self.pull_book_node_query, book_id)
        return(book)
    @staticmethod
    def pull_book_node_query(tx,book_id):
        query = """
                match (b:Book {id:$book_id}) 
                match (b)-[r]-(g)
                return
                b.img_url, 
                b.isbn13,
                b.isbn10,
                b.lang, 
                b.originalPublicationYear, 
                b.pages, 
                b.small_img_url, 
                b.description, 
                b.title,
                TYPE(r),
                g.id
                """
        if len(book_id) <= 5:
            book_id = int(book_id)

        result = tx.run(query, book_id=book_id)
        response = result.single()

        book = Book(book_id=book_id,
                    img_url=response["b.img_url"],
                    small_img_url=response["b.small_img_url"],
                    pages=response["b.pages"],
                    publication_year=response["b.originalPublicationYear"],
                    lang=response["b.lang"],
                    title=response["b.title"],
                    description=response["b.description"],
                    isbn13 = response["b.isbn13"],
                    isbn10 = response["b.isbn10"])
        for response in result:
            if response['TYPE(r)'] == 'HAS_TAG':
                book.tags.append(response["g.id"])
            elif response['TYPE(r)'] == 'HAS_GENRE':
                book.genres.append(response["g.id"])
            elif response['TYPE(r)'] == 'IS_REVIEW_OF': ## TODO update this
                book.reviews.append(response["g.id"])
            elif response['TYPE(r)'] == 'WROTE':
                book.authors.append(response["g.id"])
        return(book)
    
    def create_book(self, title, img_url, pages, publication_year, lang, 
                    description='', genres=[], authors=[], isbn13=None, isbn10=None, 
                    small_img_url='', author_names=[],genre_names=[],google_id="",gr_id=""):
        """
        Creates a book node in the database

        Args:
            title: Title of the book
            img_url: link to an image of the cover
            pages: Number of pages in the book
            publication_year: Year the book was published
            lang: Language of the book
            description: Short description of the book
            genres: Genre IDs of the related genres
            authors: Author IDs of the authors who wrote the book
            isbn13: isbn13 number if applicable
            isbn10: isbn10 number if applicable
        Returns:
            Book: book object with all related metadata

        TODO: This uses a lot of queries rn can be made faster
        """

        if not genres:
            for genre_name in genre_names:
                result = self.find_genre_by_name(genre_name)
                if result:
                    genres.append(result)
                else:
                    result = self.create_genre(genre_name)
                    genres.append(result)
        
        if not authors:
            for author_name in author_names:
                result = self.find_author_by_name(author_name)
                if result:
                    authors.append(result)
                else:
                    result = self.create_author(author_name)
                    authors.append(result.id)

        with self.driver.session() as session:
            book_id = session.execute_write(self.create_book_query,
                                            title, 
                                            img_url, 
                                            pages, 
                                            publication_year, 
                                            lang, 
                                            description, 
                                            genres, 
                                            authors, 
                                            isbn13,
                                            isbn10, 
                                            small_img_url, 
                                            author_names,
                                            google_id,
                                            gr_id)
        return(book_id)
    @staticmethod
    def create_book_query(tx,title, img_url, 
                          pages, publication_year, lang, 
                          description, genres, authors, isbn13, isbn10,
                          small_img_url, author_names,google_id,gr_id):
        # Our IDs must start with C to distinguish them from google ids
        query = """
                create (b:Book {id:"c"+randomUUID(), 
                title:$title, 
                img_url:$img_url, 
                pages:$pages, 
                publication_year:$publication_year, 
                lang:$lang, 
                description:$description, 
                isbn13:$isbn13,
                isbn10:$isbn10,
                small_img_url:$small_img_url,
                author_names:$author_names,
                google_id:$google_id,
                gr_id:$gr_id})
                return b.id
                """
        # To avoid None Type errors. THE IS INSTANCE PART COULD BE TOTALLY USELESS CATCH IS THERE TO CHECK
        if isbn13:
            if not isinstance(isbn13,str):
                print(isbn13)
                isbn13 = isbn13[0]

        if isbn10:
            if not isinstance(isbn10,str):
                print(isbn10)
                isbn10 = isbn10[0]
        
        result = tx.run(query,
                        title=title, 
                        img_url=img_url, 
                        pages=pages, 
                        publication_year=publication_year, 
                        lang=lang, 
                        description=description, 
                        isbn13=isbn13,
                        isbn10=isbn10,
                        small_img_url=small_img_url,
                        author_names=author_names,
                        google_id=google_id,
                        gr_id=gr_id)
        
        response = result.single()
        book_id = response['b.id']

        query = """
                match (a:Author {id:$author_id})
                match (b:Book {id:$book_id})
                merge (a)-[w:WROTE]->(b)
                """
        for author in authors:
            result = tx.run(query, author_id=author, book_id=book_id)

        query = """
                match (g:Genre {id:$genre_id})
                match (b:Book {id:$book_id})
                merge (b)-[h:HAS_GENRE]->(g)
                """

        for genre in genres:
            result = tx.run(query, genre_id=genre, book_id=book_id)
                
        book = Book(book_id=book_id, 
                    title=title, 
                    img_url=img_url, 
                    pages=pages, 
                    publication_year=publication_year, 
                    lang=lang, 
                    description=description, 
                    isbn13=isbn13,
                    genres=genres,
                    gr_id=gr_id,
                    authors=authors)

        return(book)
    def add_user_book(self, book_ids, user_id):
        """
        Adds an array of book_ids to a user 
        Args: 
            book_id: Array containing pk's of the book
            user_id: Pk of the user
        Returns:
            None
        """
        with self.driver.session() as session:
            books = session.execute_write(self.add_user_books_query, book_ids, user_id)
    @staticmethod
    def add_user_books_query(tx, book_ids, user_id):
        get_unset_property_query = """
                match (u:User {id: $user_id})
                set u.book_ids = coalesce(u.book_ids, []) + $book_ids
                """
        tx.run(get_unset_property_query, user_id=user_id, book_ids=book_ids)
    def add_book_tag(self, book_id, tag_id):
        """
        Add a tag to an existing book
        Args:
            book_id: PK of the book
            tag_id: PK of the tag
        Returns:
            None
        """
        with self.driver.session() as session:
            book = session.execute_write(self.add_book_tag_query, book_id, tag_id)                
    @staticmethod
    def add_book_tag_query(tx, book_id, tag_id):
        query = """
                match (b:Book {id:$book_id})
                match (t:Tag {id:$tag_id})
                merge (b)-[h:HAS_TAG]->(t)
                """
        result = tx.run(query, book_id=book_id, tag_id=tag_id)
    def pull_author_node(self,author_id):
        """
        Pull all data about an author from the DB

        Args:
            author_id: PK of the author to query
        Returns:
            Author: Author object with all related metadata
        """
        with self.driver.session() as session:
            author = session.execute_write(self.pull_author_node_query, author_id)
        return(author)                
    @staticmethod
    def pull_author_node_query(tx,author_id):
        query = """
                match (a:Author {id:$author_id})-[w:WROTE]->(b:Book) return a.name, b.id
                """
        result = tx.run(query,author_id=author_id)
        author = Author(author_id=author_id,full_name="")
        for response in result:
            author.books.append(response["b.id"])
        author.full_name = response["a.name"]
        return(author)
    def pull_author_page_nodes(self, author_id):
        """
        Pulls all data about an author INCLUDING book info for cards, author info, and friends/influences
        Args:
            author_id
        Returns: Author object, Books corresponding to author
        """
        with self.driver.session() as session:
            author = session.execute_read(self.pull_author_page_nodes_query, author_id)
        return(author) 
    @staticmethod
    def pull_author_page_nodes_query(tx, author_id):
        query = """
                match (a:Author {id: $author_id})
                match (a)-[w:WROTE]->(b:Book)
                return a.id, a.name, b.id, b.description, b.title, b.publication_year, b.authors, b.img_url
                """
        result = tx.run(query, author_id=author_id)
        result_list = list(result)

        authors_books = [
            Book(
                author_names=response["a.name"],
                book_id=response["b.id"],
                title=response["b.title"],
                description=response["b.description"],
                publication_year=response["b.publication_year"],
                img_url=response["b.img_url"],
            )
        for response in result_list]

        
        author = Author(
                author_id=result_list[0]["a.id"],
                full_name=result_list[0]["a.name"],
                books=authors_books,
            )
        
        return(author)
    def create_author(self, full_name, books=[]):
        """
        Creates an author node in the DB

        Args:
            full_name: Full name of the author
            books:PKs of all book written by the author
        Returns:
            Author: Author object with all related metadata
        """
        with self.driver.session() as session:
            author = session.execute_write(self.create_author_query, full_name, books)
        return(author)
    @staticmethod
    def create_author_query(tx, full_name, books):
        # Creates the author node
        query = """
                create (a:Author {id:randomUUID(), name:$full_name})
                return a.id
                """
        result = tx.run(query, 
                        full_name=full_name)
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
        author = Author(author_id=author_id, full_name=full_name, books=books)
        return(author)
    def pull_genre_node(self,genre_id):
        """
        Pulls a genre node and its data from the database

        Args:
            genre_id: PK of the genre to query
        Returns:
            Genre: Genre object with all the related metadata
        """
        with self.driver.session() as session:
            genre = session.execute_write(self.pull_genre_node_query, genre_id)
        return(genre)
    @staticmethod
    def pull_genre_node_query(tx, genre_id):
        query = """
                match (g:Genre {id:$genre_id})-[r]-(b) return g.name, b.id
                """
        result = tx.run(query, genre_id=genre_id)
        genre = Genre(genre_id=genre_id,name="")
        for response in result:
            genre.books.append(response["b.id"])
        genre.name = response["g.name"]
        return(genre)
    def pull_tag_node(self,tag_id):
        """
        Pulls a tag node and its data from the database

        Args:
            tag_id: PK of the tag to query
        Returns:
            Tag: Tag object with all the related metadata
        """
        with self.driver.session() as session:
            tag = session.execute_write(self.pull_tag_node_query, tag_id)
        return(tag)
    @staticmethod
    def pull_tag_node_query(tx, tag_id):
        query = """
                match (t:Tag {id:$tag_id})-[r]-(b) return t.name, b.id
                """
        result = tx.run(query, tag_id=tag_id)
        tag = Tag(tag_id=tag_id,name="")
        for response in result:
            tag.books.append(response["b.id"])
        tag.name = response["t.name"]
        return(tag)
    def pull_book_titles(self):
        """
        Query returns the titles of all the books in the db
        Args:
            None
        Returns:
            Dict: All book titles
        """
        with self.driver.session() as session:
            books = session.execute_write(self.pull_book_titles_query)
        return(books)
    @staticmethod
    def pull_book_titles_query(tx):
        query = """
                match (b:Book) return b.title, b.id
                """
        result = tx.run(query)
        books = [Book(book_id=response['b.id'],title=response["b.title"]) for response in result]
        return(books)
    def pull_n_books(self, skip=int, limit=int, by_n=None):
        """
        Query returns entire books for a selected range(index's between skip and limit) in db in order to give faster responses
        
        Args:
            skip: index to start at
            limit: index to end at
        Returns:
            Dict: All book titles
        """
        with self.driver.session() as session:
            if by_n != None:
                books = session.execute_read(self.pull_n_books_query, skip, limit, by_n)
            else: 
                books = session.execute_read(self.pull_n_books_query, skip, limit)
            return(books)
    @staticmethod
    def pull_n_books_query(tx, skip, limit, by_n=None):
        if by_n == None:
            query = """
                    match (b:Book) return b.title, b.id, b.small_img_url, b.publication_year 
                    SKIP $skip
                    LIMIT $limit
                    """
            result = tx.run(query, skip=skip, limit=limit)
            books = [
                Book(
                    book_id=response['b.id'],
                    title=response['b.title'],
                    small_img_url=response['b.small_img_url'],
                    publication_year=response['b.publication_year']
                )
                for response in result
            ]
            
        if by_n == True: 
            query = """
                    match (b:Book) with b
                    match (a:Author)-[WROTE]->(b)
                    RETURN b.title, b.id, b.description, b.img_url, b.publication_year, b.isbn13, a
                    SKIP $skip
                    LIMIT $limit
                    """
            result = tx.run(query, skip=skip, limit=limit, by_n=by_n)
            # need to find a way to get count of reviews of books maybe like this: OPTIONAL MATCH (r:Review)-[h:IS_REVIEW_OF]->(b) return r 
            books = [
                Book(
                    book_id=response['b.id'],
                    title=response['b.title'],
                    img_url=response['b.img_url'],
                    publication_year=response['b.publication_year'],
                    description=response['b.description'],
                    isbn13=response['b.isbn13'],
                    author_names=response['a'],
                )
                for response in result
            ]
        return(books)
    def pull_search2_books(self, skip, limit, text):
        """
        Returns a partial book object for a small about of book using a text search term
        
        Args:
            skip: index to start at
            limit: index to end at
            text: text to search within the title
        Returns:
            Book: Partial book object with title, id, small_img_url,publicationYear, genre_names, and author_names
        """
        with self.driver.session() as session:
            books = session.execute_read(self.pull_search2_books_query, skip, limit, text)
        return(books)
    @staticmethod
    def pull_search2_books_query(tx, skip, limit, text):
        text = "(?i)" + "".join([f".*{word}.*" for word in text.split(" ")])
        query = """
                match (b:Book) where b.title =~ $text return b.title, b.id,b.small_img_url, b.originalPublicationYear
                SKIP $skip
                LIMIT $limit
                """
        result = tx.run(query, skip=skip, limit=limit, text=text)
        books = [
            {
                "book_id":response['b.id'],
                "title":response['b.title'],
                "small_img_url":response['b.small_img_url'],
                "publication_year":response['b.originalPublicationYear']
            }
            for response in result
        ]
        book_ids = [book['book_id']for book in books]
        books_zip = dict(zip(book_ids,books))
        query = """
                match (b:Book)-[r:HAS_GENRE|WROTE]-(g:Genre|Author) where b.id IN $book_ids return b.id, g.name, TYPE(r)
                """
        result = tx.run(query, book_ids=book_ids)
        for response in result:
            book_id = response['b.id']
            if response["TYPE(r)"] == "HAS_GENRE":
                if 'genre_names' not in books_zip[book_id].keys():
                    books_zip[book_id].update({"genre_names":[]}) 
                books_zip[book_id]['genre_names'].append(response["g.name"])
            elif response["TYPE(r)"] == "WROTE":
                if 'author_names' not in books_zip[book_id].keys():
                    books_zip[book_id].update({"author_names":[]}) 
                books_zip[book_id]['author_names'].append(response["g.name"])
        books = [
            Book(
                book_id=response['book_id'],
                title=response['title'],
                small_img_url=response['small_img_url'],
                publication_year=response['publication_year'],
                genre_names=response["genre_names"],
                author_names=response["author_names"])
            for response in books_zip.values()
        ]
        return(books)
    def pull_search2_genre(self, skip, limit, text):
        """
        Returns a  genre object for a small about of genre using a text search term
        
        Args:
            skip: index to start at
            limit: index to end at
            text: text to search within the title
        Returns:
            Genre: genre object with name and id
        """
        with self.driver.session() as session:
            books = session.execute_write(self.pull_search2_genre_query, skip, limit, text)
        return(books)
    @staticmethod
    def pull_search2_genre_query(tx, skip, limit, text):
        text = "(?i)" + "".join([f".*{word}.*" for word in text.split(" ")])
        query = """
                match (g:Genre) where g.name =~ $text return g.name, g.id
                SKIP $skip
                LIMIT $limit
                """
        result = tx.run(query, skip=skip, limit=limit, text=text)
        genres = [
                Genre(
                    genre_id=response['g.id'],
                    name=response['g.name'],
                )
                for response in result
            ]
        return(genres)
    def pull_search2_author(self, skip, limit, text):
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
            authors = session.execute_write(self.pull_search2_author_query, skip, limit, text)
        return(authors)
    @staticmethod
    def pull_search2_author_query(tx, skip, limit, text):
        text = "(?i)" + "".join([f".*{word}.*" for word in text.split(" ")])
        query = """
                match (a:Author) where a.name =~ $text return a.name, a.id
                SKIP $skip
                LIMIT $limit
                """
        result = tx.run(query, skip=skip, limit=limit, text=text)
        authors = [
                Author(
                    author_id=response['a.id'],
                    full_name=response['a.name'],
                )
                for response in result
            ]
        return(authors)
    def pull_user_by_username(self, username):
        """
        Returns a partial user object for password verification

        Args:
            username: username of the user to find
        Returns:
            User: Partial user object with username, id, password, and disabled
        """
        with self.driver.session() as session:
            user = session.execute_read(self.pull_user_by_username_query, username)
        return(user)
    @staticmethod
    def pull_user_by_username_query(tx, username):
        query = """
                match (u:User {username:$username}) return u.id, u.password, u.disabled
                """
        result = tx.run(query, username=username)
        response = result.single()
        if not response:
            return None
        user = User(
            username=username,
            user_id=response["u.id"],
            hashed_password=response["u.password"],
            disabled=response["u.disabled"]
        )
        return(user)
    @timing_decorator
    def pull_all_reviews_by_user(self, username): 
        with self.driver.session() as session:
            result = session.execute_read(self.pull_all_reviews_by_user_query, username)
        return(result)
    @staticmethod
    def pull_all_reviews_by_user_query(tx, username): # TODO: Not sure if this needs the posted_by_current_user decorator
        query = """ match (u:User {username:$username})-[r:POSTED]->(p {deleted:false})
                    optional match (p)-[rb:POST_FOR_BOOK]-(b)
                    optional match (p)-[ru:RECOMMENDED_TO]->(uu)
                    optional match (p)<-[rl:LIKES]-(u)
                    optional match (comments:Comment {deleted:false})<-[:HAS_COMMENT]-(p)
                    return p, labels(p), b, uu,
                    CASE WHEN rl IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
                    count(comments) as num_comments
                    order by p.created_date desc"""
        result = tx.run(query, username=username)
        results = [record for record in result.data()]
        
        output = {"Milestone":[],
                  "RecommendationFriend":[],
                  "Comparison":[],
                  "Update":[],
                  "Review":[]}
        
        for response in results:
            post = response['p']
            if response['labels(p)'] == ["Milestone"]:
                output['Milestone'].append(MilestonePost(post_id=post["id"],
                                                         book="",
                                                         created_date=post["created_date"],
                                                         num_books=post["num_books"],
                                                         user_username=username,
                                                         likes=post['likes'],
                                                         liked_by_current_user=response['liked_by_current_user'],
                                                         num_comments=response['num_comments']))                                                        
                
            elif response['labels(p)'] == ["RecommendationFriend"]:
                output['RecommendationFriend'].append(RecommendationFriend(post_id=post["id"],
                                                                           book=response['b']['id'],
                                                                           created_date=post["created_date"],
                                                                           to_user_username=response['uu']['username'],
                                                                           from_user_text=post['from_user_text'],
                                                                           to_user_text=post['to_user_text'],
                                                                           user_username=username,
                                                                           likes=post["likes"],
                                                                           liked_by_current_user=response['liked_by_current_user'],
                                                                           num_comments=response['num_comments']))
            
            elif response['labels(p)'] == ['Comparison']:
                if output['Comparison']:
                    if output['Comparison'][-1].id == post["id"]:
                        output['Comparison'][-1].compared_books.append(response['b']['id'])
                        output['Comparison'][-1].book_title.append(response['b']['title'])
                        output['Comparison'][-1].book_small_img.append(response['b']['small_img_url'])
                        continue

                output['Comparison'].append(ComparisonPost(post_id=post["id"],
                                            compared_books=[response['b']['id']],
                                            user_username=username,
                                            comparators=post['comparators'],
                                            created_date=post['created_date'],
                                            comparator_ids=post['comparator_ids'],
                                            responses=post['responses'],
                                            book_specific_headlines=post['book_specific_headlines'],
                                            book_title=[response['b']['title']],
                                            book_small_img=[response['b']['small_img_url']],
                                            likes=post['likes'],
                                            liked_by_current_user=response['liked_by_current_user'],
                                            num_comments=response['num_comments']))


            elif response['labels(p)'] == ["Update"]:
                output['Update'].append(UpdatePost(post_id=post["id"],
                                                   book=response['b']['id'],
                                                   book_title=response['b']['title'],
                                                   created_date=post["created_date"],
                                                   page=post['page'],
                                                   response=post['response'],
                                                   spoiler=post['spoiler'],
                                                   book_small_img=response['b']['small_img_url'],
                                                   user_username=username,
                                                   likes=post['likes'],
                                                   liked_by_current_user=response['liked_by_current_user'],
                                                   num_comments=response['num_comments']))

            elif response['labels(p)'] == ["Review"]:
                    
                    output['Review'].append(ReviewPost(post_id=post["id"],
                                                       book=response['b']['id'],
                                                       book_title=response['b']['title'],
                                                       created_date=post["created_date"],
                                                       questions=post['questions'],
                                                       question_ids=post['question_ids'],
                                                       responses=post['responses'],
                                                       spoilers=post['spoilers'],
                                                       book_small_img=response['b']['small_img_url'],
                                                       user_username=username,
                                                       liked_by_current_user=response['liked_by_current_user'],
                                                       num_comments=response['num_comments'],
                                                       likes=post['likes']
                                                      ))

        return(output)
        
    def search_for_param(self, param, skip, limit):
        """
        Adds a query to search for nodes with titles that match a given request
        we need to figure out how to put a  limit on these
        """
        with self.driver.session() as session:
            results = session.execute_read(self.search_for_param_query, param, skip, limit)
        return results
    
    @staticmethod
    def search_for_param_query(tx, param, skip, limit):
        param = "(?i)" + "".join([f".*{word.lower()}.*" for word in param.split(" ")])
        query = """
                OPTIONAL MATCH (u:User)
                WHERE toLower(u.username) =~ $param
                WITH u.username AS user, null AS author, null AS book, null AS book_genre, null AS book_author
                WHERE u IS NOT NULL
                RETURN book_genre, user, author, book, book_author
                LIMIT $limit

                UNION

                OPTIONAL MATCH (a:Author)
                WHERE toLower(a.name) =~ $param
                WITH null AS user, a AS author, null AS book, null AS book_genre, null AS book_author
                WHERE a IS NOT NULL
                RETURN book_genre, user, author , book, book_author
                LIMIT $limit

                // UNION

                // OPTIONAL MATCH (b:Book)
                // WHERE toLower(b.title) =~ $param
                // WITH null AS user, null AS author, b AS book, null AS book_genre, null AS book_author
                // WHERE b IS NOT NULL
                // RETURN book_genre, user, author, book, book_author
                // LIMIT $limit

                UNION

                OPTIONAL MATCH (bb:Book)-[r:HAS_GENRE]-(g:Genre)
                WHERE toLower(g.name) =~ $param
                WITH null AS user, null AS author, null AS book, bb AS book_genre, null AS book_author
                WHERE bb IS NOT NULL
                RETURN book_genre, user, author, book, book_author
                LIMIT $limit

                UNION

                OPTIONAL MATCH (bbb:Book)-[r:WROTE]-(aa:Author)
                WHERE toLower(bbb.title) =~ $param
                WITH null AS user, null AS author, null AS book, null AS book_genre, aa AS book_author
                WHERE aa IS NOT NULL
                RETURN null AS book_genre, user, author, book, book_author
                LIMIT $limit
                """
        
        result = tx.run(query, param=param, skip=skip, limit=limit)
        res_obj = {}
        res_obj['books'] = []
        res_obj['authors'] = []
        res_obj['books_by_genre'] = []
        res_obj['books_by_author'] = []
        res_obj['users'] = []

        for response in result:
            if response != None:
                if response['book'] != None:
                    res_obj['books'].append(response[3])
                if response['author'] != None:
                    res_obj['authors'].append(response[2])
                if response['book_genre'] != None:
                    res_obj['books_by_genre'].append(response[0])
                if response['book_author'] != None:
                    res_obj['books_by_author'].append(response[4])
                if response['user'] != None:
                    res_obj['users'].append(response[1])

        return res_obj

    def pull_similar_books(self, book_id:int):
        """
        Find similar books in the database using book id
        """
        with self.driver.session() as session:
            result = session.execute_read(self.pull_similar_books_query, book_id)
        return(result)
    @staticmethod
    def pull_similar_books_query(tx, book_id):
        query = "match (b:Book {id:$book_id})-[rr:SIMILAR_TO]->(bb:Book) return bb.id,bb.title,bb.img_url"
        result = tx.run(query,book_id=book_id)
        result = [{"id":response["bb.id"],"title":response["bb.title"],"img_url":response["bb.img_url"]} for response in result]
        return(result)
    def find_book_by_isbn13(self,isbn13:int):
        """
        Finds a book by its isbn number
        """
        with self.driver.session() as session:
            result = session.execute_read(self.find_book_by_isbn13_query, isbn13)
        return(result)
    @staticmethod
    def find_book_by_isbn13_query(tx,isbn13):
        query = "match (bb:Book {isbn13:$isbn13})-[WROTE]-(a:Author) return bb.id,bb.title,bb.small_img_url,bb.img_url,bb.description,a.name"
        result = tx.run(query,isbn13=isbn13)
        response = result.single()
        if response:
            book = Book(response['bb.id'],
                        img_url=response['bb.img_url'],
                        small_img_url=response['bb.small_img_url'],
                        title=response['bb.title'],
                        description=response['bb.description']
                 )
            [book.author_names.append(response['a.name']) for response in result]
            return(book)
        else:
            return(None)
    def find_book_by_isbn10(self,isbn10:int):
        """
        Finds a book by its isbn number
        """
        with self.driver.session() as session:
            result = session.execute_read(self.find_book_by_isbn10_query, isbn10)
        return(result)
    @staticmethod
    def find_book_by_isbn10_query(tx,isbn10):
        query = "match (bb:Book {isbn10:$isbn10})-[WROTE]-(a:Author) return bb.id,bb.title,bb.small_img_url,bb.img_url,bb.description,a.name"
        result = tx.run(query,isbn10=isbn10)
        response = result.single()
        if response:
            book = Book(response['bb.id'],
                        img_url=response['bb.img_url'],
                        small_img_url=response['bb.small_img_url'],
                        title=response['bb.title'],
                        description=response['bb.description']
                 )
            [book.author_names.append(response['a.name']) for response in result]
            return(book)
        else:
            return(None)
    def find_genre_by_name(self,name):
        """
        Checks if a genre exists in the DB by name
        """
        with self.driver.session() as session:
            result = session.execute_read(self.find_genre_by_name_query, name)
        return(result)
    @staticmethod
    def find_genre_by_name_query(tx,name):
        query = "match (g:Genre {name:$name}) return g.id"
        result = tx.run(query,name=name)
        response = result.single()
        if response:
            return(response['g.id'])
        else:
            return(None)
        
    def create_genre(self,name):
        """
        Checks if a genre exists in the DB by name
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
    
    def find_author_by_name(self,name):
        """
        Checks if an author exists in the DB by name
        """
        with self.driver.session() as session:
            result = session.execute_read(self.find_author_by_name_query, name)
        return(result)
    @staticmethod
    def find_author_by_name_query(tx,name):
        query = "match (a:Author {name:$name}) return a.id"
        result = tx.run(query,name=name)
        response = result.single()
        if response:
            return(response['a.id'])
        else:
            return(None)
    

    def get_user_for_settings(self, user_id, relationship_to_current_user):
        """
        gets id of user and returns full user object
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_user_for_settings_query, user_id, relationship_to_current_user)
        return(result)
    
    @staticmethod
    def get_user_for_settings_query(tx, user_id, relationship_to_current_user):
        query = """
            match(u:User {id:$user_id}) 
            return u
        """
        result = tx.run(query, user_id=user_id, relationship_to_current_user=relationship_to_current_user)
        response = result.single()
        user = User(
            user_id=response['u']['id'],
            username=response['u']['username'],
            email=response['u']['email'] or '',
            full_name=response['u']['fullname'] or '',
            created_date=response['u']['created_date'],
            profile_img_url=response['u']['profile_img_url'] or '',
            bio=response['u']['bio'] or '',
            relationship_to_current_user=response['u']['relationship_to_current_user'] or relationship_to_current_user,
        )
        return user

    def get_book_by_google_id(self,google_id):
        """
        Finds a book by google id if in db

        Args:
            google_id: Google id of the book to pull
        Returns:
            Book: book object containing all the metadata
        """
        with self.driver.session() as session:
            book = session.execute_read(self.get_book_by_google_id_query, google_id)
        return(book)
    @staticmethod
    def get_book_by_google_id_query(tx,google_id):
        query = """
                match (b:Book {id:$google_id}) 
                match (b)-[r]-(g)
                return b.gr_id,
                b.id, 
                b.img_url, 
                b.isbn13,
                b.isbn10,
                b.lang, 
                b.originalPublicationYear, 
                b.pages, 
                b.small_img_url, 
                b.description, 
                b.title,
                TYPE(r),
                g.id
                """
        result = tx.run(query, google_id=google_id)
        response = result.single()
        if response:
            book = Book(book_id=response["b.id"], 
                        gr_id=response["b.gr_id"], 
                        img_url=response["b.img_url"],
                        small_img_url=response["b.small_img_url"],
                        pages=response["b.pages"],
                        publication_year=response["b.originalPublicationYear"],
                        lang=response["b.lang"],
                        title=response["b.title"],
                        description=response["b.description"],
                        isbn13 = response["b.isbn13"],
                        isbn10 = response["b.isbn10"])
            for response in result:
                if response['TYPE(r)'] == 'HAS_TAG':
                    book.tags.append(response["g.id"])
                elif response['TYPE(r)'] == 'HAS_GENRE':
                    book.genres.append(response["g.id"])
                elif response['TYPE(r)'] == 'IS_REVIEW_OF':
                    book.reviews.append(response["g.id"])
                elif response['TYPE(r)'] == 'WROTE':
                    book.authors.append(response["g.id"])
            return(book)
        else:
            return(None)
        
    def get_book_by_google_id_flexible(self,google_id):
        """
        Finds a book by google id if in db.

        This is the more flexible version, search for the google id in both the ID and google_id fields

        Args:
            google_id: Google id of the book to pull
        Returns:
            Book: book object containing all the metadata
        """
        with self.driver.session() as session:
            book = session.execute_read(self.get_book_by_google_id_flexible_query, google_id)
        return(book)
    @staticmethod
    def get_book_by_google_id_flexible_query(tx,google_id):
        query = """
                match (book:Book)
                WHERE book.id = $google_id OR book.google_id = $google_id
                OPTIONAL MATCH (canonical:Book)-[:HAS_VERSION]->(book)
                WITH COALESCE(canonical, book) AS b
                match (b)-[r]-(g)
                return b.gr_id,
                b.id, 
                b.img_url, 
                b.isbn13,
                b.isbn10,
                b.lang, 
                b.originalPublicationYear, 
                b.pages, 
                b.small_img_url, 
                b.description, 
                b.title,
                b.author_names,
                TYPE(r),
                g.id
                """
        result = tx.run(query, google_id=google_id)
        response = result.single()
        if response:
            book = Book(book_id=response["b.id"], 
                        gr_id=response["b.gr_id"], 
                        img_url=response["b.img_url"],
                        small_img_url=response["b.small_img_url"],
                        pages=response["b.pages"],
                        publication_year=response["b.originalPublicationYear"],
                        lang=response["b.lang"],
                        title=response["b.title"],
                        description=response["b.description"],
                        isbn13 = response["b.isbn13"],
                        isbn10 = response["b.isbn10"],
                        author_names=response["b.author_names"],
                        google_id=google_id)
            for response in result:
                if response['TYPE(r)'] == 'HAS_TAG':
                    book.tags.append(response["g.id"])
                elif response['TYPE(r)'] == 'HAS_GENRE':
                    book.genres.append(response["g.id"])
                elif response['TYPE(r)'] == 'IS_REVIEW_OF':
                    book.reviews.append(response["g.id"])
                elif response['TYPE(r)'] == 'WROTE':
                    book.authors.append(response["g.id"])
            return(book)
        else:
            return(None)
        
    def get_id_by_google_id(self,google_id):
        """
        Uses the google id to find the id, title, and small_img_url in our db TODO: Same Coalese with canonical
        """
        with self.driver.session() as session:
            book = session.execute_read(self.get_id_by_google_id_query, google_id)
        return(book)
    @staticmethod
    def get_id_by_google_id_query(tx,google_id):
        query = """
                match (book:Book)
                WHERE book.google_id = $google_id or book.id = $google_id
                OPTIONAL MATCH (canonical:Book)-[:HAS_VERSION]->(book)
                WITH COALESCE(canonical, book) AS b
                return b.id, b.title, b.small_img_url
                """
        result = tx.run(query, google_id=google_id)
        response = result.single()
        if response:
            return ({"id":response["b.id"], "title":response["b.title"], "small_img_url":response["b.small_img_url"]})
        else:
            return None
        
        
    def create_review(self, review_post:ReviewPost):
        """
        Creates a review in the database
        Args:
            review_post:ReviewPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            review_id: PK of the review_post in DB
        """
        with self.driver.session() as session:
            created_date,review_id = session.execute_write(self.create_review_query, review_post)
        return(created_date,review_id)
    @staticmethod
    def create_review_query(tx, review_post):
        query = """
                match (u:User {username:$username})
                merge (b:Book {id:$book_id, title:$title, small_img_url:$small_img_url})
                create (r:Review {id:randomUUID(), 
                                created_date:datetime(),
                                headline:$headline,
                                questions:$questions,
                                question_ids:$question_ids,
                                responses:$responses,
                                spoilers:$spoilers,
                                deleted:false,
                                likes:0})
                create (u)-[p:POSTED]->(r)
                create (r)-[pp:POST_FOR_BOOK]->(b)
                return r.created_date, r.id
                """
        result = tx.run(query, 
                        username=review_post.user_username, 
                        book_id=review_post.book, 
                        headline=review_post.headline, 
                        questions=review_post.questions,
                        question_ids=review_post.question_ids,
                        responses=review_post.responses,
                        spoilers=review_post.spoilers, 
                        title=review_post.book_title,
                        small_img_url=review_post.book_small_img)
        
        response = result.single()
        created_date = response["r.created_date"]
        review_id = response['r.id']
        return(created_date, review_id)
    
    def create_update(self, update_post:UpdatePost):
        """
        Creates a review in the database
        Args:
            update_post: UpdatePost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            update_id: PK of the update in the db
        """
        with self.driver.session() as session:
            created_date, update_id = session.execute_write(self.create_update_query, update_post)
        return(created_date,update_id)
    @staticmethod
    def create_update_query(tx, update_post):
        query = """
            match (u:User {username:$username})
            merge (b:Book {id:$book_id, title:$title, small_img_url:$small_img_url})
            create (d:Update {id:randomUUID(), 
                            created_date:datetime(),
                            page:$page,
                            headline:$headline,
                            response:$response,
                            spoiler:$spoiler,
                            deleted:false,
                            likes:0})
            create (u)-[p:POSTED]->(d)
            create (d)-[pp:POST_FOR_BOOK]->(b)
            return d.created_date, d.id
                """
        result = tx.run(query, 
                        username=update_post.user_username, 
                        book_id=update_post.book, 
                        page=update_post.page, 
                        headline=update_post.headline, 
                        response=update_post.response,
                        spoiler=update_post.spoiler, 
                        title=update_post.book_title, 
                        small_img_url=update_post.book_small_img)
        
        response = result.single()
        created_date = response["d.created_date"]
        update_id = response["d.id"]
        return(created_date, update_id)
    
    def create_comparison(self, comparison_post:ComparisonPost):
        """
        Creates a review in the database
        Args:
            comparison_post: ComparisonPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            comparison_id: PK of the comparison in the db
        """
        with self.driver.session() as session:
            created_date, comparison_id = session.execute_write(self.create_comparison_query, comparison_post)
        return(created_date,comparison_id)
    @staticmethod
    def create_comparison_query(tx, comparison_post):
        query = """
        match (u:User {username:$username})
        merge (b:Book {id:$book_id_1, title:$title_1, small_img_url:$small_img_url_1})
        merge (bb:Book {id:$book_id_2, title:$title_2, small_img_url:$small_img_url_2})
        create (c:Comparison {id:randomUUID(), 
                            created_date:datetime(),
                            comparator_ids:$comparator_ids,
                            comparators:$comparators,
                            responses:$responses,
                            book_specific_headlines:$book_specific_headlines,
                            deleted:false,
                            likes:0})

        create (u)-[p:POSTED]->(c)
        create (c)-[pp:POST_FOR_BOOK]->(b)
        create (c)-[cc:POST_FOR_BOOK]->(bb)

        return c.created_date, c.id
                """
        result = tx.run(query, 
                        username=comparison_post.user_username, 
                        book_id_1=comparison_post.book[0],
                        book_id_2=comparison_post.book[1],
                        title_1=comparison_post.book_title[0],
                        title_2=comparison_post.book_title[1],
                        small_img_url_1=comparison_post.book_small_img[0],
                        small_img_url_2=comparison_post.book_small_img[1],
                        compared_books=comparison_post.book, 
                        comparators=comparison_post.comparators,
                        comparator_ids=comparison_post.comparator_ids,
                        responses=comparison_post.responses,
                        book_specific_headlines=comparison_post.book_specific_headlines)
        
        response = result.single()
        created_date = response["c.created_date"]
        comparison_id = response["c.id"]
        return(created_date,comparison_id)
    
    def create_recommendation_post(self, recommendation_post:RecommendationFriend):
        """
        Creates a review in the database
        Args:
            recommendation_post: RecommendationFriend object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            recommendation_id: PK of the recommendation in the db
        """
        with self.driver.session() as session:
            created_date,recommendation_id = session.execute_write(self.create_recommendation_post_query, recommendation_post)
        return(created_date,recommendation_id)
    @staticmethod
    def create_recommendation_post_query(tx, recommendation_post):
        query = """
        match (u:User {username:$username})
        match (f:User {username:$to_user_username})
        merge (b:Book {id:$book_id, title:$title, small_img_url:$small_img_url})
        create (r:RecommendationFriend {id:randomUUID(), 
                                        created_date:datetime(),
                                        from_user_text:$from_user_text,
                                        to_user_text:$to_user_text,
                                        deleted:false,
                                        likes:0})
        create (u)-[p:POSTED]->(r)
        create (r)-[rr:RECOMMENDED_TO]->(f)
        create (r)-[pp:POST_FOR_BOOK]->(b)
        return r.created_date, r.id
        """
        result = tx.run(query, 
                        username=recommendation_post.user_username, 
                        book_id=recommendation_post.book,
                        title=recommendation_post.book_title,
                        small_img_url=recommendation_post.book_small_img,
                        to_user_username=recommendation_post.to_user_username,
                        from_user_text=recommendation_post.from_user_text, 
                        to_user_text=recommendation_post.to_user_text)
        
        response = result.single()
        created_date = response["r.created_date"]
        recommendation_id = response["r.id"]
        return(created_date,recommendation_id)
    
    def create_milestone(self, milestone_post:MilestonePost):
        """
        Creates a review in the database
        Args:
            milestone_post: MilestonePost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            milestone_id: PK of the milestone in the db
        """
        with self.driver.session() as session:
            created_date,milestone_id = session.execute_write(self.create_milestone_query, milestone_post)
        return(created_date,milestone_id)
    @staticmethod
    def create_milestone_query(tx, milestone_post):
        query = """
        match (u:User {username:$username})
        create (m:Milestone {id:randomUUID(),
                            created_date:datetime(),
                            num_books:$num_books,
                            deleted:false,
                            likes:0
        })
        create (u)-[r:POSTED]->(m)
        return m.created_date, m.id
        """
        result = tx.run(query, 
                        username=milestone_post.user_username,
                        num_books=milestone_post.num_books)
        response = result.single()
        created_date = response["m.created_date"]
        milestone_id = response["m.id"]
        return(created_date,milestone_id)

    def create_comment(self, comment:Comment):
        """
        Creates a comment in the database
        Args:
            comment: Comment object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            comment_id: PK of the comment in the db
        """
        with self.driver.session() as session:
            created_date,comment_id = session.execute_write(self.create_comment_query, comment)
        return(created_date,comment_id)
    @staticmethod
    def create_comment_query(tx, comment):
        query_w_reply = """
        match (pp {id:$post_id, deleted:false})
        match (u:User {username:$username})
        MATCH (parent:Comment {id: $replied_to, deleted:false})
        create (c:Comment {
            id:randomUUID(),
            created_date:datetime(),
            text:$text,
            likes:0,
            is_reply:True,
            deleted:false
        })
        merge (pp)-[h:HAS_COMMENT]->(c)
        merge (u)-[cc:COMMENTED]->(c)
        MERGE (c)-[:REPLIED_TO]->(parent)

        return c.id, c.created_date
        """
        query_no_reply = """
        match (pp {id:$post_id, deleted:false})
        match (u:User {username:$username})
        create (c:Comment {
            id:randomUUID(),
            created_date:datetime(),
            text:$text,
            likes:0,
            is_reply:False,
            deleted:false
        })
        merge (pp)-[h:HAS_COMMENT]->(c)
        merge (u)-[cc:COMMENTED]->(c)

        return c.id, c.created_date
        """
        if comment.replied_to:
            result = tx.run(query_w_reply, 
                            post_id = comment.post_id,
                            replied_to = comment.replied_to,
                            text = comment.text,
                            username = comment.username)
        else:
            result = tx.run(query_no_reply, 
                            post_id = comment.post_id,
                            text = comment.text,
                            username = comment.username)
        
        if result:
            response = result.single()
            comment_id = response["c.id"]
            created_date = response["c.created_date"]
        else:
            created_date = None
            comment_id = None
        return(comment_id, created_date)

    def get_post(self, post_id, username):
        """
        Returns a post by UUID. Works for post types Update, Comparison, Review, and Milestone
        Also returns the book objects
        """
        with self.driver.session() as session:
            data = session.execute_read(self.get_post_query, post_id, username)
        return(data)
    @staticmethod
    def get_post_query(tx, post_id, username):
        query = """
            match (p {id:$post_id, deleted:false})
            match (cu:User {username:$username})
            match (p)-[:POST_FOR_BOOK]-(b:Book)
            match (pu:User)-[pr:POSTED]->(p)
            optional match (cu:User)-[lr:LIKES]->(p)
            return p, labels(p), b.id, b.title, b.small_img_url, pu.username, pu.id,
            CASE WHEN lr IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
            CASE WHEN pu.username = $username THEN true ELSE false END AS posted_by_current_user
        """

        result = tx.run(query, post_id=post_id, username=username)
        result = [record for record in result.data()]
        response = result[0]
        post = response['p']

        user_id = response["pu.id"]

        if response['labels(p)'] == ["Milestone"]:
            output = MilestonePost(post_id=post["id"],
                                    book="",
                                    created_date=post["created_date"],
                                    num_books=post["num_books"],
                                    user_username=response["pu.username"],
                                    likes=post['likes'],
                                    liked_by_current_user=response['liked_by_current_user'],
                                    posted_by_current_user=response['posted_by_current_user'])                                                        
            
        elif response['labels(p)'] == ['Comparison']:
            book_ids = []
            book_titles = []
            book_small_img_urls = []
            
            for response in result:
                book_ids.append(response['b.id'])
                book_titles.append(response['b.title'])
                book_small_img_urls.append(response['b.small_img_url'])

            output = ComparisonPost(post_id=post["id"],
                            compared_books=book_ids,
                            user_username=response["pu.username"],
                            comparators=post['comparators'],
                            created_date=post['created_date'],
                            comparator_ids=post['comparator_ids'],
                            responses=post['responses'],
                            book_specific_headlines=post['book_specific_headlines'],
                            book_title=book_titles,
                            book_small_img=book_small_img_urls,
                            likes=post['likes'],
                            liked_by_current_user=response['liked_by_current_user'],
                            posted_by_current_user=response['posted_by_current_user']
                            )
            
        elif response['labels(p)'] == ["Update"]:

            output = UpdatePost(post_id=post["id"],
                                book=response['b.id'],
                                book_title=response['b.title'],
                                created_date=post["created_date"],
                                page=post['page'],
                                response=post['response'],
                                spoiler=post['spoiler'],
                                book_small_img=response['b.small_img_url'],
                                user_username=response["pu.username"],
                                likes=post['likes'],
                                liked_by_current_user=response['liked_by_current_user'],
                                posted_by_current_user=response['posted_by_current_user']
                                )

        elif response['labels(p)'] == ["Review"]:
                output = ReviewPost(post_id=post["id"],
                                    book=response['b.id'],
                                    book_title=response['b.title'],
                                    created_date=post["created_date"],
                                    questions=post['questions'],
                                    question_ids=post['question_ids'],
                                    responses=post['responses'],
                                    spoilers=post['spoilers'],
                                    book_small_img=response['b.small_img_url'],
                                    user_username=response["pu.username"],
                                    likes=post['likes'],
                                    liked_by_current_user=response['liked_by_current_user'],
                                    posted_by_current_user=response['posted_by_current_user']
                                    )
                
        return({"post": output, "user_id": user_id})
    
    def add_liked_comment(self, username, comment_id):
        """
        Adds a liked comment for a user
        
        Args:
            username: users PK
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_liked_comment_query, username, comment_id)    
    @staticmethod
    def add_liked_comment_query(tx, username, comment_id):
        query = """
                match (uu:User {username: $username}) 
                match (rr:Comment {id: $comment_id})
                with uu, rr
                where not exists ((uu)-[:LIKES]-(rr))
                    create (uu)-[ll:LIKES {created_date:datetime()}]->(rr)
                    set rr.likes = rr.likes + 1
                """
        result = tx.run(query, username=username, comment_id=comment_id)
    def get_all_replies_for_comment(self, comment_id, username):
        """
        get all replies for a specific comment
        """
        with self.driver.session() as session:
            comments = session.execute_read(self.get_all_replies_for_comment_query, comment_id, username)
        return(comments)
    @staticmethod
    def get_all_replies_for_comment_query(tx, comment_id, username):
        query = """
            match (currentUser:User {username:$username})
            match (cr:Comment {deleted:false})-[REPLIED_TO]->(c:Comment {id: $comment_id, deleted:false})
            match (p {deleted:false})-[HAS_COMMENT]->(cr)
            match (commenter:User)-[COMMENTED]->(cr)
            optional match (currentUser)-[likedReply:LIKES]->(cr)
            return cr, commenter.username, p.id, commenter.id,
            CASE WHEN likedReply IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
            Case when commenter.username = $username then true else false END as posted_by_current_user
        """
        result = tx.run(query, comment_id=comment_id, username=username)
        comments = []
        for response in result:
            comments.append(Comment(
                comment_id=response['cr']['id'],
                replied_to=comment_id,
                text=response['cr']['text'],
                likes=response['cr']['likes'],
                created_date=response['cr']['created_date'],
                username=response['commenter.username'],
                user_id=response['commenter.id'],
                post_id=response["p.id"],
                liked_by_current_user=response["liked_by_current_user"],
                posted_by_current_user=response["posted_by_current_user"]
            ))
        return(comments)

    def get_all_comments_for_post(self, post_id, username, skip, limit):
        """
        Gets all the comments on the post. For comments in a thread, returns the number of comments in the thread
        as well as the most liked reply.

        Load in batches, so only 5 comments at a time, in order from most recent to least recent

        Also return if the current user has liked each of the comments

        Args:
            post_id: PK of the post for which to return comments    
            username: username of the current user
            skip: Low index of comments to grab
            limit: high index of comments to grab 
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_all_comments_for_post_query, post_id, username, skip, limit)  
        return(result)
    @staticmethod
    def get_all_comments_for_post_query(tx, post_id, username, skip, limit):
        query = """
                match (uu:User {username: $username}) 
                match (rr {id: $post_id, deleted:false}) 
                match (rr)-[r:HAS_COMMENT]->(c:Comment {is_reply:false, deleted:false})
                // Find the user who commented the parent comment
                MATCH (commenter:User)-[:COMMENTED]->(c)
                OPTIONAL MATCH (rcc:Comment {deleted:false})-[rrr:REPLIED_TO]->(c)
                with count(rcc) as num_replies, uu, rr, r, c, commenter
                OPTIONAL MATCH (rc:Comment {deleted:false})-[rrr:REPLIED_TO]->(c)
                // Find the user who commented the reply
                OPTIONAL MATCH (replyCommenter:User)-[:COMMENTED]->(rc)
                // Check if user with <username> has liked the parent comment
                OPTIONAL MATCH (uu)-[likedParent:LIKES]->(c)
                // Check if user with <username> has liked the reply
                OPTIONAL MATCH (uu)-[likedReply:LIKES]->(rc)
                WITH c, rr, r, rc, rrr, uu, likedParent, likedReply, commenter, replyCommenter, num_replies
                ORDER BY rc.likes DESC, rc.created_date ASC
                WITH c, rr, r, COLLECT(rc)[0] AS top_liked_reply, COLLECT(rrr)[0] AS topLikedRel, uu, 
                    COLLECT(likedParent)[0] AS likedParentRel, COLLECT(likedReply)[0] AS likedReplyRel, 
                    commenter, COLLECT(replyCommenter)[0] AS top_reply_commenter, num_replies
                RETURN c, top_liked_reply,
                    CASE WHEN likedParentRel IS NOT NULL THEN true ELSE false END AS parent_liked_by_user,
                    CASE WHEN likedReplyRel IS NOT NULL THEN true ELSE false END AS reply_liked_by_user,
                    commenter.username,
                    commenter.id,
                    top_reply_commenter.username,
                    top_reply_commenter.id,
                    case when commenter.username = $username then true else false END as parent_posted_by_user,
                    case when top_reply_commenter.username = $username then true else false END as reply_posted_by_user,
                    num_replies
                order by c.created_date desc
                skip $skip
                limit $limit
                """
        result = tx.run(query, username=username, post_id=post_id, skip=skip, limit=limit)
        # result = [record for record in result.data()]

        comment_response = []
        pinned_comment_response = []
        for response in result:
            if not response['c']['pinned']:
                comment = Comment(comment_id=response['c']['id'],
                                post_id=post_id,
                                replied_to=None,
                                text=response['c']['text'],
                                username=response['commenter.username'],
                                user_id=response['commenter.id'],
                                created_date=response['c']['created_date'],
                                likes=response['c']['likes'],
                                pinned=response['c']['pinned'],
                                liked_by_current_user=response['parent_liked_by_user'],
                                posted_by_current_user=response['parent_posted_by_user'],
                                num_replies=response["num_replies"])
                
                response_entry = {"comment":comment,
                                "liked_by_current_user":response['parent_liked_by_user'],
                                "replies":[]}
                
                if response['top_liked_reply']:
                    reply = Comment(comment_id=response['top_liked_reply']['id'],
                                    post_id=post_id,
                                    replied_to=response["c"]["id"],
                                    text=response["top_liked_reply"]['text'],
                                    username=response['top_reply_commenter.username'],
                                    user_id=response['top_reply_commenter.id'],
                                    created_date=response["top_liked_reply"]["created_date"],
                                    likes=response['top_liked_reply']['likes'],
                                    pinned=response['top_liked_reply']['pinned'],
                                    liked_by_current_user=response['reply_liked_by_user'],
                                    posted_by_current_user=response['reply_posted_by_user'])
                    response_entry['replies'].append({
                                                "comment":reply,
                                                "liked_by_current_user":response["reply_liked_by_user"],
                                                "replies":[]
                                            })

                comment_response.append(response_entry)
            else:
                comment = Comment(comment_id=response['c']['id'],
                                post_id=post_id,
                                replied_to=None,
                                text=response['c']['text'],
                                username=response['commenter.username'],
                                user_id=response['commenter.id'],
                                created_date=response['c']['created_date'],
                                likes=response['c']['likes'],
                                pinned=response['c']['pinned'],
                                liked_by_current_user=response['parent_liked_by_user'],
                                posted_by_current_user=response['parent_posted_by_user'],
                                num_replies=response["num_replies"])
                
                response_entry = {"comment":comment,
                                "liked_by_current_user":response['parent_liked_by_user'],
                                "replies":[]}
                
                if response['top_liked_reply']:
                    reply = Comment(comment_id=response['top_liked_reply']['id'],
                                    post_id=post_id,
                                    replied_to=response["c"]["id"],
                                    text=response["top_liked_reply"]['text'],
                                    username=response['top_reply_commenter.username'],
                                    user_id=response['top_reply_commenter.id'],
                                    created_date=response["top_liked_reply"]["created_date"],
                                    likes=response['top_liked_reply']['likes'],
                                    pinned=response['top_liked_reply']['pinned'],
                                    liked_by_current_user=response['reply_liked_by_user'],
                                    posted_by_current_user=response['reply_posted_by_user'])
                    response_entry['replies'].append({
                                                "comment":reply,
                                                "liked_by_current_user":response["reply_liked_by_user"],
                                                "replies":[]
                                            })

                pinned_comment_response.append(response_entry)
        return({"comments": comment_response, "pinned_comments": pinned_comment_response})
    
    def add_pinned_comment(self, comment_id, post_id):
        """
        Adds a pinned comment for a post
        
        Args:
            comment_id: comment's PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_pinned_comment_query, comment_id, post_id)
        
    @staticmethod
    def add_pinned_comment_query(tx, comment_id, post_id):
        query = """
                match (pp {id: $post_id}) 
                match (rr:Comment {id: $comment_id})
                with pp,rr
                where not exists ((pp)-[ll:PINNED]->(rr)) 
                    create (pp)-[ll:PINNED {created_date:datetime()}]->(rr)
                    set rr.pinned = True
                    return rr
                """
        result = tx.run(query, comment_id=comment_id, post_id=post_id)
        
    def remove_liked_comment(self, username, comment_id):
        """
        removes a liked comment for a user
        
        Args:
            username: users PK
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.remove_liked_comment_query, username, comment_id)    
    @staticmethod
    def remove_liked_comment_query(tx, username, comment_id):
        query = """
                match (uu:User {username: $username}) 
                match (rr:Comment {id: $comment_id}) 
                match (uu)-[ll:LIKES]->(rr)
                delete ll
                WITH rr
                WHERE rr.likes > 0
                SET rr.likes = rr.likes - 1
                """
        result = tx.run(query, username=username, comment_id=comment_id)

    def remove_liked_post(self, username, post_id):
        """
        removes a liked post for a user
        
        Args:
            username: users PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.remove_liked_post_query, username, post_id)    
    @staticmethod
    def remove_liked_post_query(tx, username, post_id):
        query = """
                match (uu:User {username: $username}) 
                match (rr {id: $post_id}) 
                match (uu)-[ll:LIKES]->(rr)
                delete ll
                WITH rr
                WHERE rr.likes > 0
                SET rr.likes = rr.likes - 1
                """
        result = tx.run(query, username=username, post_id=post_id)

    def remove_pinned_comment(self, comment_id, post_id):
        """
        removes a pinned comment for a post
        
        Args:
            comment_id: comment's PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.remove_pinned_comment_query, comment_id, post_id)    
    @staticmethod
    def remove_pinned_comment_query(tx, comment_id, post_id):
        query = """
                match (pp {id: $post_id}) 
                match (rr:Comment {id: $comment_id}) 
                match (pp)-[ll:PINNED]->(rr)
                delete ll
                set rr.pinned = False
                """
        result = tx.run(query, comment_id=comment_id, post_id=post_id)

    @timing_decorator
    def get_feed(self, current_user:User, skip:int, limit:int): 
        with self.driver.session() as session:
            result = session.execute_read(self.get_feed_query, current_user.username, skip, limit)
        return(result)
    @staticmethod
    def get_feed_query(tx, username, skip, limit):
        query = """ 
                    MATCH (p {deleted:false})
                    WHERE p:Milestone OR p:Review OR p:Comparison OR p:Update
                    match (p)<-[pr:POSTED]-(u:User)
                    optional match (cu:User {username:$username})-[lr:LIKES]->(p)
                    optional match (p)-[br:POST_FOR_BOOK]-(b)
                    optional match (comments:Comment {deleted:false})<-[:HAS_COMMENT]-(p)
                    RETURN p, labels(p), u.username, b, u.id,
                    CASE WHEN lr IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
                    CASE WHEN u.username = $username THEN true ELSE false END AS posted_by_current_user,
                    count(comments) as num_comments
                    order by p.created_date desc
                    skip $skip
                    limit $limit
                    """
        result = tx.run(query, username=username, skip=skip, limit=limit)
        # results = [record for record in result.data()]
        
        output = {"Milestone":[],
                  "RecommendationFriend":[],
                  "Comparison":[],
                  "Update":[],
                  "Review":[]}
        
        for response in result:
            post = response['p']
            if response['labels(p)'] == ["Milestone"]:
                milestone = MilestonePost(post_id=post["id"],
                                                         book="",
                                                         created_date=post["created_date"],
                                                         num_books=post["num_books"],
                                                         user_id=response['u.id'],
                                                         user_username=response['u.username'],
                                                         likes=post['likes'],
                                                         num_comments=response["num_comments"])
                
                milestone.liked_by_current_user = response['liked_by_current_user']
                milestone.posted_by_current_user = response['posted_by_current_user']
                output['Milestone'].append(milestone)                                                       
            
            elif response['labels(p)'] == ['Comparison']:
                if output['Comparison']:
                    if output['Comparison'][-1].id == post["id"]:
                        output['Comparison'][-1].compared_books.append(response['b']['id'])
                        output['Comparison'][-1].book_title.append(response['b']['title'])
                        output['Comparison'][-1].book_small_img.append(response['b']['small_img_url'])
                        continue
                
                comparison = ComparisonPost(post_id=post["id"],
                                            compared_books=[response['b']['id']],
                                            user_username=response['u.username'],
                                            user_id=response['u.id'],
                                            comparators=post['comparators'],
                                            created_date=post['created_date'],
                                            comparator_ids=post['comparator_ids'],
                                            responses=post['responses'],
                                            book_specific_headlines=post['book_specific_headlines'],
                                            book_title=[response['b']['title']],
                                            book_small_img=[response['b']['small_img_url']],
                                            likes=post['likes'],
                                            num_comments=response["num_comments"])
                
                comparison.liked_by_current_user = response['liked_by_current_user']
                comparison.posted_by_current_user = response['posted_by_current_user']
                output['Comparison'].append(comparison)


            elif response['labels(p)'] == ["Update"]:
                update = UpdatePost(post_id=post["id"],
                                                   book=response['b']['id'],
                                                   book_title=response['b']['title'],
                                                   created_date=post["created_date"],
                                                   page=post['page'],
                                                   response=post['response'],
                                                   spoiler=post['spoiler'],
                                                   user_id=response['u.id'],
                                                   book_small_img=response['b']['small_img_url'],
                                                   user_username=response['u.username'],
                                                   likes=post['likes'],
                                                   num_comments=response["num_comments"])
                
                update.liked_by_current_user = response['liked_by_current_user']
                update.posted_by_current_user = response['posted_by_current_user']
                output['Update'].append(update)

            elif response['labels(p)'] == ["Review"]:
                review = ReviewPost(post_id=post["id"],
                                                    book=response['b']['id'],
                                                    book_title=response['b']['title'],
                                                    created_date=post["created_date"],
                                                    questions=post['questions'],
                                                    question_ids=post['question_ids'],
                                                    responses=post['responses'],
                                                    spoilers=post['spoilers'],
                                                    user_id=response['u.id'],
                                                    book_small_img=response['b']['small_img_url'],
                                                    user_username=response['u.username'],
                                                    num_comments=response["num_comments"]
                                                    )
                review.liked_by_current_user = response['liked_by_current_user']
                review.posted_by_current_user = response['posted_by_current_user']
                output['Review'].append(review)

        return(output)
    
    def set_post_as_deleted(self,post_id):
        """
        Set deleted flag of a post and all comments on that post to True
        
        Args:
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.set_post_as_deleted_query, post_id)    
    @staticmethod
    def set_post_as_deleted_query(tx, post_id):
        query = """
                match (pp {id: $post_id})
                optional match (postComment:Comment)<-[commentRel:HAS_COMMENT]-(pp)
                set pp.deleted=true
                set postComment.deleted=true
                """
        result = tx.run(query, post_id=post_id)

    def set_comment_as_deleted(self,comment_id):
        """
        Set deleted flag of a comment to True
        
        Args:
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.set_comment_as_deleted_query, comment_id)    
    @staticmethod
    def set_comment_as_deleted_query(tx, comment_id):
        query = """
                match (comment {id: $comment_id})
                optional match (commentReply:Comment)-[replyRel:REPLIED_TO]->(comment)
                set comment.deleted=true
                set commentReply.deleted=true
                """
        result = tx.run(query, comment_id=comment_id)

    def get_all_pinned_comments_for_post(self, post_id, username, skip, limit):
        """
        Gets all the pinned comments on the post. For comments in a thread, returns the number of comments in the thread
        as well as the most liked reply.

        Load in batches, so only 5 comments at a time, in order from most recent to least recent

        Also return if the current user has liked each of the comments

        Args:
            post_id: PK of the post for which to return comments    
            username: username of the current user
            skip: Low index of comments to grab
            limit: high index of comments to grab 
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_all_pinned_comments_for_post_query, post_id, username, skip, limit)  
        return(result)
    @staticmethod
    def get_all_pinned_comments_for_post_query(tx, post_id, username, skip, limit):
        query = """
                match (uu:User {username: $username}) 
                match (rr {id: $post_id, deleted:false}) 
                match (rr)-[r:PINNED]->(c:Comment {is_reply:false, deleted:false})
                // Find the user who commented the parent comment
                MATCH (commenter:User)-[:COMMENTED]->(c)
                OPTIONAL MATCH (rcc:Comment {deleted:false})-[rrr:REPLIED_TO]->(c)
                with count(rcc) as num_replies, uu, rr, r, c, commenter
                OPTIONAL MATCH (rc:Comment {deleted:false})-[rrr:REPLIED_TO]->(c)
                // Find the user who commented the reply
                OPTIONAL MATCH (replyCommenter:User)-[:COMMENTED]->(rc)
                // Check if user with <username> has liked the parent comment
                OPTIONAL MATCH (u)-[likedParent:LIKES]->(c)
                // Check if user with <username> has liked the reply
                OPTIONAL MATCH (u)-[likedReply:LIKES]->(rc)
                WITH c, rr, r, rc, rrr, u, likedParent, likedReply, commenter, replyCommenter, num_replies
                ORDER BY rc.likes DESC, rc.created_date ASC
                WITH c, rr, r, COLLECT(rc)[0] AS top_liked_reply, COLLECT(rrr)[0] AS topLikedRel, u, 
                    COLLECT(likedParent)[0] AS likedParentRel, COLLECT(likedReply)[0] AS likedReplyRel, 
                    commenter, COLLECT(replyCommenter)[0] AS top_reply_commenter, num_replies
                RETURN c, top_liked_reply,
                    CASE WHEN likedParentRel IS NOT NULL THEN true ELSE false END AS parent_liked_by_user,
                    CASE WHEN likedReplyRel IS NOT NULL THEN true ELSE false END AS reply_liked_by_user,
                    commenter.username, 
                    top_reply_commenter.username,
                    case when commenter.username = $username then true else false END as parent_posted_by_user,
                    case when top_reply_commenter.username = $username then true else false END as reply_posted_by_user,
                    num_replies
                order by c.created_date desc
                skip $skip
                limit $limit
                """
        result = tx.run(query, username=username, post_id=post_id, skip=skip, limit=limit)
        # result = [record for record in result.data()]
        comment_response = []
        for response in result:
            comment = Comment(comment_id=response['c']['id'],
                              post_id=post_id,
                              replied_to=None,
                              text=response['c']['text'],
                              username=response['commenter.username'],
                              created_date=response['c']['created_date'],
                              likes=response['c']['likes'],
                              pinned=response['c']['pinned'],
                              liked_by_current_user=response['parent_liked_by_user'],
                              posted_by_current_user=response['parent_posted_by_user'],
                              num_replies=response['num_replies'])
            
            response_entry = {"comment":comment,
                               "liked_by_current_user":response['parent_liked_by_user'],
                               "replies":[]}
            
            if response['top_liked_reply']:
                reply = Comment(comment_id=response['top_liked_reply']['id'],
                                post_id=post_id,
                                replied_to=response["c"]["id"],
                                text=response["top_liked_reply"]['text'],
                                username=response['top_reply_commenter.username'],
                                created_date=response["top_liked_reply"]["created_date"],
                                likes=response['top_liked_reply']['likes'],
                                pinned=response['top_liked_reply']['pinned'],
                                liked_by_current_user=response['reply_liked_by_user'],
                                posted_by_current_user=response['reply_posted_by_user'])
                response_entry['replies'].append({"comment":reply,
                                                 "liked_by_current_user":response["reply_liked_by_user"],
                                                 "replies":[]})

            comment_response.append(response_entry)
        return(comment_response)

    def get_all_books(self):
        """
        Grabs all the book currently in the db and returns the ID and ISBN #s
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_all_books_query)  
        return(result)
    @staticmethod
    def get_all_books_query(tx):
        query = """
                match (b:Book)
                WHERE not EXISTS {
                    MATCH (b)<-[:HAS_VERSION]-(:Book)
                }
                return b.id, b.isbn13, b.isbn10, b.google_id, b.gr_id
                """
        result = tx.run(query)

        books = []
        for response in result:
            book = {"id":response["b.id"],
                    "isbn13":response["b.isbn13"],
                    "isbn10":response["b.isbn10"],
                    "google_id":response["b.google_id"],
                    "goodreads_id":response['b.gr_id']}
            
            books.append(book)
        
        return books
    
    def create_canon_book_relationship(self, canon_book_id, version_book_id):
        """
        Creates the canon book relationship in the DB
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_canon_book_relationship_query, canon_book_id=canon_book_id, version_book_id=version_book_id)  
        return(result)
    @staticmethod
    def create_canon_book_relationship_query(tx, canon_book_id, version_book_id):
        query = """
                match (canon_book:Book {id:$canon_book_id})
                match (version_book:Book {id:$version_book_id})
                merge (canon_book)-[:HAS_VERSION]->(version_book)
                """
        result = tx.run(query, canon_book_id=canon_book_id, version_book_id=version_book_id)
    def check_if_version_or_canon(self,book_id):
        """
        Checks if a book is already a version or a canon version
        """
        with self.driver.session() as session:
            result = session.execute_read(self.check_if_version_or_canon_query, book_id=book_id)  
        return(result)
    @staticmethod
    def check_if_version_or_canon_query(tx, book_id):
        query = """
                match (b:Book {id:$book_id})
                RETURN CASE 
                WHEN NOT EXISTS ((b)-[:HAS_VERSION]-(:Book)) 
                THEN true 
                ELSE false 
                END AS relationshipDoesNotExist    
                """
        result = tx.run(query, book_id=book_id)
        response = result.single()
        return(response['relationshipDoesNotExist'])

    def get_book_versions(self, book_id):
        """
        Grabs all the versions of a book stored in the db
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_book_versions_query, book_id=book_id)  
        return(result)
    @staticmethod
    def get_book_versions_query(tx, book_id):
        query = """
        match (book:Book {id:$book_id})-[:HAS_VERSION]->(version:Book)
        return version.gr_id,
        version.id, 
        version.img_url, 
        version.isbn13,
        version.isbn10,
        version.lang, 
        version.originalPublicationYear, 
        version.pages, 
        version.small_img_url, 
        version.description, 
        version.title,
        version.author_names,
        version.google_id
        """
        versions_list = []
        result = tx.run(query, book_id=book_id)
       
        for response in result:
            book = Book(book_id=response["version.id"], 
                            gr_id=response["version.gr_id"], 
                            img_url=response["version.img_url"],
                            small_img_url=response["version.small_img_url"],
                            pages=response["version.pages"],
                            publication_year=response["version.originalPublicationYear"],
                            lang=response["version.lang"],
                            title=response["version.title"],
                            description=response["version.description"],
                            isbn13 = response["version.isbn13"],
                            isbn10 = response["version.isbn10"],
                            author_names=response["version.author_names"],
                            google_id=response['version.google_id'])
            versions_list.append(book)
        
        return versions_list
    
    def get_book_versions_by_google_id(self, book_id):
        """
        Grabs all the versions of a book stored in the db, searching by google_id
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_book_versions_by_google_id_query, book_id=book_id)  
        return(result)
    
    @staticmethod
    def get_book_versions_by_google_id_query(tx, book_id):
        query = """
        match (book:Book)
        where book.id = $book_id or book.google_id = $book_id
        match (book)-[:HAS_VERSION]->(version:Book)
        return version.gr_id,
        version.id, 
        version.img_url, 
        version.isbn13,
        version.isbn10,
        version.lang, 
        version.originalPublicationYear, 
        version.pages, 
        version.small_img_url, 
        version.description, 
        version.title,
        version.author_names,
        version.google_id
        """
        versions_list = []
        result = tx.run(query, book_id=book_id)
       
        for response in result:
            book = Book(book_id=response["version.id"], 
                            gr_id=response["version.gr_id"], 
                            img_url=response["version.img_url"],
                            small_img_url=response["version.small_img_url"],
                            pages=response["version.pages"],
                            publication_year=response["version.originalPublicationYear"],
                            lang=response["version.lang"],
                            title=response["version.title"],
                            description=response["version.description"],
                            isbn13 = response["version.isbn13"],
                            isbn10 = response["version.isbn10"],
                            author_names=response["version.author_names"],
                            google_id=response['version.google_id'])
            versions_list.append(book)
        
        return versions_list
    
    
    ###################################################################################################################
    ###########
    ###########        USER QUERIES
    ###########
    ###################################################################################################################
    def update_user_profile_image(self, user_id:str, img:str):
        """
        Updates user profile img from uploadCare cdn link
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_user_profile_image_query, user_id=user_id, img=img)
        return(result)
    @staticmethod
    def update_user_profile_image_query(tx, user_id, img):
        """
        More nerd shit on here
        """
        query = """
            match(u:User {id:$user_id})
            set u.profile_img_url = $img
            return u.profile_img_url
        """
        tx.run(query, user_id=user_id, img=img)

    def update_username(self,new_username:str, user_id:str):
        """
        Updates the username of a user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_username_query, new_username=new_username, user_id=user_id)  
        return(result)
    
    @staticmethod
    def update_username_query(tx, new_username, user_id):
        query = """
        match (u:User {id:$user_id})
        set u.username = $new_username
        """
        try:
            tx.run(query,user_id=user_id,new_username=new_username)
            return HTTPException(
                status_code=200,
                detail="Username change successfully"
            )
        except:
            return HTTPException(
                    status_code=401,
                    detail="Username is already taken"
                )
            
    def update_bio(self, new_bio, user_id):
        """
        Updates the bio of a user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_bio_query, new_bio=new_bio, user_id=user_id)  
        return(result)
    
    @staticmethod
    def update_bio_query(tx, new_bio, user_id):
        query = """
        match (u:User {id:$user_id})
        set u.bio = $new_bio
        """
        
        tx.run(query,user_id=user_id,new_bio=new_bio)

    def update_email(self, new_email, user_id):
        """
        Updates the email of a user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_email_query, new_email=new_email, user_id=user_id)  
        return(result)
    
    @staticmethod
    def update_email_query(tx, new_email, user_id):
        query = """
        match (u:User {id:$user_id})
        set u.email = $new_email
        """
        
        tx.run(query,user_id=user_id,new_email=new_email)

    def update_password(self,new_password:str, user_id:str):
        """
        Updates the password of a user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_password_query, new_password=new_password, user_id=user_id)  
        return(result)
    
    @staticmethod
    def update_password_query(tx, new_password, user_id):
        query = """
        match (u:User {id:$user_id})
        set u.password = $new_password
        """
        
        tx.run(query,user_id=user_id,new_password=new_password)
    
    ###################################################################################################################
    ###########
    ###########        About me QUERIES
    ###########
    ###################################################################################################################
    
    def get_user_about_me(self, user_id):
        with self.driver.session() as session:
            result = session.execute_read(self.get_user_about_me_query, user_id=user_id)
        return(result)
    
    @staticmethod
    def get_user_about_me_query(tx, user_id):
        query = """
            match(u:User {id: $user_id})
            optional match(u)-[LIKES]->(g:Genre)
            optional match(u)-[rr:LIKES]-(a:Author)

            return g, a
        """
        result = tx.run(query, user_id=user_id)

        genres = set()
        authors = set()

        for response in result:
            if response['g']:
                genres.add(
                    (response['g']['name'], response['g']['id'])
                )
            
            if response['a']:
                authors.add(
                    (response['a']['name'], response['a']['id'])
                )

        return { "genres": genres, "authors": authors }

    ###################################################################################################################
    ###########
    ###########        Friend/Follow/Block QUERIES
    ###########
    ###################################################################################################################

    def block_user(self,from_user_id:str, to_user_id:str):
        """
        blocks a user, deletes all existing relationships to the user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.block_user_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def block_user_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        optional match (fromUser)-[anyRel]-(toUser)
        delete anyRel
        merge (fromUser)-[blockRel:BLOCKED]->(toUser)
        RETURN Case when blockRel is not null then true else false end as foundRelationship
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend Request Not Found")
        else:
            return HTTPException(200, 'Success')

    def unblock_user(self,from_user_id:str, to_user_id:str):
        """
        unblocks a user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.unblock_user_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def unblock_user_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        match (fromUser)-[blockRel:BLOCKED]->(toUser)
        delete blockRel
        RETURN Case when toUser is not null then true else false end as foundRelationship
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend Request Not Found")
        else:
            return HTTPException(200, 'Success')
        
    def send_friend_request(self,from_user_id:str, to_user_id:str):
        """
        Sends a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.send_friend_request_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def send_friend_request_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        with toUser, fromUser
        where not exists ((fromUser)-[:BLOCKED]-(toUser))
            and not exists ((fromUser)-[:FRIENDED]-(toUser))
            create (fromUser)-[friend_request:FRIENDED {status:"pending", created_date:datetime()}]->(toUser)
        return toUser.id, friend_request.status
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()

        if not response:
            return HTTPException(400,"Request Not Sent")
        else:
            return HTTPException(199,'Friend Request Sent')
            
    
    def unsend_friend_request(self,from_user_id:str, to_user_id:str):
        """
        Unsends a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.unsend_friend_request_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def unsend_friend_request_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        OPTIONAL MATCH (fromUser)-[friend_request:FRIENDED {status:"pending"}]->(toUser)
        DELETE friendRequest
        RETURN toUser
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"Unsend request did not go through")
        else:
            return HTTPException(200, 'Friend Request Unsent')

        
    def accept_friend_request(self,from_user_id:str, to_user_id:str):
        """
        accepts a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.accept_friend_request_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def accept_friend_request_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        MATCH (fromUser)-[friend_request:FRIENDED {status:"pending"}]->(toUser)
        set friend_request.status = "friends"
        set friend_request.created_date = datetime()
        RETURN friend_request
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend Request Not Found")
        else:
            return HTTPException(200, 'Success')

        
    def decline_friend_request(self,from_user_id:str, to_user_id:str):
        """
        declines a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.decline_friend_request_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def decline_friend_request_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        MATCH (fromUser)-[friend_request:FRIENDED {status:"pending"}]->(toUser)
        del friend_request
        RETURN toUser
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend Request Not Found")
        else:
            return HTTPException(200, 'Success')

    def remove_friend(self,from_user_id:str, to_user_id:str):
        """
        remove a friend relationship
        """
        with self.driver.session() as session:
            result = session.execute_write(self.remove_friend_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def remove_friend_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        MATCH (fromUser)-[friendRelationship:FRIENDED {status:"friends"}]->(toUser)
        delete friendRelationship
        RETURN toUser
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend relationship not found")
        else:
            return HTTPException(200, 'Success')

    def follow_user(self,from_user_id:str, to_user_id:str):
        """
        Follows a user if the to_user has a critic account
        """
        with self.driver.session() as session:
            result = session.execute_write(self.follow_user_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def follow_user_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id, user_type:"critic"})
        where not exists ((fromUser)-[:BLOCKED]-(toUser))
            merge (fromUser)-[followRel:FOLLOWS {created_date:datetime()}]->(toUser)
        RETURN followRel
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend Request Not Found")
        else:
            return HTTPException(200, 'Success')

    def unfollow_user(self,from_user_id:str, to_user_id:str):
        """
        unfollows a user if the to_user has a critic account
        """
        with self.driver.session() as session:
            result = session.execute_write(self.unfollow_user_query, from_user_id=from_user_id,to_user_id=to_user_id)  
        return(result)
    
    @staticmethod
    def unfollow_user_query(tx, from_user_id:str, to_user_id:str):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id, user_type:"critic"})
        match (fromUser)-[followRel:FOLLOWS]->(toUser)
        delete followRel
        RETURN Case when toUser is not null then true else false end as foundRelationship
        """
        
        result = tx.run(query,from_user_id=from_user_id,to_user_id=to_user_id)
        response = result.single()
        if not response:
            return HTTPException(400,"User or Friend Request Not Found")
        else:
            return HTTPException(200, 'Success')
        

    ###################################################################################################################
    ###########
    ###########        Friend/Follow/Block List QUERIES
    ###########
    ###################################################################################################################

    def get_friend_list(self,user_id:str, current_user_id:str):
        """
        unfollows a user if the to_user has a critic account
        """
        with self.driver.session() as session:
            result = session.execute_write(self.get_friend_list_query, user_id=user_id, current_user_id=current_user_id)  
        return(result)
    
    @staticmethod
    def get_friend_list_query(tx, user_id:str, current_user_id:str):
        query = """
        match (user:User {id:$user_id})
        match (currentUser:User {id:$current_user_id})
        match (user)-[friendRel:FRIENDED {status:"friends"}]-(toUser)
        OPTIONAL MATCH (currentUser)-[friendStatus:FRIENDED]-(toUser)
        OPTIONAL MATCH (currentUser)-[blockStatus:BLOCKED]-(toUser)
        OPTIONAL MATCH (currentUser)-[followStatus:FOLLOWS]-(toUser)
        RETURN toUser, 
            friendRel.status AS friendStatus, 
            friendStatus.status AS currentUserFriendStatus, 
            blockStatus AS currentUserBlockStatus, 
            followStatus AS currentUserFollowStatus
        """
        
        result = tx.run(query,user_id=user_id, current_user_id=current_user_id)
        for response in result:
            print(response.data())
    
    def close(self):
        self.driver.close()

if __name__ == "__main__":
    driver = Neo4jDriver()

    # driver.send_friend_request("a0f86d40-4915-4773-8aa1-844d1bfd0b41","dfa501ff-0f58-485f-94e9-50ba5dd10396")
    # driver.accept_friend_request("a0f86d40-4915-4773-8aa1-844d1bfd0b41","dfa501ff-0f58-485f-94e9-50ba5dd10396")
    # driver.remove_friend("a0f86d40-4915-4773-8aa1-844d1bfd0b41","dfa501ff-0f58-485f-94e9-50ba5dd10396")
    # driver.unfollow_user("a0f86d40-4915-4773-8aa1-844d1bfd0b41","dfa501ff-0f58-485f-94e9-50ba5dd10396")
    # driver.follow_user("a0f86d40-4915-4773-8aa1-844d1bfd0b41","dfa501ff-0f58-485f-94e9-50ba5dd10396")

    driver.get_friend_list("a0f86d40-4915-4773-8aa1-844d1bfd0b41","dfa501ff-0f58-485f-94e9-50ba5dd10396")
    # driver.block_user()
    driver.close()