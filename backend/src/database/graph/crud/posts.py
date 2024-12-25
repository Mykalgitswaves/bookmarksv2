from src.database.graph.crud.base import BaseCRUDRepositoryGraph

from src.database.graph.base import graph_db
from src.models.schemas.posts import (
    ReviewPost, 
    ReviewCreate, 
    UpdateCreate, 
    UpdatePost, 
    ComparisonCreate, 
    ComparisonPost, 
    RecommendationFriendCreate,
    RecommendationFriend,
    MilestoneCreate,
    MilestonePost,
    LikedPost,
    WantToReadCreate,
    CurrentlyReadingCreate,
    WantToReadPost,
    CurrentlyReadingPost
)
from src.models.schemas.books import BookPreview

class PostCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def create_review(self, review_post:ReviewCreate):
        """
        Creates a review in the database
        Args:
            review_post:ReviewPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            review_id: PK of the review_post in DB
        """
        with self.driver.session() as session:
            review = session.execute_write(self.create_review_query, review_post)
        return(review)
    
    @staticmethod
    def create_review_query(tx, review_post):
        query = """
                match (u:User {username:$username})
                match (b:Book {id:$book_id})
                create (r:Review {id:randomUUID(), 
                                created_date:datetime(),
                                headline:$headline,
                                questions:$questions,
                                question_ids:$question_ids,
                                responses:$responses,
                                spoilers:$spoilers,
                                rating:$rating,
                                deleted:false,
                                likes:0})
                create (u)-[p:POSTED]->(r)
                create (r)-[pp:POST_FOR_BOOK]->(b)
                return r.created_date as created_date, 
                    r.id as review_id
                """
        result = tx.run(query, 
                        username=review_post.user_username, 
                        book_id=review_post.book.id, 
                        headline=review_post.headline, 
                        questions=review_post.questions,
                        question_ids=review_post.question_ids,
                        responses=review_post.responses,
                        spoilers=review_post.spoilers,
                        rating=review_post.rating)
        
        response = result.single()
        review = ReviewPost(
                        user_username=review_post.user_username, 
                        book=review_post.book,
                        headline=review_post.headline, 
                        questions=review_post.questions,
                        question_ids=review_post.question_ids,
                        responses=review_post.responses,
                        spoilers=review_post.spoilers,
                        rating=review_post.rating,
                        created_date=response['created_date'],
                        id=response['review_id']
        )
        return(review)
    
    def create_review_and_book(self, review_post:ReviewCreate):
        """
        Creates a review in the database and the book that it is associated with
        Args:
            review_post:ReviewPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            review_id: PK of the review_post in DB
        """
        with self.driver.session() as session:
            review = session.execute_write(self.create_review_and_book_query, review_post)
        return(review)
    
    @staticmethod
    def create_review_and_book_query(tx, review_post):
        query = """
                match (u:User {username:$username})
                create (b:Book {id:"c"+randomUUID(),
                                google_id:$book_id, 
                                title:$title, 
                                small_img_url:$small_img_url})
                create (r:Review {id:randomUUID(), 
                                created_date:datetime(),
                                headline:$headline,
                                questions:$questions,
                                question_ids:$question_ids,
                                responses:$responses,
                                spoilers:$spoilers,
                                rating:$rating,
                                deleted:false,
                                likes:0})
                create (u)-[p:POSTED]->(r)
                create (r)-[pp:POST_FOR_BOOK]->(b)
                return r.created_date as created_date, 
                    r.id as review_id,
                    b.id as book_id
                """
        result = tx.run(query, 
                        username=review_post.user_username, 
                        book_id=review_post.book.id, 
                        title=review_post.book.title, 
                        small_img_url=review_post.book.small_img_url, 
                        headline=review_post.headline, 
                        questions=review_post.questions,
                        question_ids=review_post.question_ids,
                        responses=review_post.responses,
                        spoilers=review_post.spoilers,
                        rating=review_post.rating)
        
        response = result.single()
        review_post.book.google_id = review_post.book.id
        review_post.book.id = response['book_id']
        review = ReviewPost(
            user_username=review_post.user_username, 
            book=review_post.book,
            headline=review_post.headline, 
            questions=review_post.questions,
            question_ids=review_post.question_ids,
            responses=review_post.responses,
            spoilers=review_post.spoilers,
            rating=review_post.rating,
            created_date=response['created_date'],
            id=response['review_id']
        )
        return(review)
    
    def create_update(self, update_post:UpdateCreate):
        """
        Creates a review in the database
        Args:
            update_post: UpdatePost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            update_id: PK of the update in the db
        """
        with self.driver.session() as session:
            update_result = session.execute_write(self.create_update_query, update_post)
        return(update_result)
    
    @staticmethod
    def create_update_query(tx, update_post):
        query = """
            match (u:User {username:$username})
            match (b:Book {id:$book_id})
            MATCH (u)-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(b)
            create (d:Update {id:randomUUID(), 
                            created_date:datetime(),
                            page:$page,
                            chapter:$chapter,
                            headline:$headline,
                            response:$response,
                            spoiler:$spoiler,
                            quote:$quote,
                            deleted:false,
                            likes:0})
            create (u)-[p:POSTED]->(d)
            create (d)-[pp:POST_FOR_BOOK]->(b)
            set rr.current_page = $page
            set rr.last_updated = datetime()
            return d.created_date, d.id
            """
        result = tx.run(query, 
                        username=update_post.user_username, 
                        book_id=update_post.book.id,
                        page=update_post.page, 
                        headline=update_post.headline, 
                        response=update_post.response,
                        spoiler=update_post.spoiler,
                        quote=update_post.quote)
        
        response = result.single()
        update_result = UpdatePost(
                        user_username=update_post.user_username, 
                        book=update_post.book,
                        page=update_post.page, 
                        chapter=update_post.chaper,
                        headline=update_post.headline, 
                        response=update_post.response,
                        spoiler=update_post.spoiler,
                        quote=update_post.quote,
                        created_date=response['d.created_date'],
                        id=response['d.id']
        )   
        return(update_result)
    
    def create_update_and_book(self, update_post:UpdateCreate):
        """
        Creates a update in the database and book
        Args:
            update_post: UpdatePost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            update_id: PK of the update in the db
        """
        with self.driver.session() as session:
            update_result = session.execute_write(self.create_update_and_book_query, update_post)
        return(update_result)
    
    @staticmethod
    def create_update_and_book_query(tx, update_post):
        query = """
            match (u:User {username:$username})
            create (b:Book {id:"c"+randomUUID(),
                            google_id:$book_id, 
                            title:$title, 
                            small_img_url:$small_img_url})
            MATCH (u)-[:HAS_READING_FLOW_SHELF]->(shelf:CurrentlyReadingShelf)
            OPTIONAL MATCH (shelf)-[rr:CONTAINS_BOOK]->(b)
            create (d:Update {id:randomUUID(), 
                            created_date:datetime(),
                            page:$page,
                            headline:$headline,
                            response:$response,
                            spoiler:$spoiler,
                            quote:$quote,
                            deleted:false,
                            likes:0})
            create (u)-[p:POSTED]->(d)
            create (d)-[pp:POST_FOR_BOOK]->(b)
            set rr.current_page = $page
            set rr.last_updated = datetime()
            return d.created_date, d.id, b.id as book_id
            """
        result = tx.run(query, 
                        username=update_post.user_username, 
                        book_id=update_post.book.id, 
                        title=update_post.book.title, 
                        small_img_url=update_post.book.small_img_url,
                        page=update_post.page, 
                        headline=update_post.headline, 
                        response=update_post.response,
                        spoiler=update_post.spoiler,
                        quote=update_post.quote)
        
        response = result.single()
        update_post.book.google_id = update_post.book.id
        update_post.book.id = response['book_id']
        update_result = UpdatePost(
                        user_username=update_post.user_username, 
                        book=update_post.book,
                        page=update_post.page, 
                        headline=update_post.headline, 
                        response=update_post.response,
                        spoiler=update_post.spoiler,
                        quote=update_post.quote,
                        created_date=response['d.created_date'],
                        id=response['d.id']
        )   
        return(update_result)
    
    def create_comparison(self, comparison_post:ComparisonCreate):
        """
        Creates a review in the database
        Args:
            comparison_post: ComparisonPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            comparison_id: PK of the comparison in the db
        """
        with self.driver.session() as session:
            comparison_result = session.execute_write(self.create_comparison_query, comparison_post)
        return(comparison_result)
    
    @staticmethod
    def create_comparison_query(tx, comparison_post):
        query = """
        match (u:User {username:$username})
        match (b:Book {id:$book_id_1})
        match (bb:Book {id:$book_id_2})
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
                        book_id_1=comparison_post.compared_books[0].id,
                        book_id_2=comparison_post.compared_books[1].id,
                        comparators=comparison_post.comparators,
                        comparator_ids=comparison_post.comparator_ids,
                        responses=comparison_post.responses,
                        book_specific_headlines=comparison_post.book_specific_headlines)
        
        response = result.single()
        
        comparison_result = ComparisonPost(
                        user_username=comparison_post.user_username, 
                        compared_books=comparison_post.compared_books,
                        comparators=comparison_post.comparators,
                        comparator_ids=comparison_post.comparator_ids,
                        responses=comparison_post.responses,
                        book_specific_headlines=comparison_post.book_specific_headlines,
                        created_date=response['c.created_date'],
                        id=response['c.id']
        )
        return(comparison_result)
    
    def create_comparison_and_books(self, comparison_post:ComparisonCreate):
        """
        Creates a review in the database
        Args:
            comparison_post: ComparisonPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            comparison_id: PK of the comparison in the db
        """
        with self.driver.session() as session:
            comparison_result = session.execute_write(self.create_comparison_and_books_query, comparison_post)
        return(comparison_result)
    
    @staticmethod
    def create_comparison_and_books_query(tx, comparison_post):
        query = """
        match (u:User {username:$username})
        merge (b:Book {google_id:$book_id_1})
        on create set b.title=$title_1, b.small_img_url=$small_img_url_1, b.id="c"+randomUUID()
        merge (bb:Book {google_id:$book_id_2})
        on create set bb.title=$title_2, bb.small_img_url=$small_img_url_2, bb.id="c"+randomUUID()
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

        return c.created_date, 
               c.id, 
               b.id as book_id_1, 
               bb.id as book_id_2,
               b.google_id as book_google_id_1,
                bb.google_id as book_google_id_2 
                """
        result = tx.run(query, 
                        username=comparison_post.user_username, 
                        book_id_1=comparison_post.compared_books[0].id,
                        book_id_2=comparison_post.compared_books[1].id,
                        title_1=comparison_post.compared_books[0].title,
                        title_2=comparison_post.compared_books[1].title,
                        small_img_url_1=comparison_post.compared_books[0].small_img_url,
                        small_img_url_2=comparison_post.compared_books[1].small_img_url,
                        comparators=comparison_post.comparators,
                        comparator_ids=comparison_post.comparator_ids,
                        responses=comparison_post.responses,
                        book_specific_headlines=comparison_post.book_specific_headlines)
        
        response = result.single()

        comparison_post.compared_books[0].google_id = response['book_google_id_1']
        comparison_post.compared_books[0].id = response['book_id_1']
        comparison_post.compared_books[1].google_id = response['book_google_id_2']
        comparison_post.compared_books[1].id = response['book_id_2']
        
        comparison_result = ComparisonPost(
                        user_username=comparison_post.user_username, 
                        compared_books=comparison_post.compared_books,
                        comparators=comparison_post.comparators,
                        comparator_ids=comparison_post.comparator_ids,
                        responses=comparison_post.responses,
                        book_specific_headlines=comparison_post.book_specific_headlines,
                        created_date=response['c.created_date'],
                        id=response['c.id']
        )
        return(comparison_result)
    
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
            recommendation_result = session.execute_write(self.create_recommendation_post_query, recommendation_post)
        return(recommendation_result)
    
    @staticmethod
    def create_recommendation_post_query(tx, recommendation_post):
        query = """
        match (u:User {username:$username})
        match (f:User {username:$to_user_username})
        match (b:Book {id:$book_id})
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
                        book_id=recommendation_post.book.id,
                        to_user_username=recommendation_post.to_user_username,
                        from_user_text=recommendation_post.from_user_text, 
                        to_user_text=recommendation_post.to_user_text)
        
        response = result.single()
        recommendation_result = RecommendationFriend(
                        user_username=recommendation_post.user_username, 
                        book=recommendation_post.book,
                        to_user_username=recommendation_post.to_user_username,
                        from_user_text=recommendation_post.from_user_text, 
                        to_user_text=recommendation_post.to_user_text,
                        created_date=response['r.created_date'],
                        id=response['r.id']
        )
        return(recommendation_result)
    
    def create_recommendation_post_and_book(self, recommendation_post:RecommendationFriend):
        """
        Creates a recommendation post and book in the database
        Args:
            recommendation_post: RecommendationFriend object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            recommendation_id: PK of the recommendation in the db
        """
        with self.driver.session() as session:
            recommendation_result = session.execute_write(self.create_recommendation_post_and_book_query, recommendation_post)
        return(recommendation_result)
    
    @staticmethod
    def create_recommendation_post_and_book_query(tx, recommendation_post):
        query = """
        match (u:User {username:$username})
        match (f:User {username:$to_user_username})
        create (b:Book {id:"c"+randomUUID(),
                        google_id:$book_id, 
                        title:$title, 
                        small_img_url:$small_img_url})
        create (r:RecommendationFriend {id:randomUUID(), 
                                        created_date:datetime(),
                                        from_user_text:$from_user_text,
                                        to_user_text:$to_user_text,
                                        deleted:false,
                                        likes:0})
        create (u)-[p:POSTED]->(r)
        create (r)-[rr:RECOMMENDED_TO]->(f)
        create (r)-[pp:POST_FOR_BOOK]->(b)
        return r.created_date, r.id, b.id as book_id
        """
        result = tx.run(query, 
                        username=recommendation_post.user_username, 
                        book_id=recommendation_post.book.id,
                        title=recommendation_post.book.title,
                        small_img_url=recommendation_post.book.small_img_url,
                        to_user_username=recommendation_post.to_user_username,
                        from_user_text=recommendation_post.from_user_text, 
                        to_user_text=recommendation_post.to_user_text)
        
        response = result.single()
        recommendation_post.book.google_id = recommendation_post.book.id
        recommendation_post.book.id = response['book_id']
        recommendation_result = RecommendationFriend(
                        user_username=recommendation_post.user_username, 
                        book=recommendation_post.book,
                        to_user_username=recommendation_post.to_user_username,
                        from_user_text=recommendation_post.from_user_text, 
                        to_user_text=recommendation_post.to_user_text,
                        created_date=response['r.created_date'],
                        id=response['r.id']
        )
        return(recommendation_result)
    
    def create_milestone(self, milestone_post:MilestoneCreate):
        """
        Creates a review in the database
        Args:
            milestone_post: MilestonePost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            milestone_id: PK of the milestone in the db
        """
        with self.driver.session() as session:
            milestone_result = session.execute_write(self.create_milestone_query, milestone_post)
        return(milestone_result)
    
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
        milestone_result = MilestonePost(
                        user_username=milestone_post.user_username, 
                        num_books=milestone_post.num_books,
                        created_date=response['m.created_date'],
                        id=response['m.id']
        )
        return(milestone_result)
    
    def create_want_to_read_post(self, want_to_read_post:WantToReadCreate):
        """
        Creates a review in the database
        Args:
            want_to_read_post: WantToReadPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            want_to_read_id: PK of the want_to_read in the db
        """
        with self.driver.session() as session:
            want_to_read_result = session.execute_write(self.create_want_to_read_post_query, want_to_read_post)
        return(want_to_read_result)
    
    @staticmethod
    def create_want_to_read_post_query(tx, want_to_read_post):
        query = """
        match (u:User {id:$user_id})
        match (b:Book)
        where b.id = $book_id or b.google_id = $book_id
        with u, b
        create (w:WantToReadPost {id:"post_want_to_read_" + randomUUID(),
                            created_date:datetime(),
                            deleted:false,
                            likes:0,
                            visibility:u.visibility,
                            headline:$headline
        })
        create (u)-[r:POSTED]->(w)
        create (w)-[rr:POST_FOR_BOOK]->(b)
        return w.created_date, w.id
        """
        result = tx.run(query, 
                        user_id=want_to_read_post.user_id,
                        book_id=want_to_read_post.book_id,
                        headline=want_to_read_post.headline)
        response = result.single()
        
        return(response)
    
    def create_currently_reading_post(self, currently_reading_post:CurrentlyReadingCreate):
        """
        Creates a review in the database
        Args:
            currently_reading_post: CurrentlyReadingPost object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            currently_reading_id: PK of the currently_reading in the db
        """
        with self.driver.session() as session:
            currently_reading_result = session.execute_write(self.create_currently_reading_post_query, currently_reading_post)
        return(currently_reading_result)
    
    @staticmethod
    def create_currently_reading_post_query(tx, currently_reading_post):
        query = """
        match (u:User {id:$user_id})
        match (b:Book)
        where b.id = $book_id or b.google_id = $book_id
        with u, b
        create (c:CurrentlyReadingPost {id:"post_currently_reading_" + randomUUID(),
                            created_date:datetime(),
                            deleted:false,
                            likes:0,
                            visibility:u.visibility,
                            headline:$headline
        })
        create (u)-[r:POSTED]->(c)
        create (c)-[rr:POST_FOR_BOOK]->(b)
        return c.created_date, c.id
        """
        result = tx.run(query, 
                        user_id=currently_reading_post.user_id,
                        book_id=currently_reading_post.book_id,
                        headline=currently_reading_post.headline)
        response = result.single()
        
        return(response)
    
    def create_post_like(self, liked_post:LikedPost):
        """
        Creates a like relationship between a user and a post
        Args:
            liked_post: LikedPost object to be pushed to DB
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_post_like_query, liked_post)
        return(result)
    
    @staticmethod
    def create_post_like_query(tx, liked_post):
        query = """
                match (uu:User {username: $username}) 
                match (rr {id: $post_id}) 
                merge (uu)-[ll:LIKES]->(rr)
                on create 
                set ll.created_date = datetime(),
                    rr.likes = coalesce(rr.likes, 0) + 1
                return rr.likes as likes
                """
        
        result = tx.run(query, username=liked_post.username, post_id=liked_post.post_id)
        response = result.single()
        print(response)
        return response is not None
    
    def get_feed(self, current_user, skip:int, limit:int): 
        with self.driver.session() as session:
            result = session.execute_read(self.get_feed_query, current_user.username, skip, limit)
        return(result)
    
    @staticmethod
    def get_feed_query(tx, username, skip, limit):
        query = """ 
                    MATCH (p {deleted:false})
                    WHERE p:Milestone OR p:Review OR p:Comparison OR p:Update OR p:WantToReadPost OR p:CurrentlyReadingPost
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
        
        output = []        
        for response in result:
            post = response['p']
            if response['labels(p)'] == ["Milestone"]:
                milestone = MilestonePost(id=post["id"],
                                          created_date=post["created_date"],
                                          num_books=post["num_books"],
                                          user_id=response['u.id'],
                                          user_username=response['u.username'],
                                          likes=post['likes'],
                                          num_comments=response["num_comments"])
                
                milestone.liked_by_current_user = response['liked_by_current_user']
                milestone.posted_by_current_user = response['posted_by_current_user']
                output.append(milestone)                                                       
            
            elif response['labels(p)'] == ['Comparison']:
                if output:
                    if output[-1].id == post["id"]:
                        output[-1].compared_books.append(
                            BookPreview(id=response['b']['id'],
                                        title=response['b']['title'],
                                        small_img_url=response['b']['small_img_url'])
                        )
                        continue
                    
                comparison = ComparisonPost(id=post["id"],
                                            compared_books=[
                                                BookPreview(id=response['b']['id'],
                                                            title=response['b']['title'],
                                                            small_img_url=response['b']['small_img_url'])
                                            ],
                                            user_username=response['u.username'],
                                            user_id=response['u.id'],
                                            comparators=post['comparators'],
                                            created_date=post['created_date'],
                                            comparator_ids=post['comparator_ids'],
                                            responses=post['responses'],
                                            book_specific_headlines=post['book_specific_headlines'],
                                            likes=post['likes'],
                                            num_comments=response["num_comments"])
                
                comparison.liked_by_current_user = response['liked_by_current_user']
                comparison.posted_by_current_user = response['posted_by_current_user']
                output.append(comparison)


            elif response['labels(p)'] == ["Update"]:
                update = UpdatePost(id=post["id"],
                                    book=BookPreview(id=response['b']['id'],
                                            title=response['b']['title'],
                                            small_img_url=response['b']['small_img_url']),
                                    headline=post.get('headline', ""),
                                    created_date=post["created_date"],
                                    page=post['page'],
                                    response=post['response'],
                                    spoiler=post['spoiler'],
                                    quote=post['quote'],
                                    user_id=response['u.id'],
                                    user_username=response['u.username'],
                                    likes=post['likes'],
                                    num_comments=response["num_comments"])
                
                update.liked_by_current_user = response['liked_by_current_user']
                update.posted_by_current_user = response['posted_by_current_user']
                output.append(update)

            elif response['labels(p)'] == ["Review"]:
                review = ReviewPost(
                            id=post["id"],
                            book=BookPreview(
                                id=response['b']['id'],
                                title=response['b']['title'],
                                small_img_url=response['b']['small_img_url']
                            ),
                            headline=post.get('headline', ""),
                            created_date=post["created_date"],
                            questions=post['questions'],
                            question_ids=post['question_ids'],
                            responses=post.get('responses', []),
                            spoilers=post['spoilers'],
                            user_id=response['u.id'],
                            user_username=response['u.username'],
                            num_comments=response["num_comments"],
                            likes=post['likes'],
                            rating=post.get('rating')
                        )
                review.liked_by_current_user = response['liked_by_current_user']
                review.posted_by_current_user = response['posted_by_current_user']
                output.append(review)

            elif response['labels(p)'] == ["WantToReadPost"]:
                want_to_read = WantToReadPost(
                            id=post["id"],
                            book=BookPreview(
                                id=response['b']['id'],
                                title=response['b']['title'],
                                small_img_url=response['b']['small_img_url']
                            ),
                            headline=post.get('headline', ""),
                            created_date=post["created_date"],
                            user_id=response['u.id'],
                            user_username=response['u.username'],
                            num_comments=response["num_comments"],
                            likes=post['likes']
                        )
                want_to_read.liked_by_current_user = response['liked_by_current_user']
                want_to_read.posted_by_current_user = response['posted_by_current_user']
                output.append(want_to_read)

            elif response['labels(p)'] == ["CurrentlyReadingPost"]:
                currently_reading = CurrentlyReadingPost(
                            id=post["id"],
                            book=BookPreview(
                                id=response['b']['id'],
                                title=response['b']['title'],
                                small_img_url=response['b']['small_img_url']
                            ),
                            headline=post.get('headline', ""),
                            created_date=post["created_date"],
                            user_id=response['u.id'],
                            user_username=response['u.username'],
                            num_comments=response["num_comments"],
                            likes=post['likes']
                        )
                currently_reading.liked_by_current_user = response['liked_by_current_user']
                currently_reading.posted_by_current_user = response['posted_by_current_user']
                output.append(currently_reading)
        return(output)
    
    def get_all_reviews_by_username(self, username): 
        with self.driver.session() as session:
            result = session.execute_read(self.get_all_reviews_by_username_query, username)
        return(result)
    
    @staticmethod
    def get_all_reviews_by_username_query(tx, username): # TODO: Not sure if this needs the posted_by_current_user decorator
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
        
        output = []
        for response in results:
            post = response['p']
            if response['labels(p)'] == ["Milestone"]:
                post = MilestonePost(id=post["id"],
                    created_date=post["created_date"],
                    num_books=post["num_books"],
                    user_username=username,
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user'],
                    num_comments=response['num_comments']
                )
                
                output.append(post)
                                                                                                           
                
            elif response['labels(p)'] == ["RecommendationFriend"]:
                recommendation = RecommendationFriend(id=post["id"],
                                    book=BookPreview(id=response['b']['id'], 
                                                     title=response['b']['title'], 
                                                     small_img_url=response['b']['small_img_url']),
                                    created_date=post["created_date"],
                                    to_user_username=response['uu']['username'],
                                    from_user_text=post['from_user_text'],
                                    to_user_text=post['to_user_text'],
                                    user_username=username,
                                    likes=post["likes"],
                                    liked_by_current_user=response['liked_by_current_user'],
                                    num_comments=response['num_comments']
                                )
                
                output.append(recommendation)
            
            elif response['labels(p)'] == ['Comparison']:
                if output:
                    if output[-1].id == post["id"]:
                        output[-1].compared_books.append(BookPreview(id=response['b']['id'], 
                                                                     title=response['b']['title'], 
                                                                     small_img_url=response['b']['small_img_url']))
                        continue

                comparison = ComparisonPost(id=post["id"],
                                compared_books=[BookPreview(id=response['b']['id'], 
                                                            title=response['b']['title'], 
                                                            small_img_url=response['b']['small_img_url'])],
                                user_username=username,
                                comparators=post['comparators'],
                                created_date=post['created_date'],
                                comparator_ids=post['comparator_ids'],
                                responses=post['responses'],
                                book_specific_headlines=post['book_specific_headlines'],
                                likes=post['likes'],
                                liked_by_current_user=response['liked_by_current_user'],
                                num_comments=response['num_comments']
                            )
                
                output.append(comparison)

            elif response['labels(p)'] == ["Update"]:
                update = UpdatePost(id=post["id"],
                                book=BookPreview(id=response['b']['id'], 
                                                     title=response['b']['title'], 
                                                     small_img_url=response['b']['small_img_url']),
                                created_date=post["created_date"],
                                page=post['page'],
                                response=post['response'],
                                spoiler=post['spoiler'],
                                user_username=username,
                                likes=post['likes'],
                                liked_by_current_user=response['liked_by_current_user'],
                                num_comments=response['num_comments'],
                                headline=post.get('headline', "")
                            )
                
                output.append(update)

            elif response['labels(p)'] == ["Review"]:
                    
                    review = ReviewPost(id=post["id"],
                                book=BookPreview(id=response['b']['id'], 
                                                     title=response['b']['title'], 
                                                     small_img_url=response['b']['small_img_url']),
                                created_date=post["created_date"],
                                questions=post['questions'],
                                question_ids=post['question_ids'],
                                responses=post['responses'],
                                spoilers=post['spoilers'],
                                user_username=username,
                                liked_by_current_user=response['liked_by_current_user'],
                                num_comments=response['num_comments'],
                                likes=post['likes'],
                                headline=post.get('headline', ""),
                                rating=post.get('rating')
                            )
                    
                    output.append(review)

            elif response['labels(p)'] == ["WantToReadPost"]:
                want_to_read = WantToReadPost(
                    id=post["id"],
                    book=BookPreview(
                        id=response['b']['id'], 
                        title=response['b']['title'], 
                        small_img_url=response['b']['small_img_url']),
                    created_date=post["created_date"],
                    user_username=username,
                    headline=post.get('headline', ""),
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user'],
                    num_comments=response['num_comments']
                )

                output.append(want_to_read)

            elif response['labels(p)'] == ["CurrentlyReadingPost"]:
                currently_reading = CurrentlyReadingPost(
                    id=post["id"],
                    book=BookPreview(
                        id=response['b']['id'], 
                        title=response['b']['title'], 
                        small_img_url=response['b']['small_img_url']),
                    created_date=post["created_date"],
                    user_username=username,
                    headline=post.get('headline', ""),
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user'],
                    num_comments=response['num_comments']
                )
                
                output.append(currently_reading)
        return(output)
    
    def get_all_reviews_by_user_id(self, user_id): 
        with self.driver.session() as session:
            result = session.execute_read(self.get_all_reviews_by_user_id_query, user_id)
        return(result)
    
    @staticmethod
    def get_all_reviews_by_user_id_query(tx, user_id): # TODO: Not sure if this needs the posted_by_current_user decorator
        query = """ match (u:User {id:$user_id})-[r:POSTED]->(p {deleted:false})
                    optional match (p)-[rb:POST_FOR_BOOK]-(b)
                    optional match (p)-[ru:RECOMMENDED_TO]->(uu)
                    optional match (p)<-[rl:LIKES]-(u)
                    optional match (comments:Comment {deleted:false})<-[:HAS_COMMENT]-(p)
                    return p, labels(p), b, uu, u.username as username,
                    CASE WHEN rl IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
                    count(comments) as num_comments
                    order by p.created_date desc"""
        result = tx.run(query, user_id=user_id)
        results = [record for record in result.data()]
        
        output = []
        for response in results:
            post = response['p']
            if response['labels(p)'] == ["Milestone"]:
                post = MilestonePost(id=post["id"],
                    created_date=post["created_date"],
                    num_books=post["num_books"],
                    user_username=response['username'],
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user'],
                    num_comments=response['num_comments']
                )
                
                output.append(post)
                                                                                                           
                
            elif response['labels(p)'] == ["RecommendationFriend"]:
                recommendation = RecommendationFriend(id=post["id"],
                                    book=BookPreview(id=response['b']['id'], 
                                                     title=response['b']['title'], 
                                                     small_img_url=response['b']['small_img_url']),
                                    created_date=post["created_date"],
                                    to_user_username=response['uu']['username'],
                                    from_user_text=post['from_user_text'],
                                    to_user_text=post['to_user_text'],
                                    user_username=response['username'],
                                    likes=post["likes"],
                                    liked_by_current_user=response['liked_by_current_user'],
                                    num_comments=response['num_comments']
                                )
                
                output.append(recommendation)
            
            elif response['labels(p)'] == ['Comparison']:
                if output:
                    if output[-1].id == post["id"]:
                        output[-1].compared_books.append(BookPreview(id=response['b']['id'], 
                                                                     title=response['b']['title'], 
                                                                     small_img_url=response['b']['small_img_url']))
                        continue

                comparison = ComparisonPost(id=post["id"],
                                compared_books=[BookPreview(id=response['b']['id'], 
                                                            title=response['b']['title'], 
                                                            small_img_url=response['b']['small_img_url'])],
                                user_username=response['username'],
                                comparators=post['comparators'],
                                created_date=post['created_date'],
                                comparator_ids=post['comparator_ids'],
                                responses=post['responses'],
                                book_specific_headlines=post['book_specific_headlines'],
                                likes=post['likes'],
                                liked_by_current_user=response['liked_by_current_user'],
                                num_comments=response['num_comments']
                            )
                
                output.append(comparison)

            elif response['labels(p)'] == ["Update"]:
                update = UpdatePost(id=post["id"],
                                book=BookPreview(id=response['b']['id'], 
                                                     title=response['b']['title'], 
                                                     small_img_url=response['b']['small_img_url']),
                                created_date=post["created_date"],
                                page=post['page'],
                                response=post['response'],
                                spoiler=post['spoiler'],
                                user_username=response['username'],
                                likes=post['likes'],
                                liked_by_current_user=response['liked_by_current_user'],
                                num_comments=response['num_comments'],
                                headline=post.get('headline', "")
                            )
                
                output.append(update)

            elif response['labels(p)'] == ["Review"]:
                    
                    review = ReviewPost(id=post["id"],
                                book=BookPreview(id=response['b']['id'], 
                                                     title=response['b']['title'], 
                                                     small_img_url=response['b']['small_img_url']),
                                created_date=post["created_date"],
                                questions=post['questions'],
                                question_ids=post['question_ids'],
                                responses=post['responses'],
                                spoilers=post['spoilers'],
                                user_username=response['username'],
                                liked_by_current_user=response['liked_by_current_user'],
                                num_comments=response['num_comments'],
                                likes=post['likes'],
                                headline=post.get('headline', ""),
                                rating=post.get('rating')
                            )
                    
                    output.append(review)

            elif response['labels(p)'] == ["WantToReadPost"]:
                want_to_read = WantToReadPost(
                    id=post["id"],
                    book=BookPreview(
                        id=response['b']['id'], 
                        title=response['b']['title'], 
                        small_img_url=response['b']['small_img_url']),
                    created_date=post["created_date"],
                    user_username=response['username'],
                    headline=post.get('headline', ""),
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user'],
                    num_comments=response['num_comments']
                )
                output.append(want_to_read)

            elif response['labels(p)'] == ["CurrentlyReadingPost"]:
                currently_reading = CurrentlyReadingPost(
                    id=post["id"],
                    book=BookPreview(
                        id=response['b']['id'], 
                        title=response['b']['title'], 
                        small_img_url=response['b']['small_img_url']),
                    created_date=post["created_date"],
                    user_username=response['username'],
                    headline=post.get('headline', ""),
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user'],
                    num_comments=response['num_comments']
                )
                
                output.append(currently_reading)

        return(output)
    
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
            optional match (p)-[:POST_FOR_BOOK]-(b:Book)
            match (pu:User)-[pr:POSTED]->(p)
            optional match (cu:User)-[lr:LIKES]->(p)
            return p, labels(p), b.id, b.title, b.small_img_url, pu.username, pu.id,
            CASE WHEN lr IS NOT NULL THEN true ELSE false END AS liked_by_current_user,
            CASE WHEN pu.username = $username THEN true ELSE false END AS posted_by_current_user
        """

        result = tx.run(query, post_id=post_id, username=username)
        result = [record for record in result.data()]
        if not result:
            return None
        response = result[0]
        post = response['p']

        user_id = response["pu.id"]

        if response['labels(p)'] == ["Milestone"]:
            output = MilestonePost(id=post["id"],
                    created_date=post["created_date"],
                    num_books=post["num_books"],
                    user_username=username,
                    likes=post['likes'],
                    liked_by_current_user=response['liked_by_current_user']
                )                                                      
            
        elif response['labels(p)'] == ['Comparison']:
            books = []
            
            for response in result:
                books.append(BookPreview(id = response['b.id'],
                                         title = response['b.title'],
                                        small_img_url = response['b.small_img_url']))
                
            output = ComparisonPost(id=post['id'],
                            compared_books=books,
                            user_username=response["pu.username"],
                            comparators=post['comparators'],
                            created_date=post['created_date'],
                            comparator_ids=post['comparator_ids'],
                            responses=post['responses'],
                            book_specific_headlines=post['book_specific_headlines'],
                            likes=post['likes'],
                            liked_by_current_user=response['liked_by_current_user'],
                            posted_by_current_user=response['posted_by_current_user']
                            )
            
        elif response['labels(p)'] == ["Update"]:

            output = UpdatePost(id=post["id"],
                                book=BookPreview(id = response['b.id'],
                                         title = response['b.title'],
                                        small_img_url = response['b.small_img_url']),
                                created_date=post["created_date"],
                                page=post['page'],
                                response=post['response'],
                                spoiler=post['spoiler'],
                                headline=post.get('headline'),
                                quote=post.get('quote'),
                                user_username=response["pu.username"],
                                likes=post['likes'],
                                liked_by_current_user=response['liked_by_current_user'],
                                posted_by_current_user=response['posted_by_current_user']
                                )

        elif response['labels(p)'] == ["Review"]:
                output = ReviewPost(id=post["id"],
                                    book=BookPreview(id = response['b.id'],
                                         title = response['b.title'],
                                        small_img_url = response['b.small_img_url']),
                                    created_date=post["created_date"],
                                    questions=post['questions'],
                                    question_ids=post['question_ids'],
                                    responses=post['responses'],
                                    spoilers=post['spoilers'],
                                    headline=post.get('headline'),
                                    user_username=response["pu.username"],
                                    likes=post['likes'],
                                    liked_by_current_user=response['liked_by_current_user'],
                                    posted_by_current_user=response['posted_by_current_user'],
                                    rating=post.get('rating')
                                    )
        
        elif response['labels(p)'] == ["WantToReadPost"]:
            output = WantToReadPost(
                id=post["id"],
                book=BookPreview(
                    id = response['b.id'],
                    title = response['b.title'],
                    small_img_url = response['b.small_img_url']),
                created_date=post["created_date"],
                headline=post.get('headline',""),
                user_username=response["pu.username"],
                likes=post['likes'],
                liked_by_current_user=response['liked_by_current_user']
                )
        
        elif response['labels(p)'] == ["CurrentlyReadingPost"]:
            output = CurrentlyReadingPost(
                id=post["id"],
                book=BookPreview(
                    id = response['b.id'],
                    title = response['b.title'],
                    small_img_url = response['b.small_img_url']),
                created_date=post["created_date"],
                headline=post.get('headline',""),
                user_username=response["pu.username"],
                likes=post['likes'],
                liked_by_current_user=response['liked_by_current_user']
                )
                
        return({"post": output, "user_id": user_id})
    
    def update_post_to_deleted(self,post_id, username):
        """
        update deleted flag of a post and all comments on that post to True
        
        Args:
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_post_to_deleted_query, post_id, username)
        return result
       
    @staticmethod
    def update_post_to_deleted_query(tx, post_id, username):
        query = """
                match (u:User {username: $username})-[postRel:POSTED]->(pp {id: $post_id})
                optional match (postComment:Comment)<-[commentRel:HAS_COMMENT]-(pp)
                set pp.deleted=true
                set postComment.deleted=true
                return pp.id as post_id
                """
        result = tx.run(query, post_id=post_id, username=username)
        response = result.single()
        return response is not None
    
    def delete_post(self, post_id):
        """
        update deleted flag of a post and all comments on that post to True
        
        Args:
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_post_query, post_id)
        return result
       
    @staticmethod
    def delete_post_query(tx, post_id):
        query = """
                match (pp {id: $post_id})
                optional match (postComment:Comment)<-[commentRel:HAS_COMMENT]-(pp)
                detach delete pp, postComment
                """
        result = tx.run(query, post_id=post_id)
        response = result.single()
        return response is not None
    
    def delete_post_like(self, liked_post:LikedPost):
        """
        removes a liked post for a user
        
        Args:
            username: users PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_post_like_query, liked_post)    
        return result
    
    @staticmethod
    def delete_post_like_query(tx, liked_post):
        query = """
                match (uu:User {username: $username}) 
                match (rr {id: $post_id}) 
                match (uu)-[ll:LIKES]->(rr)
                delete ll
                WITH rr
                WHERE rr.likes > 0
                SET rr.likes = rr.likes - 1
                return rr.likes as likes
                """
        result = tx.run(query, username=liked_post.username, post_id=liked_post.post_id)
        response = result.single()
        return response is not None