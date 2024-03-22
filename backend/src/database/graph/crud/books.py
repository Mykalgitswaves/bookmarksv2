from fastapi import Depends

from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.database.graph.crud.genres import GenreCRUDRepositoryGraph
from src.database.graph.crud.authors import AuthorCRUDRepositoryGraph

from src.database.graph.base import graph_db
from src.models.schemas.books import Book, BookSearchResult, BookSimilar, BookPreview, BookUpdate
from src.models.schemas.bookshelves import BookshelfBook

class BookCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def get_book_by_id(self,book_id):
        """
        Pulls all the data from a book in the DB

        Args:
            book_id: PK of the book to pull
        Returns:
            Book: book object containing all the metadata
        """
        with self.driver.session() as session:
            book = session.execute_read(self.get_book_by_id_query, book_id)
        return(book)
    @staticmethod
    def get_book_by_id_query(tx,book_id):
        query = """
                match (b:Book {id:$book_id}) 
                match (b)-[r]-(g)
                return
                b.img_url, 
                b.isbn13,
                b.isbn10,
                b.lang, 
                b.publication_year, 
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

        book = Book(id=book_id,
                    img_url=response["b.img_url"],
                    small_img_url=response["b.small_img_url"],
                    pages=response["b.pages"],
                    publication_year=response["b.publication_year"],
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

    def get_books_by_title(self, text: str, skip: int, limit: int):
        with self.driver.session() as session:
            response = session.execute_read(self.get_books_by_title_query, text=text, skip=skip, limit=limit)
        return response
    
    @staticmethod
    def get_books_by_title_query(tx, text: str, skip: int, limit: int):
        text = "(?i)" + "".join([f".*{word.lower()}.*" for word in text.split(" ")])
        query = """
                match (b:Book)
                where toLower(b.title) =~ $text
                return b.title as title,
                b.id as id,
                b.small_img_url as small_img_url,
                b.publication_year as publication_year
                skip $skip
                limit $limit
                """
        
        result = tx.run(query, text=text, skip=skip, limit=limit)
        response = [BookSearchResult(**response) for response in result]
        return response
    
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
                b.publication_year, 
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
            book = Book(id=response["b.id"],
                        img_url=response["b.img_url"],
                        small_img_url=response["b.small_img_url"],
                        pages=response["b.pages"],
                        publication_year=response["b.publication_year"],
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
                return 
                b.id, 
                b.img_url, 
                b.isbn13,
                b.isbn10,
                b.lang, 
                b.publication_year, 
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
            book = Book(id=response["b.id"],
                        img_url=response["b.img_url"],
                        small_img_url=response["b.small_img_url"],
                        pages=response["b.pages"],
                        publication_year=response["b.publication_year"],
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
        
    def get_canonical_book_by_google_id(self,google_id):
        """
        Uses the google id to find the id, title, and small_img_url in our db TODO: Same Coalese with canonical
        """
        with self.driver.session() as session:
            book = session.execute_read(self.get_canonical_book_by_google_id_query, google_id)
        return(book)
    
    @staticmethod
    def get_canonical_book_by_google_id_query(tx,google_id):
        query = """
                match (book:Book)
                WHERE book.google_id = $google_id or book.id = $google_id
                OPTIONAL MATCH (canonical:Book)-[:HAS_VERSION]->(book)
                WITH COALESCE(canonical, book) AS b
                return b.id as id, 
                b.title as title, 
                b.small_img_url as small_img_url
                """
        result = tx.run(query, google_id=google_id)
        response = result.single()
        if response:
            return (BookPreview(**response))
        else:
            return None
        
    def get_canonical_book_by_google_id_extended(self,google_id):
        """
        Uses the google id to find the id, title, authors, and small_img_url in our db TODO: Same Coalese with canonical
        """
        with self.driver.session() as session:
            book = session.execute_read(self.get_canonical_book_by_google_id_extended_query, google_id)
        return(book)
    
    @staticmethod
    def get_canonical_book_by_google_id_extended_query(tx,google_id):
        query = """
                match (book:Book)
                WHERE book.google_id = $google_id or book.id = $google_id
                OPTIONAL MATCH (canonical:Book)-[:HAS_VERSION]->(book)
                WITH COALESCE(canonical, book) AS b
                return b.id as id, 
                b.title as title,
                b.author_names as authors,
                b.small_img_url as small_img_url
                """
        result = tx.run(query, google_id=google_id)
        response = result.single()
        if response:
            return (BookshelfBook(**response))
        else:
            return None
        
    def get_book_by_isbn13(self,isbn13:int):
        """
        gets a book by its isbn number
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_book_by_isbn13_query, isbn13)
        return(result)
    
    @staticmethod
    def get_book_by_isbn13_query(tx,isbn13):
        query = "match (bb:Book {isbn13:$isbn13})-[WROTE]-(a:Author) return bb.id,bb.title,bb.small_img_url,bb.img_url,bb.description,a.name"
        result = tx.run(query,isbn13=isbn13)
        response = result.single()
        if response:
            book = Book(id=response['bb.id'],
                        img_url=response['bb.img_url'],
                        small_img_url=response['bb.small_img_url'],
                        title=response['bb.title'],
                        description=response['bb.description']
                 )
            [book.author_names.append(response['a.name']) for response in result]
            return(book)
        else:
            return(None)
        
    def get_book_by_isbn10(self,isbn10:int):
        """
        gets a book by its isbn number
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_book_by_isbn10_query, isbn10)
        return(result)
    
    @staticmethod
    def get_book_by_isbn10_query(tx,isbn10):
        query = "match (bb:Book {isbn10:$isbn10})-[WROTE]-(a:Author) return bb.id,bb.title,bb.small_img_url,bb.img_url,bb.description,a.name"
        result = tx.run(query,isbn10=isbn10)
        response = result.single()
        if response:
            book = Book(id=response['bb.id'],
                        img_url=response['bb.img_url'],
                        small_img_url=response['bb.small_img_url'],
                        title=response['bb.title'],
                        description=response['bb.description']
                 )
            [book.author_names.append(response['a.name']) for response in result]
            return(book)
        else:
            return(None)
        
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
        return
        version.id, 
        version.img_url, 
        version.isbn13,
        version.isbn10,
        version.lang, 
        version.publication_year, 
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
            book = Book(id=response["version.id"], 
                            img_url=response["version.img_url"],
                            small_img_url=response["version.small_img_url"],
                            pages=response["version.pages"],
                            publication_year=response["version.publication_year"],
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
        return 
        version.id, 
        version.img_url, 
        version.isbn13,
        version.isbn10,
        version.lang, 
        version.publication_year, 
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
            book = Book(id=response["version.id"], 
                        img_url=response["version.img_url"],
                        small_img_url=response["version.small_img_url"],
                        pages=response["version.pages"],
                        publication_year=response["version.publication_year"],
                        lang=response["version.lang"],
                        title=response["version.title"],
                        description=response["version.description"],
                        isbn13 = response["version.isbn13"],
                        isbn10 = response["version.isbn10"],
                        author_names=response["version.author_names"],
                        google_id=response['version.google_id'])
            versions_list.append(book)
        
        return versions_list
    
    def get_similar_books(self, book_id:int):
        """
        Find similar books in the database using book id
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_similar_books_query, book_id)
        return(result)
    
    @staticmethod
    def get_similar_books_query(tx, book_id):
        query = """
        match (b:Book {id:$book_id})-[rr:SIMILAR_TO]->(bb:Book) 
        return bb.id as id,
        bb.title as title,
        bb.img_url as img_url
        """
        result = tx.run(query,book_id=book_id)
        result = [BookSimilar(**response) for response in result]
        return(result)

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
        
    def create_book(self, book:Book):
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
        title=book.title 
        img_url=book.img_url 
        pages=book.pages
        publication_year=book.publication_year 
        lang=book.lang 
        description=book.description
        genres=book.genres
        authors=book.authors
        isbn13= book.isbn13
        isbn10= book.isbn10
        small_img_url=book.small_img_url
        author_names=book.author_names
        genre_names=book.genre_names
        google_id=book.google_id

        
        genre_repo = GenreCRUDRepositoryGraph(driver=graph_db) 
        author_repo = AuthorCRUDRepositoryGraph(driver=graph_db)

        if not genres:
            for genre_name in genre_names:
                result = genre_repo.get_genre_by_name(genre_name)
                if result:
                    genres.append(result)
                else:
                    result = genre_repo.create_genre(genre_name)
                    genres.append(result)
        
        if not authors:
            for author_name in author_names:
                result = author_repo.get_author_by_name(author_name)
                if result:
                    authors.append(result)
                else:
                    result = author_repo.create_author(author_name)
                    authors.append(result.id)

        with self.driver.session() as session:
            book = session.execute_write(self.create_book_query,
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
                                            google_id)
        return(book)

    @staticmethod
    def create_book_query(tx,title, img_url, 
                        pages, publication_year, lang, 
                        description, genres, authors, isbn13, isbn10,
                        small_img_url, author_names,google_id):
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
                google_id:$google_id})
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
                        google_id=google_id)
        
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
                
        book = Book(id=book_id, 
                    title=title, 
                    img_url=img_url, 
                    pages=pages, 
                    publication_year=publication_year, 
                    lang=lang, 
                    description=description, 
                    isbn13=isbn13,
                    genres=genres,
                    authors=authors)

        return(book)
    
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

    def update_book_preview(self, book:BookUpdate):
        """
        Updates the book preview in the DB
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_book_preview_query, book)  
        return(result)
    
    @staticmethod
    def update_book_preview_query(tx, book):
        query = """
                        match (b:Book {id:$google_id})
                        set b.id = randomUUID(),
                            b.google_id = $google_id,
                            b.description = $description,
                            b.isbn13 = $isbn13,
                            b.isbn10 = $isbn10,
                            b.img_url = $img_url,
                            b.lang = $lang,
                            b.publication_year = $publication_year,
                            b.pages = $pages
                            return b.id as id
                        """
        
        result = tx.run(query,
                        google_id=book.google_id,
                        description=book.description,
                        isbn13=book.isbn13,
                        isbn10=book.isbn10,
                        img_url=book.img_url,
                        lang=book.lang,
                        publication_year=book.publication_year,
                        pages=book.pages)
        
        response = result.single()
        book_id = response['id']
        return(book_id)
        

    def delete_book_and_versions_by_google_id(self, google_id):
        """
        Deletes a book and all its versions from the DB
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_book_and_versions_by_google_id_query, google_id=google_id)  
        return(result)
    
    @staticmethod
    def delete_book_and_versions_by_google_id_query(tx, google_id):
        query = """
                match (book:Book {google_id:$google_id})
                with book
                optional match (book)-[r:HAS_VERSION]->(version)
                detach delete book, version
                """
        result = tx.run(query, google_id=google_id)
        return(result)