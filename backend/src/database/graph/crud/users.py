from fastapi import HTTPException
from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.users import UserCreate, User, UserLogin, UserWithPassword, UserSettings, UserAboutMe
from src.models.schemas.social import (
    FriendRequestCreate, 
    BlockUserCreate, 
    FollowUserCreate, 
    FriendRequest, 
    FriendDelete, 
    FriendUser, 
    BlockedUser,
    FriendActivity,
    LikedPostActivity,
    LikedCommentActivity,
    CommentedOnPostActivity,
    RepliedToCommentActivity,
    PinnedCommentActivity,
    SuggestedFriend)

class UserCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def create_user(self, user_create: UserCreate) -> User:
        with self.driver.session() as session:
            response = session.execute_write(self.create_user_query, user_create)
        return User(**response.data())
    
    @staticmethod
    def create_user_query(tx, user_create: UserCreate):
        query = """
                create (u:User {
                    id:randomUUID(),
                    username:$username,
                    email:$email,
                    password:$password,
                    created_date:datetime(),
                    disabled:False}) 
                    return u.id as id, 
                    u.username as username, 
                    u.email as email, 
                    u.created_date as created_date, 
                    u.disabled as disabled
                """
        
        result = tx.run(query,
                        username=user_create.username,
                        email=user_create.email,
                        password=user_create.password)
        response = result.single()
        return response
    
    def create_friend_request(self,friend_request:FriendRequestCreate):
        """
        creates a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_friend_request_query, friend_request=friend_request)  
        return(result)
    
    @staticmethod
    def create_friend_request_query(tx, friend_request):
        query = """
        match (fromUser:User {id:$from_user_id, disabled:False})
        match (toUser:User {id:$to_user_id, disabled:False})
        with toUser, fromUser
        where not exists ((fromUser)-[:BLOCKED]-(toUser))
            and not exists ((fromUser)-[:FRIENDED]-(toUser))
            create (fromUser)-[friend_request:FRIENDED {status:"pending", created_date:datetime()}]->(toUser)
        return toUser.id, friend_request.status
        """
        
        result = tx.run(query,from_user_id=friend_request.from_user_id,to_user_id=friend_request.to_user_id)

        response = result.single()
        return response is not None
    
    def create_follow_relationship(self,follow_user:FollowUserCreate):
        """
        Follows a user if the to_user has a critic account
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_follow_relationship_query, follow_user=follow_user)  
        return(result)
    
    @staticmethod
    def create_follow_relationship_query(tx, follow_user):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id, user_type:"critic"})
        where not exists ((fromUser)-[:BLOCKED]-(toUser))
            merge (fromUser)-[followRel:FOLLOWS {created_date:datetime()}]->(toUser)
        RETURN followRel
        """
        
        result = tx.run(query,from_user_id=follow_user.from_user_id,to_user_id=follow_user.to_user_id)
        response = result.single()
        return response is not None
    
    def create_blocked_relationship(self,block_user:BlockUserCreate):
        """
        blocks a user, deletes all existing relationships to the user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_blocked_relationship_query, block_user=block_user)  
        return(result)
    
    @staticmethod
    def create_blocked_relationship_query(tx, block_user):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        optional match (fromUser)-[anyRel]-(toUser)
        delete anyRel
        merge (fromUser)-[blockRel:BLOCKED]->(toUser)
        RETURN Case when blockRel is not null then true else false end as foundRelationship
        """
        
        result = tx.run(query,from_user_id=block_user.from_user_id,to_user_id=block_user.to_user_id)
        response = result.single()
        return response is not None
    
    def is_username_taken(self, username: str) -> bool:
        with self.driver.session() as session:
            response = session.execute_read(self.is_username_taken_query, username=username)
        
        return response
    
    @staticmethod
    def is_username_taken_query(tx, username: str):
        query = """
                match (u:User {username:$username})
                return u
                """
        
        result = tx.run(query, username=username)
        response = result.single()
        return response is not None
    
    
    def is_email_taken(self, email: str) -> bool:  
        with self.driver.session() as session:
            response = session.execute_read(
                self.is_email_taken_query,
                email=email
            )
        
        return response
    
    @staticmethod
    def is_email_taken_query(tx, email: str):
        query = """
                match (u:User {email:$email})
                return u
                """
        
        result = tx.run(query, email=email)
        response = result.single()
        return response is not None
    
    def get_user_by_email(self, email: str) -> UserWithPassword:
        with self.driver.session() as session:
            response = session.execute_read(self.get_user_by_email_query, email=email)
        
        if response:
            return UserWithPassword(**response.data())
        else:
            return None

    @staticmethod
    def get_user_by_email_query(tx, email: str):
        query = """
                match (u:User {email:$email})
                return u.id as id, 
                u.username as username, 
                u.email as email,
                u.password as password,
                u.created_date as created_date, 
                u.disabled as disabled
                """
        
        result = tx.run(query, email=email)
        response = result.single()
        return response
    
    def get_user_by_username(self, username: str) -> UserWithPassword:
        with self.driver.session() as session:
            response = session.execute_read(self.get_user_by_username_query, username=username)
        
        if response:
            return UserWithPassword(**response.data())
        else:
            return None
        
    @staticmethod
    def get_user_by_username_query(tx, username: str):
        query = """
                match (u:User {username:$username})
                return u.id as id, 
                u.username as username, 
                u.email as email,
                u.password as password,
                u.created_date as created_date, 
                u.disabled as disabled
                """
        
        result = tx.run(query, username=username)
        response = result.single()
        return response
    
    def get_user_liked_genres(self, username: str) -> list[str]:
        with self.driver.session() as session:
            response = session.execute_read(self.get_user_liked_genres_query, username=username)
        
        return response
    
    @staticmethod
    def get_user_liked_genres_query(tx, username: str):
        query = """
                match (u:User {username: $username})-[r:LIKES]->(g:Genre) 
                return g.id as genre_id
                """
        
        result = tx.run(query, username=username)
        genres = [response['genre_id'] for response in result]
    
        return genres
    
    def get_user_liked_authors(self, username: str) -> list[str]:
        with self.driver.session() as session:
            response = session.execute_read(self.get_user_liked_authors_query, username=username)
        
        return response
    
    @staticmethod
    def get_user_liked_authors_query(tx, username: str):
        query = """
                match (u:User {username: $username})-[r:LIKES]->(a:Author) 
                return a.id as author_id
                """
        
        result = tx.run(query, username=username)
        authors = [response['author_id'] for response in result]
    
        return authors
    
    def get_user_properties(self, username: str) -> User:
        with self.driver.session() as session:
            response = session.execute_read(self.get_user_properties_query, username=username)
        
        if response:
            user_dict = response.data()['u']
            del user_dict['password']
            return User(**user_dict)
        else:
            return None
    
    @staticmethod
    def get_user_properties_query(tx, username: str) -> str:
        query = """
                match (u:User {username:$username})
                return u
                """
        
        result = tx.run(query, username=username)
        response = result.single()
        return response
    
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
        user = UserSettings(
            id=response['u']['id'],
            username=response['u']['username'],
            email=response['u']['email'] or '',
            disabled=response['u']['disabled'] or False,
            full_name=response['u']['fullname'] or '',
            created_date=response['u']['created_date'],
            profile_img_url=response['u']['profile_img_url'] or '',
            bio=response['u']['bio'] or '',
            relationship_to_current_user=response['u']['relationship_to_current_user'] or relationship_to_current_user,
        )
        return user
    
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

        user = UserAboutMe()

        for response in result:
            if response['g']:
                user.genres.add(
                    (response['g']['name'], response['g']['id'])
                )
            
            if response['a']:
                user.authors.add(
                    (response['a']['name'], response['a']['id'])
                )

        return user
    
    def get_friend_list(self,user_id:str, current_user_id:str):
        """
        Returns all the friends of user and their relationships to current_user
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_friend_list_query, user_id=user_id, current_user_id=current_user_id)  
        return(result)
    
    @staticmethod
    def get_friend_list_query(tx, user_id:str, current_user_id:str):
        query = """
        match (user:User {id:$user_id})
        match (currentUser:User {id:$current_user_id})
        match (user)-[friendRel:FRIENDED {status:"friends"}]-(toUser:User {disabled:False})
        OPTIONAL MATCH (currentUser)<-[incomingFriendStatus:FRIENDED]-(toUser)
        OPTIONAL MATCH (currentUser)-[outgoingFriendStatus:FRIENDED]->(toUser)
        OPTIONAL MATCH (currentUser)<-[incomingBlockStatus:BLOCKED]-(toUser)
        OPTIONAL MATCH (currentUser)-[outgoingBlockStatus:BLOCKED]->(toUser)
        OPTIONAL MATCH (currentUser)<-[incomingFollowStatus:FOLLOWS]-(toUser)
        OPTIONAL MATCH (currentUser)-[outgoingFollowStatus:FOLLOWS]->(toUser)
        RETURN toUser, currentUser,
            incomingFriendStatus.status AS incomingFriendStatus,
            incomingBlockStatus,
            incomingFollowStatus,
            outgoingFriendStatus.status AS outgoingFriendStatus,
            outgoingBlockStatus,
            outgoingFollowStatus
        """
        
        result = tx.run(query,user_id=user_id, current_user_id=current_user_id)
        friend_list = []
        for response in result:
            if 'profile_img_url' in response['toUser']:
                profile_img_url = response['toUser']['profile_img_url']
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
            elif response['toUser']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'stranger'

            friend = FriendUser(
                id=response['toUser']['id'],
                username=response['toUser']['username'],
                disabled=False,
                created_date=response['toUser']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user
            )

            friend_list.append(friend)
        
        return friend_list
    
    def get_simple_friend_list(self,user_id:str):
        """
        Returns all the friends of user and their relationships to current_user
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_simple_friend_list_query, user_id=user_id)  
        return(result)
    
    @staticmethod
    def get_simple_friend_list_query(tx, user_id:str):
        query = """
        match (user:User {id:$user_id})
        match (user)-[friendRel:FRIENDED {status:"friends"}]-(toUser:User {disabled:False})
        RETURN toUser.id as friend_id
        """
        
        result = tx.run(query,user_id=user_id)

        return [response['friend_id'] for response in result]
    
    def get_friend_request_list(self,user_id:str):
        """
        Returns all incoming friend requests for a user
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_friend_request_list_query, user_id=user_id)  
        return(result)
    
    @staticmethod
    def get_friend_request_list_query(tx, user_id):
        query = """
        match (user:User {id:$user_id})
        match (user)<-[friendRel:FRIENDED {status:"pending"}]-(fromUser:User {disabled:False})
        RETURN fromUser, friendRel.created_date as created_date
        """
        
        result = tx.run(query,user_id=user_id)
        friend_request_list = []
        for response in result:
            if 'profile_img_url' in response['fromUser']:
                profile_img_url = response['fromUser']['profile_img_url']
            else:
                profile_img_url = None

            from_user = FriendUser(
                id=response['fromUser']['id'],
                username=response['fromUser']['username'],
                disabled=False,
                created_date=response['fromUser']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user='anonymous_user_friend_requested'
            )

            friend_request = FriendRequest(
                from_user=from_user, 
                created_date=response['created_date'])
            
            friend_request_list.append(friend_request)
        
        return friend_request_list
    
    def get_blocked_users_list(self,user_id:str):
        """
        Returns all blocked users for a user
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_blocked_users_list_query, user_id=user_id)  
        return(result)
    
    @staticmethod
    def get_blocked_users_list_query(tx, user_id):
        query = """
        match (user:User {id:$user_id})
        match (user)-[friendRel:BLOCKED]->(blockedUser:User {disabled:False})
        RETURN blockedUser
        """
        
        result = tx.run(query,user_id=user_id)
        blocked_user_list = []
        for response in result:
            if 'profile_img_url' in response['blockedUser']:
                profile_img_url = response['blockedUser']['profile_img_url']
            else:
                profile_img_url = None

            blocked_user = BlockedUser(
                id=response['blockedUser']['id'],
                username=response['blockedUser']['username'],
                disabled=False,
                created_date=response['blockedUser']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user='current_user_blocked_by_anonymous_user'
            )

            blocked_user_list.append(blocked_user)
        
        return blocked_user_list
    
    def get_activity_list(self, username:str, user_id:str, skip:int, limit:int):
        """
        Returns all activity related to a user
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_activity_list_query, username=username, user_id=user_id, skip=skip, limit=limit)  
        return(result)
    
    @staticmethod
    def get_activity_list_query(tx, username:str, user_id:str, skip:int, limit:int):
        # NOTE: This query is an alternative to the one we are using, incase speed becomes an issue in the future this MAY be faster. We would have to do pagination on our end
        # query = """
        # // Match for recent friendships
        # OPTIONAL MATCH (user:User {id: $user_id})-[f:FRIENDED {status: "friends"}]-(friend:User)
        # RETURN user.id AS userId, friend.id AS acting_user_id, f.created_date AS date, 'friendship' AS activity
        # ORDER BY f.created_date DESC
        # limit 10

        # UNION

        # // OPTIONAL Match for recent likes on content (posts or any type)
        # OPTIONAL MATCH (user:User {id: $user_id})-[:POSTED]->(content)<-[l:LIKES]-(liker:User)
        # RETURN user.id AS userId, liker.id AS acting_user_id, l.created_date AS date, 'likeOnPost' AS activity
        # ORDER BY l.created_date DESC
        # limit 10

        # UNION

        # // OPTIONAL Match for recent likes on comments
        # OPTIONAL MATCH (user:User {id: $user_id})-[:COMMENTED]->(comment)<-[l:LIKES]-(liker:User)
        # RETURN user.id AS userId, liker.id AS acting_user_id, l.created_date AS date, 'likeOnComment' AS activity
        # ORDER BY l.created_date DESC
        # limit 10

        # UNION

        # // OPTIONAL Match for recent comments on posts
        # OPTIONAL MATCH (user:User {id: $user_id})-[:POSTED]->(content)-[c:HAS_COMMENT]-(comment:Comment)<-[:COMMENTED]-(commenter:User)
        # RETURN user.id AS userId, commenter.id AS acting_user_id, comment.created_date AS date, 'commentOnPost' AS activity
        # ORDER BY comment.created_date DESC
        # limit 10

        # UNION

        # // OPTIONAL Match for recent comments on comments
        # OPTIONAL MATCH (user:User {id: $user_id})-[:COMMENTED]->(comment:Comment)<-[:REPLIED_TO]-(reply:Comment)<-[:COMMENTED]-(commenter:User)
        # RETURN user.id AS userId, commenter.id AS acting_user_id, reply.created_date AS date, 'replyToComment' AS activity
        # ORDER BY reply.created_date DESC
        # limit 10

        # UNION

        # // OPTIONAL Match for pins for comments
        # OPTIONAL MATCH (user:User {id: $user_id})-[:COMMENTED]->(comment:Comment)<-[pin:PINNED]-(post)<-[:POSTED]-(pinner:User)
        # RETURN user.id AS userId, pinner.id AS acting_user_id, pin.created_date AS date, 'pinForComment' AS activity
        # ORDER BY pin.created_date DESC
        # limit 10 
        # """

        query = """
        // Collecting friendships
        OPTIONAL MATCH (user:User {id: $user_id})-[f:FRIENDED {status: "friends"}]-(friend:User)
        WITH user, COLLECT({acting_user_id: friend.id, 
                            acting_user_username:friend.username, 
                            acting_user_profile_img_url:friend.profile_img_url, 
                            created_date: f.created_date, 
                            activity: 'friendship'}) AS friendships

        // Collecting likes on content (posts or any type)
        OPTIONAL MATCH (user)-[:POSTED]->(content)<-[l:LIKES]-(liker:User)
        OPTIONAL MATCH (content)-[:POST_FOR_BOOK]->(book:Book)
        WITH user, friendships, content, COLLECT(book.small_img_url) AS book_small_img_urls, liker, l
        WITH user, friendships, COLLECT({acting_user_id: liker.id, 
                                         acting_user_username:liker.username, 
                                         acting_user_profile_img_url:liker.profile_img_url,
                                         post_id:content.id,
                                         book_small_img_urls:book_small_img_urls,
                                         created_date: l.created_date, 
                                         activity: 'liked_post'}) AS likesOnPosts

        // Collecting likes on comments
        OPTIONAL MATCH (user)-[:COMMENTED]->(comment)<-[l:LIKES]-(liker:User)
        OPTIONAL MATCH (comment)<-[:HAS_COMMENT]-(content)-[:POST_FOR_BOOK]->(book:Book)
        WITH user, friendships, likesOnPosts, content, COLLECT(book.small_img_url) AS book_small_img_urls, liker, l, comment
        WITH user, friendships, likesOnPosts, COLLECT({acting_user_id: liker.id, 
                                                       acting_user_username:liker.username, 
                                                       acting_user_profile_img_url:liker.profile_img_url,
                                                       post_id:content.id,
                                                       comment_id:comment.id,
                                                       comment_text:comment.text,
                                                       book_small_img_urls:book_small_img_urls,
                                                       created_date: l.created_date,
                                                       activity: 'liked_comment'}) AS likesOnComments

        // OPTIONAL Match for recent comments on posts
        OPTIONAL MATCH (user)-[:POSTED]->(content)-[:HAS_COMMENT]-(comment:Comment)<-[:COMMENTED]-(commenter:User)
        OPTIONAL MATCH (content)-[:POST_FOR_BOOK]->(book:Book)
        WITH user, friendships, likesOnPosts, likesOnComments, content, COLLECT(book.small_img_url) AS book_small_img_urls, commenter, comment
        WITH user, friendships, likesOnPosts, likesOnComments, COLLECT({acting_user_id: commenter.id, 
                                                                        acting_user_username:commenter.username, 
                                                                        acting_user_profile_img_url:commenter.profile_img_url,
                                                                        post_id:content.id,
                                                                        comment_id:comment.id,
                                                                        comment_text:comment.text,
                                                                        book_small_img_urls:book_small_img_urls,
                                                                        created_date: comment.created_date, 
                                                                        activity: 'commented_on_post'}) AS commentsOnPosts

        // OPTIONAL Match for recent comments on comments
        OPTIONAL MATCH (user)-[:COMMENTED]->(comment:Comment)<-[:REPLIED_TO]-(reply:Comment)<-[:COMMENTED]-(commenter:User)
        OPTIONAL MATCH (comment)-[:HAS_COMMENT]-(content)-[:POST_FOR_BOOK]->(book:Book)
        WITH user, friendships, likesOnPosts, likesOnComments, commentsOnPosts, content, COLLECT(book.small_img_url) AS book_small_img_urls, commenter, comment, reply
        WITH user, friendships, likesOnPosts, likesOnComments, commentsOnPosts, COLLECT({acting_user_id: commenter.id, 
                                                                                         acting_user_username:commenter.username, 
                                                                                         acting_user_profile_img_url:commenter.profile_img_url,
                                                                                         post_id:content.id,
                                                                                         comment_id:comment.id,
                                                                                         reply_id:reply.id,
                                                                                         reply_text:reply.text,
                                                                                         book_small_img_urls:book_small_img_urls,
                                                                                         created_date: reply.created_date,  
                                                                                         activity: 'replied_to_comment'}) AS repliesToComments

        // OPTIONAL Match for pins for comments
        OPTIONAL MATCH (user)-[:COMMENTED]->(comment:Comment)<-[pin:PINNED]-(content)<-[:POSTED]-(pinner:User)
        OPTIONAL MATCH (content)-[:POST_FOR_BOOK]->(book:Book)
        WITH user, friendships, likesOnPosts, likesOnComments, commentsOnPosts, repliesToComments, content, COLLECT(book.small_img_url) AS book_small_img_urls, pinner, comment, pin
        WITH user, friendships, likesOnPosts, likesOnComments, commentsOnPosts, repliesToComments, COLLECT({acting_user_id: pinner.id, 
                                                                                                            acting_user_username:pinner.username, 
                                                                                                            acting_user_profile_img_url:pinner.profile_img_url,
                                                                                                            post_id:content.id,
                                                                                                            comment_id:comment.id,
                                                                                                            comment_text:comment.text,
                                                                                                            book_small_img_urls:book_small_img_urls,
                                                                                                            created_date: pin.created_date,  
                                                                                                            activity: 'pinned_comment'}) AS pinsForComments

        // Filtering out null values from each activity type
        WITH user, 
            [x IN friendships WHERE x.acting_user_id IS NOT NULL] AS filteredFriendships,
            [x IN likesOnPosts WHERE x.acting_user_id IS NOT NULL] AS filteredLikesOnPosts,
            [x IN likesOnComments WHERE x.acting_user_id IS NOT NULL] AS filteredLikesOnComments,
            [x IN commentsOnPosts WHERE x.acting_user_id IS NOT NULL] AS filteredCommentsOnPosts,
            [x IN repliesToComments WHERE x.acting_user_id IS NOT NULL] AS filteredRepliesToComments,
            [x IN pinsForComments WHERE x.acting_user_id IS NOT NULL] AS filteredPinsForComments

        // Merging and sorting the results
        WITH user, filteredFriendships + filteredLikesOnPosts + filteredLikesOnComments + filteredCommentsOnPosts + filteredRepliesToComments + filteredPinsForComments AS activities
        UNWIND activities AS activity
        RETURN activity
        ORDER BY activity.created_date DESC
        SKIP $skip
        LIMIT $limit
        """
        
        result = tx.run(query, user_id=user_id, skip=skip, limit=limit)

        activity_list = []
        for response in result:
            activity = response['activity']
            if activity['activity'] == 'friendship':
                friend_activity = FriendActivity(
                    acting_user_id=activity['acting_user_id'],
                    acting_user_profile_img_url=activity['acting_user_profile_img_url'],
                    acting_user_username=activity['acting_user_username'],
                    created_date=activity['created_date'],
                    activity_type='friendship'
                )
                # Added this since we need to know who the current user is.
                friend_activity.current_username = username
                activity_list.append(friend_activity)
            elif activity['activity'] == 'liked_post':
                activity_list.append(
                    LikedPostActivity(
                        acting_user_id=activity['acting_user_id'],
                        acting_user_profile_img_url=activity['acting_user_profile_img_url'],
                        acting_user_username=activity['acting_user_username'],
                        created_date=activity['created_date'],
                        activity_type='liked_post',
                        post_id=activity['post_id'],
                        book_small_img_urls=activity['book_small_img_urls']
                    )
                )
            elif activity['activity'] == 'liked_comment':
                activity_list.append(
                    LikedCommentActivity(
                        acting_user_id=activity['acting_user_id'],
                        acting_user_profile_img_url=activity['acting_user_profile_img_url'],
                        acting_user_username=activity['acting_user_username'],
                        created_date=activity['created_date'],
                        activity_type='liked_comment',
                        post_id=activity['post_id'],
                        book_small_img_urls=activity['book_small_img_urls'],
                        comment_id=activity['comment_id'],
                        comment_text=activity['comment_text']
                    )
                )
            elif activity['activity'] == 'commented_on_post':
                activity_list.append(
                    CommentedOnPostActivity(
                        acting_user_id=activity['acting_user_id'],
                        acting_user_profile_img_url=activity['acting_user_profile_img_url'],
                        acting_user_username=activity['acting_user_username'],
                        created_date=activity['created_date'],
                        activity_type='commented_on_post',
                        post_id=activity['post_id'],
                        book_small_img_urls=activity['book_small_img_urls'],
                        comment_id=activity['comment_id'],
                        comment_text=activity['comment_text']
                    )
                )
            elif activity['activity'] == 'replied_to_comment':
                activity_list.append(
                    RepliedToCommentActivity(
                        acting_user_id=activity['acting_user_id'],
                        acting_user_profile_img_url=activity['acting_user_profile_img_url'],
                        acting_user_username=activity['acting_user_username'],
                        created_date=activity['created_date'],
                        activity_type='replied_to_comment',
                        post_id=activity['post_id'],
                        book_small_img_urls=activity['book_small_img_urls'],
                        comment_id=activity['comment_id'],
                        reply_id=activity['reply_id'],
                        reply_text=activity['reply_text'],
                    )
                )
            elif activity['activity'] == 'pinned_comment':
                print(activity)
                activity_list.append(
                    PinnedCommentActivity(
                        acting_user_id=activity['acting_user_id'],
                        acting_user_profile_img_url=activity['acting_user_profile_img_url'],
                        acting_user_username=activity['acting_user_username'],
                        created_date=activity['created_date'],
                        activity_type='pinned_comment',
                        post_id=activity['post_id'],
                        book_small_img_urls=activity['book_small_img_urls'],
                        comment_id=activity['comment_id'],
                        comment_text=activity['comment_text']
                    )
                )
 
        return(activity_list)
    
    def get_suggested_friends(self,user_id:str,n:int):
        """
        Returns a list of n suggested friends for the user_id
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_suggested_friends_query, user_id=user_id, n=n)  
        return(result)
    
    @staticmethod
    def get_suggested_friends_query(tx, user_id, n):
        query = """
        MATCH (user:User {id: $user_id})
        WITH user
        MATCH (otherUser:User)
        WHERE NOT (user)-[:FRIENDED]-(otherUser)
        and not (user)-[:BLOCKED]-(otherUser) 
        AND user.id <> otherUser.id
        OPTIONAL MATCH (user)-[:FRIENDED {status:'friends'}]-(friend:User)-[:FRIENDED {status:'friends'}]-(otherUser)
        WITH otherUser, COUNT(friend) AS mutualFriends
        ORDER BY mutualFriends DESC, RAND()
        LIMIT $n
        RETURN otherUser.id, otherUser.username, otherUser.profile_img_url, mutualFriends
        """
        
        result = tx.run(query,user_id=user_id, n=n)
        suggested_friends = [
            SuggestedFriend(user_id=response['otherUser.id'],
                            user_username=response['otherUser.username'],
                            user_profile_img_url=response['otherUser.profile_img_url'],
                            n_mutual_friends=response['mutualFriends']) for response in result
        ]
        return(suggested_friends)

    def update_user_full_name(self, username: str, full_name: str) -> User:
        with self.driver.session() as session:
            response = session.execute_write(self.update_user_full_name_query, username=username, full_name=full_name)
        
        if response:
            return User(**response.data()['u'])
        else:
            return None
    
    @staticmethod
    def update_user_full_name_query(tx, username: str, full_name: str):
        query = """
                match (u:User {username:$username})
                set u.full_name = $full_name
                return u
                """
        
        result = tx.run(query, username=username, full_name=full_name)
        response = result.single()
        return response
    
    def update_user_liked_genre(self, username: str, genre_id: str) -> bool:
        with self.driver.session() as session:
            response = session.execute_write(self.update_user_liked_genre_query, username=username, genre_id=genre_id)
        
        return response
    
    @staticmethod
    def update_user_liked_genre_query(tx, username: str, genre_id: str):
        query = """
                match (u:User {username:$username})
                merge (g:Genre {id:$genre_id})
                merge (u)-[:LIKES]->(g)
                return g
                """
        
        result = tx.run(query, username=username, genre_id=genre_id)
        response = result.single()
        return response is not None
    
    def update_user_liked_author(self, username: str, author_id: str) -> bool:
        with self.driver.session() as session:
            response = session.execute_write(self.update_user_liked_author_query, username=username, author_id=author_id)
        
        return response
    
    @staticmethod
    def update_user_liked_author_query(tx, username: str, author_id: str):
        query = """
                match (u:User {username:$username})
                merge (a:Author {id:$author_id})
                merge (u)-[:LIKES]->(a)
                return a
                """
        
        result = tx.run(query, username=username, author_id=author_id)
        response = result.single()
        return response is not None
    
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
        return u
        """
        
        result = tx.run(query,user_id=user_id,new_bio=new_bio)
        response = result.single()
        return response is not None
    
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
        return u
        """
        
        result = tx.run(query,user_id=user_id,new_email=new_email)
        response = result.single()
        return response is not None
    
    def update_user_profile_image(self, user_id:str, profile_img_url:str):
        """
        Updates user profile img from uploadCare cdn link
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_user_profile_image_query, user_id=user_id, profile_img_url=profile_img_url)
        return(result)
    @staticmethod
    def update_user_profile_image_query(tx, user_id, profile_img_url):
        """
        More nerd shit on here
        """
        query = """
            match(u:User {id:$user_id})
            set u.profile_img_url = $profile_img_url
            return u.profile_img_url
        """
        result = tx.run(query, user_id=user_id, profile_img_url=profile_img_url)
        response = result.single()
        return response is not None
    
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
        return u
        """
        
        result = tx.run(query,user_id=user_id,new_password=new_password)
        response = result.single()
        return response is not None
    
    def update_friend_request_to_accepted(self,friend_request:FriendRequestCreate):
        """
        accepts a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_friend_request_to_accepted_query, friend_request=friend_request)  
        return(result)
    
    @staticmethod
    def update_friend_request_to_accepted_query(tx, friend_request):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        MATCH (fromUser)-[friend_request:FRIENDED {status:"pending"}]->(toUser)
        set friend_request.status = "friends"
        set friend_request.created_date = datetime()
        RETURN friend_request
        """
        
        result = tx.run(query,from_user_id=friend_request.from_user_id,to_user_id=friend_request.to_user_id)
        response = result.single()
        return response is not None
    
    def update_friend_request_to_declined(self,friend_request:FriendRequestCreate):
        """
        declines a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_friend_request_to_declined_query, friend_request=friend_request)  
        return(result)
    
    @staticmethod
    def update_friend_request_to_declined_query(tx, friend_request):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        MATCH (fromUser)-[friend_request:FRIENDED {status:"pending"}]->(toUser)
        set friend_request.status = "declined"
        RETURN toUser
        """
        
        result = tx.run(query,from_user_id=friend_request.from_user_id,to_user_id=friend_request.to_user_id)
        response = result.single()
        return response is not None

    def delete_user_by_username(self, username: str) -> bool:
        with self.driver.session() as session:
            response = session.execute_write(self.delete_user_by_username_query, username=username)
        
        return response
    
    @staticmethod
    def delete_user_by_username_query(tx, username: str):
        query = """
                match (u:User {username:$username})
                detach delete u
                """
        
        result = tx.run(query, username=username)
        response = result.single()
        return response is not None
    
    def delete_friend_request(self,friend_request:FriendRequestCreate):
        """
        deletes a friend request from a user to another user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_friend_request_query, friend_request=friend_request)  
        return(result)
    
    @staticmethod
    def delete_friend_request_query(tx, friend_request):
        query = """
        match (fromUser:User {id:$from_user_id, disabled:False})
        match (toUser:User {id:$to_user_id, disabled:False})
        MATCH (fromUser)-[friend_request:FRIENDED {status:"pending"}]->(toUser)
        DELETE friend_request
        RETURN toUser
        """
        
        result = tx.run(query,from_user_id=friend_request.from_user_id,to_user_id=friend_request.to_user_id)
        response = result.single()
        return response is not None
    
    def delete_friend_relationship(self,friend_delete:FriendDelete):
        """
        remove a friend relationship
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_friend_relationship_query, friend_delete=friend_delete)  
        return(result)
    
    @staticmethod
    def delete_friend_relationship_query(tx, friend_delete):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        MATCH (fromUser)-[friendRelationship:FRIENDED {status:"friends"}]-(toUser)
        delete friendRelationship
        RETURN toUser
        """
        
        result = tx.run(query,from_user_id=friend_delete.from_user_id,to_user_id=friend_delete.to_user_id)
        response = result.single()
        return response is not None
    
    def delete_follow_relationship(self,unfollow_user:FollowUserCreate):
        """
        unfollows a user if the to_user has a critic account
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_follow_relationship_query, unfollow_user=unfollow_user)  
        return(result)
    
    @staticmethod
    def delete_follow_relationship_query(tx, unfollow_user):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id, user_type:"critic"})
        match (fromUser)-[followRel:FOLLOWS]->(toUser)
        delete followRel
        RETURN Case when toUser is not null then true else false end as foundRelationship
        """
        
        result = tx.run(query,from_user_id=unfollow_user.from_user_id,to_user_id=unfollow_user.to_user_id)
        response = result.single()
        return response is not None
    
    def delete_blocked_relationship(self,unblock_user:BlockUserCreate):
        """
        unblocks a user
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_blocked_relationship_query, unblock_user=unblock_user)  
        return(result)
    
    @staticmethod
    def delete_blocked_relationship_query(tx, unblock_user):
        query = """
        match (fromUser:User {id:$from_user_id})
        match (toUser:User {id:$to_user_id})
        match (fromUser)-[blockRel:BLOCKED]->(toUser)
        delete blockRel
        RETURN Case when toUser is not null then true else false end as foundRelationship
        """
        
        result = tx.run(query,from_user_id=unblock_user.from_user_id,to_user_id=unblock_user.to_user_id)
        response = result.single()
        return response is not None
    
