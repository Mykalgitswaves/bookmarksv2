from neo4j import GraphDatabase
import uuid
import json
import sys
sys.path.append('./')
from helpers import timing_decorator 

class User():
    def __init__(self, user_id: int, 
                 username="", 
                 created_date="", 
                 book_ids=[], 
                 review_ids=[],
                 to_read_ids=[],
                 liked_authors=[],
                 liked_genres=[],
                 currently_reading=[],
                 friends=[],
                 liked_reviews=[],
                 email="",
                 full_name="",
                 hashed_password="",
                 disabled=False):
        self.user_id = user_id
        self.books = book_ids
        self.reviews = review_ids
        self.want_to_read = to_read_ids
        self.authors = liked_authors
        self.genres = liked_genres
        self.reading = currently_reading
        self.friends = friends
        self.liked_reviews = liked_reviews
        self.username = username
        self.created_date = created_date
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.disabled=disabled
    def add_friend(self, friend_id:int):
        """
        Adds a friendship relationship to the database
        
        Args:
            friend_id: PK of the friend to add
        Returns:
            None
        """
        driver = Neo4jDriver()
        if friend_id not in self.friends:
            driver.add_user_friend(self.user_id, friend_id)
            self.friends.append(friend_id)
        else:
            raise Exception("This relationship already exists")
    def add_favorite_genre(self, genre_id:int):
        """
        Adds a favorite genre relationship to the database
        
        Args:
            genre_id: PK of the genre to favorite
        Returns:
            None
        """
        driver = Neo4jDriver()
        if genre_id not in self.genres:
            driver.add_favorite_genre(self.user_id, genre_id)
            self.genres.append(genre_id)
        else:
            raise Exception("This relationship already exists")
    def add_favorite_author(self, author_id:int):
        """
        Adds a favorite author relationship to the database
        
        Args:
            author_id: PK of the author to favorite
        Returns:
            None
        """
        driver = Neo4jDriver()
        if author_id not in self.authors:
            driver.add_favorite_author(self.user_id, author_id)
            self.authors.append(author_id)
        else:
            raise Exception("This relationship already exists")
    def add_liked_review(self, review_id:int):
        """
        Adds a liked review relationship to the database
        
        Args:
            review_id: PK of the review to like
        Returns:
            None
        """
        driver = Neo4jDriver()
        if review_id not in self.liked_reviews:
            driver.add_liked_review(self.user_id, review_id)
            self.liked_reviews.append(review_id)
        else:
            raise Exception("This relationship already exists")
    def add_to_read(self, book_id:int):
        """
        Adds a book to the user's to read list in db. Deletes all other relationships to this book
        
        Args:
            book_id: PK of book to add to to read
        Returns:
            None
        """
        driver = Neo4jDriver()
        if book_id not in self.want_to_read:
            driver.add_to_read(self.user_id, book_id)
            self.want_to_read.append(book_id)
        else:
            raise Exception("This relationship already exists")
    def add_is_reading(self, book_id:int):
        """
        Adds a book to the user's currently reading list in db. Deletes all other relationships to this book
        
        Args:
            book_id: PK of book to add to to read
        Returns:
            None
        """
        if book_id not in self.reading:
            driver = Neo4jDriver()
            driver.add_reading(self.user_id, book_id)
            self.reading.append(book_id)
        else:
            raise Exception("This relationship already exists")
    def add_reviewed_setup(self, book_id:int, rating:int):
        driver = Neo4jDriver()
        driver.add_reviewed_book_setup(user_id=self.user_id, book_id=book_id, rating=rating)
        self.books.append(book_id)
    

class Review():
    def __init__(self, review_id, rating, user, book):
        self.id = review_id
        self.rating = rating
        self.user = user
        self.book = book
    def change_rating(self, new_rating:int):
        """
        Changes the rating associated with this review in the db
        
        Args:
            new_rating: The value for the rating to be updated to
        Returns:
            None
        """
        driver = Neo4jDriver()
        if new_rating != self.rating:
            driver.change_review_rating(self.id,new_rating)
            self.rating = new_rating
        else:
            print("New rating is same as old rating")
class Book():
    def __init__(self, book_id, gr_id=None, 
                 img_url="", small_img_url="", pages=None, 
                 publication_year=None, lang="", title="", 
                 description="", isbn24=None ,genres=[], 
                 authors=[], tags=[], reviews=[], 
                 genre_names=[], author_names=[], google_id="",in_database=True):
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
        self.isbn24 = isbn24,
        self.in_database = in_database,
        self.google_id = google_id
    def add_tag(self,tag_id):
        """
        Adds a tag to the book
        
        Args:
            tag_id: PK of tag to add
        Returns:
            None
        """
        if tag_id not in self.tags:
            driver = Neo4jDriver()
            driver.add_book_tag(self.id, tag_id)
            self.tags.append(tag_id)
            driver.close()
        else:
            raise Exception("This relationship already exists")
    def add_to_db(self):
        driver = Neo4jDriver()
        id = driver.create_book(self.title,self.img_url,self.pages,self.publication_year,self.lang,self.description,self.genres,
                           self.authors,self.isbn24,self.small_img_url,self.author_names,self.genre_names,self.google_id,self.gr_id)
        self.id = id
        driver.close()
        
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
    def pull_user_node_query(tx,user_id):
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
                elif response["Labels(b)"] == ["Review"]:
                    user.liked_reviews.append(response["b.id"])
            # Kyle i added this because i was getting error referencing before assignments on my put request.
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
    def add_user_friend(self, user_id:int, friend_id:int):
        """
        Adds a friend relationship between two users
        
        Args:
            user_id: users PK
            friend_id: friend's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_user_friend_query, user_id, friend_id)
    @staticmethod
    def add_user_friend_query(tx, user_id, friend_id):
        query = """
                match (uu:User {id: $user_id}) match (bb:User {id: $friend_id}) merge (uu)-[rr:HAS_FRIEND]->(bb)
                """
        result = tx.run(query, user_id=user_id,friend_id=friend_id)
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
    def add_liked_review(self, user_id, review_id):
        """
        Adds a liked review for a user
        
        Args:
            user_id: users PK
            review_id: reviews's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.add_liked_review_query, user_id, review_id)    
    @staticmethod
    def add_liked_review_query(tx, user_id, review_id):
        query = """
                match (uu:User {id: $user_id}) match (rr:Review {id: $review_id}) merge (uu)-[ll:LIKES]->(aa)
                """
        result = tx.run(query, user_id=user_id, review_id=review_id)
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
    def get_unique_pk(self, node):
        """
        Returns a unique primary key for the node instance
        Args:
            node: Node to get a primary key for
        Returns
            int: Primary Key which has never been used before
        """
        with self.driver.session() as session:
            result = session.execute_write(self.get_unique_pk_query, node)
        return(result)
    @staticmethod
    def get_unique_pk_query(tx, node):
        query = f"""
                match (n:{node}) return MAX(n.id)
                """
        result = tx.run(query)
        response = result.single()
        return(int(response['MAX(n.id)']) + 1)

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
    def pull_review_node(self,review_id):
        """
        Returns all the metadata for a review
        Args:
            review_id: PK of review to retrieve
        Returns:
            Review: review object with metadata
        """
        with self.driver.session() as session:
            result = session.execute_write(self.pull_review_node_query, review_id)
        return(result)
    @staticmethod
    def pull_review_node_query(tx, review_id):
        query = """
                match (rn:Review {id: $review_id})-[r]-(b) return TYPE(r),b.id,rn.rating
                """
        result = tx.run(query, review_id=review_id)
        for response in result:
            if response['TYPE(r)'] == "WROTE_REVIEW":
                user_id = response["b.id"]
            elif response['TYPE(r)'] == "IS_REVIEW_OF":
                book_id = response["b.id"]
        rating = response['rn.rating']
        review = Review(review_id=review_id,user=user_id,book=book_id,rating=rating)
        return(review)
    def change_review_rating(self,review_id,new_rating):
        """
        Changes the rating associated with a review in the DB
        Args:
            review_id: PK for the review to be altered
            new_rating: New rating for the review
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_user_query, review_id, new_rating)
    @staticmethod
    def change_review_rating_query(tx,review_id,new_rating):
        query = """
                match (r:Rating {id:$review_id})
                set r += {rating:$new_rating}
                """
        result = tx.run(query,review_id=review_id,new_rating=new_rating)
        return(result)
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
    def create_review(self, rating, user, book):
        """
        Creates a review in the database
        Args:
            rating: rating of the book
            user: PK of the user that wrote the review
            book: PK of the book that was reviewed
        Returns:
            Review: review object for the created review
        """
        review_id = self.get_unique_pk("Rating")
        with self.driver.session() as session:
            review = session.execute_write(self.create_review_query, rating, review_id, user, book)
        return(review)
    @staticmethod
    def create_review_query(tx, rating, review_id, user, book):
        query = """
                match (u:User {id:$user})
                match (b:Book {id:$book})
                create (r:Review {id:$review_id, rating:$rating})
                create (r)-[ir:IS_REVIEW_OF]->(b)
                create (u)-[wr:WROTE_REVIEW]->(r)
                """
        result = tx.run(query, user=user, book=book, rating=rating,review_id=review_id)
        review = Review(review_id=review_id,rating=rating,user=user,book=book)
        return(review)
    def pull_book_node(self,book_id):
        """
        Pulls all the data from a book in the DB

        Args:
            book_id: PK of the book to pull
        Returns:
            Book: book object containing all the metadata
        """
        with self.driver.session() as session:
            book = session.execute_write(self.pull_book_node_query, book_id)
        return(book)
    @staticmethod
    def pull_book_node_query(tx,book_id):
        query = """
                match (b:Book {id:$book_id}) 
                match (b)-[r]-(g)
                return b.gr_id, 
                b.img_url, 
                b.isbn24, 
                b.lang, 
                b.originalPublicationYear, 
                b.pages, 
                b.small_img_url, 
                b.description, 
                b.title,
                TYPE(r),
                g.id
                """
        result = tx.run(query, book_id=book_id)
        response = result.single()
        book = Book(book_id=book_id, 
                    gr_id=response["b.gr_id"], 
                    img_url=response["b.img_url"],
                    small_img_url=response["b.small_img_url"],
                    pages=response["b.pages"],
                    publication_year=response["b.originalPublicationYear"],
                    lang=response["b.lang"],
                    title=response["b.title"],
                    description=response["b.description"],
                    isbn24 = response["b.isbn24"])
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
    
    def create_book(self, title, img_url, pages, publication_year, lang, 
                    description='', genres=[], authors=[], isbn24='', 
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
            isbn24: ISBN24 number is applicable
        Returns:
            Book: book object with all related metadata
        """
        book_id = self.get_unique_pk("Book")

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
            book = session.execute_write(self.create_book_query, book_id, 
                                         title, img_url, pages, publication_year, 
                                         lang, description, genres, authors, 
                                         isbn24, small_img_url, author_names,google_id,gr_id)
        return(book_id)
    @staticmethod
    def create_book_query(tx,book_id, title, img_url, 
                          pages, publication_year, lang, 
                          description, genres, authors, isbn24, 
                          small_img_url, author_names,google_id,gr_id):
        query = """
                create (b:Book {id:$book_id, 
                title:$title, 
                img_url:$img_url, 
                pages:$pages, 
                publication_year:$pages, 
                lang:$lang, 
                description:$description, 
                isbn24:$isbn24,
                small_img_url:$small_img_url,
                author_names:$author_names,
                google_id:$google_id,
                gr_id:$gr_id})
                """
        result = tx.run(query,
                        book_id=book_id, 
                        title=title, 
                        img_url=img_url, 
                        pages=pages, 
                        publication_year=publication_year, 
                        lang=lang, 
                        description=description, 
                        isbn24=isbn24[0],
                        small_img_url=small_img_url,
                        author_names=author_names,
                        google_id=google_id,
                        gr_id=gr_id)
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
                    isbn24=isbn24,
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
        author_id = self.get_unique_pk("Author")
        with self.driver.session() as session:
            author = session.execute_write(self.create_author_query, author_id, full_name, books)
        return(author)
    @staticmethod
    def create_author_query(tx, author_id, full_name, books):
        # Creates the author node
        query = """
                create (a:Author {id:$author_id, name:$full_name})
                """
        result = tx.run(query, author_id=author_id,full_name=full_name)
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
                    RETURN b.title, b.id, b.description, b.img_url, b.publication_year, b.isbn24, a
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
                    isbn24=response['b.isbn24'],
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
            books = session.execute_write(self.pull_search2_books_query, skip, limit, text)
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
    def add_reviewed_book_setup(self, book_id, user_id, rating):
        """
        
        """
        with self.driver.session() as session:
            user = session.execute_write(self.add_reviewed_book_setup_query, book_id, user_id, rating)
        
    @staticmethod
    def add_reviewed_book_setup_query(tx, book_id, user_id, rating):
        query = """
                match (u:User {id:$user_id})
                match (b:Book {id:$book_id}) 
                merge (u)-[rr:REVIEWED {rating:$rating}]->(b)
                """
        result = tx.run(query, user_id=user_id,book_id=book_id, rating=rating)

    def pull_all_reviews_by_user(self):
        with self.driver.session() as session:
            result = session.execute_read(self.pull_all_reviews_by_user_query)
        return(result)
    @staticmethod
    def pull_all_reviews_by_user_query(tx):
        query = "match (u:User)-[rr:REVIEWED]-(b:Book) return u.id,rr.rating,b.id"
        result = tx.run(query)
        result = [{"user":response["u.id"],"book":response["b.id"],"rating":response["rr.rating"]} for response in result]
        return(result)
        
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
    def find_book_by_isnb13(self,isbn13:int):
        """
        Finds a book by its isbn number
        """
        with self.driver.session() as session:
            result = session.execute_read(self.find_book_by_isnb13_query, isbn13)
        return(result)
    @staticmethod
    def find_book_by_isnb13_query(tx,isbn13):
        query = "match (bb:Book {isbn24:$isbn13})-[WROTE]-(a:Author) return bb.id,bb.title,bb.small_img_url,bb.description,a.name"
        result = tx.run(query,isbn13=isbn13)
        response = result.single()
        if response:
            book = Book(response['bb.id'],
                 small_img_url=response['bb.small_image_url'],
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
        genre_id = self.get_unique_pk("Genre")
        with self.driver.session() as session:
            result = session.execute_write(self.create_genre_query, genre_id, name)
        return(result)
    @staticmethod
    def create_genre_query(tx,genre_id, name):
        query = "create (g:Genre {id:$genre_id, name:$name}) return g.id"
        result = tx.run(query,genre_id=genre_id,name=name)
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
    
    def get_book_by_google_id(self,google_id):
        """
        Finds a book by google id if in db

        Args:
            google_id: Google id of the book to pull
        Returns:
            Book: book object containing all the metadata
        """
        with self.driver.session() as session:
            book = session.execute_write(self.get_book_by_google_id_query, google_id)
        return(book)
    @staticmethod
    def get_book_by_google_id_query(tx,google_id):
        query = """
                match (b:Book {google_id:$google_id}) 
                match (b)-[r]-(g)
                return b.gr_id,
                b.id, 
                b.img_url, 
                b.isbn24, 
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
                        isbn24 = response["b.isbn24"])
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
        
    def close(self):
        self.driver.close()



if __name__ == "__main__":
    driver = Neo4jDriver()
    book = driver.pull_book_node(book_id=1)
    print(book)
    driver.close()