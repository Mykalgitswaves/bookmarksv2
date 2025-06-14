from typing import Dict
from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.comments import (
    Comment, 
    CommentCreate, 
    LikedComment, 
    PinnedComment, 
    build_comment_thread,
)
from src.database.graph.utils.comments import (
    build_get_comments_query,
    build_get_comments_for_comment_query, 
    build_comment_object
)


class CommentCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def get_all_comments_for_post(
            self, 
            post_id, 
            user_id, 
            skip, 
            limit,
            depth
        ):
        """
        Gets all the comments on the post. For comments with replies, it returns
        the top liked reply at each depth, up to the specified depth

        Args:
            post_id: PK of the post for which to return comments    
            user_id: id of the current user
            skip: Low index of comments to grab
            limit: high index of comments to grab 
            depth: The maximum depth for threads
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_all_comments_for_post_query, 
                post_id, 
                user_id, 
                skip, 
                limit,
                depth
                )  
        return(result)

    @staticmethod
    def get_all_comments_for_post_query(
        tx, 
        post_id, 
        user_id, 
        skip,
        limit, 
        depth
        ):
        query = build_get_comments_query(
            depth, 
            book_club_posts=False
            )

        result = tx.run(
            query, 
            user_id=user_id, 
            post_id=post_id, 
            skip=skip, 
            limit=limit
        )

        comments = []
        for response in result:
            comment_data = response['parentWithChain']
            comment_author = comment_data['parentAuthor']
            parent_comment_data = comment_data['parentComment']
            comment = build_comment_object(
                parent_comment_data,
                comment_author,
                comment_data['parentLikedByUser'],
                post_id,
                user_id
            )
            prev_comment_id = comment.id
            thread = []
            for thread_comment in comment_data['chainedReplies']:
                if not thread_comment['node']:
                    break

                thread_comment_data = thread_comment['node']
                thread_comment_author = thread_comment['author']
                thread_comment_object = build_comment_object(
                    thread_comment_data,
                    thread_comment_author,
                    thread_comment['likedByUser'],
                    post_id,
                    user_id,
                    prev_comment_id
                )
                thread.append(thread_comment_object)
                prev_comment_id = thread_comment_object.id
            
            comment.thread = thread
            comments.append(comment)

        pinned_query = build_get_comments_query(
            depth,
            pinned=True
        )

        pinned_result = tx.run(
            pinned_query, 
            user_id=user_id, 
            post_id=post_id, 
            skip=skip, 
            limit=limit
        )

        pinned_comments = []
        prev_comment_id = None
        for response in pinned_result:
            comment_data = response['parentWithChain']
            comment_author = comment_data['parentAuthor']
            parent_comment_data = comment_data['parentComment']
            comment = build_comment_object(
                parent_comment_data,
                comment_author,
                comment_data['parentLikedByUser'],
                post_id,
                user_id
            )
            prev_comment_id = comment.id
            thread = []
            for thread_comment in comment_data['chainedReplies']:
                if not thread_comment['node']:
                    break

                thread_comment_data = thread_comment['node']
                thread_comment_author = thread_comment['author']
                thread_comment_object = build_comment_object(
                    thread_comment_data,
                    thread_comment_author,
                    thread_comment['likedByUser'],
                    post_id,
                    user_id,
                    prev_comment_id
                )
                thread.append(thread_comment_object)
                prev_comment_id = thread_comment_object.id
            
            comment.thread = thread
            pinned_comments.append(comment)

        return({"comments":comments, "pinned_comments": pinned_comments})

    def get_all_comments_for_comment(
            self, 
            post_id,
            comment_id, 
            user_id, 
            skip, 
            limit,
            depth
        ):
        """
        Gets all the comments on the post. For comments with replies, it returns
        the top liked reply at each depth, up to the specified depth

        Args:
            post_id: PK of the post for which to return comments    
            comment_id: The ID of the comment to grab replies to
            user_id: id of the current user
            skip: Low index of comments to grab
            limit: high index of comments to grab 
            depth: The maximum depth for threads
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_all_comments_for_comment_query, 
                post_id, 
                comment_id, 
                user_id,
                skip, 
                limit,
                depth
                )  
        return(result)

    @staticmethod
    def get_all_comments_for_comment_query(
        tx, 
        post_id,
        comment_id, 
        user_id, 
        skip,
        limit, 
        depth
        ):
        query = build_get_comments_for_comment_query(
            depth, 
            book_club_posts=False
            )

        result = tx.run(
            query, 
            user_id=user_id, 
            post_id=post_id,
            comment_id=comment_id, 
            skip=skip, 
            limit=limit
        )

        comments = []
        for response in result:
            comment_data = response['parentWithChain']
            comment_author = comment_data['parentAuthor']
            parent_comment_data = comment_data['parentComment']
            comment = build_comment_object(
                parent_comment_data,
                comment_author,
                comment_data['parentLikedByUser'],
                post_id,
                user_id,
                comment_id
            )
            prev_comment_id = comment.id
            thread = []
            for thread_comment in comment_data['chainedReplies']:
                if not thread_comment['node']:
                    break

                thread_comment_data = thread_comment['node']
                thread_comment_author = thread_comment['author']
                thread_comment_object = build_comment_object(
                    thread_comment_data,
                    thread_comment_author,
                    thread_comment['likedByUser'],
                    post_id,
                    user_id,
                    prev_comment_id
                )
                thread.append(thread_comment_object)
                prev_comment_id = thread_comment_object.id
            
            comment.thread = thread
            comments.append(comment)
        
        return comments

    def get_paginated_comments_for_book_club_post(
            self, 
            post_id, 
            user_id, 
            book_club_id,
            skip, 
            limit, 
            depth
    ):
        """
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_paginated_comments_for_book_club_post_query, 
                post_id=post_id, 
                user_id=user_id,
                book_club_id=book_club_id, 
                skip=skip, 
                limit=limit,
                depth=depth
            )  
        return(result)
    
    @staticmethod
    def get_paginated_comments_for_book_club_post_query(
        tx, 
        post_id,
        user_id, 
        book_club_id,
        depth,
        skip=0, 
        limit=20
        ):
        
        query = build_get_comments_query(depth, book_club_posts=True)
        
        result = tx.run(
            query, 
            user_id=user_id, 
            post_id=post_id, 
            book_club_id=book_club_id,
            skip=skip, 
            limit=limit
        )

        comments = []
        for response in result:
            comment_data = response['parentWithChain']
            comment_author = comment_data['parentAuthor']
            parent_comment_data = comment_data['parentComment']
            comment = build_comment_object(
                parent_comment_data,
                comment_author,
                comment_data['parentLikedByUser'],
                post_id,
                user_id
            )
            prev_comment_id = comment.id
            thread = []
            for thread_comment in comment_data['chainedReplies']:
                if not thread_comment['node']:
                    break

                thread_comment_data = thread_comment['node']
                thread_comment_author = thread_comment['author']
                thread_comment_object = build_comment_object(
                    thread_comment_data,
                    thread_comment_author,
                    thread_comment['likedByUser'],
                    post_id,
                    user_id,
                    prev_comment_id
                )
                thread.append(thread_comment_object)
                prev_comment_id = thread_comment_object.id
            
            comment.thread = thread
            comments.append(comment)

        pinned_query = build_get_comments_query(
            depth, 
            book_club_posts=True,
            pinned=True
        )
        
        result = tx.run(
            pinned_query, 
            user_id=user_id, 
            post_id=post_id, 
            book_club_id=book_club_id,
            skip=skip, 
            limit=limit
        )
        
        pinned_comments = []
        prev_comment_id = None
        for response in result:
            comment_data = response['parentWithChain']
            comment_author = comment_data['parentAuthor']
            parent_comment_data = comment_data['parentComment']
            comment = build_comment_object(
                parent_comment_data,
                comment_author,
                comment_data['parentLikedByUser'],
                post_id,
                user_id,
            )
            prev_comment_id = comment.id
            thread = []
            for thread_comment in comment_data['chainedReplies']:
                if not thread_comment['node']:
                    break

                thread_comment_data = thread_comment['node']
                thread_comment_author = thread_comment['author']
                thread_comment_object = build_comment_object(
                    thread_comment_data,
                    thread_comment_author,
                    thread_comment['likedByUser'],
                    post_id,
                    user_id,
                    prev_comment_id
                )
                thread.append(thread_comment_object)
                prev_comment_id = thread_comment_object.id
            
            comment.thread = thread or []
            pinned_comments.append(comment)

        return({"comments":comments, "pinned_comments": pinned_comments})
    
    def get_parent_comment(
            self,
            comment_id: str,
            user_id: str,
            post_id: str,
    ):
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_parent_comment_query,  
                comment_id, 
                user_id,
                post_id,
            )  
        return(result)

    @staticmethod
    def get_parent_comment_query(
            tx,
            comment_id,
            user_id,
            post_id,
    ):
        query = """
            match (user:User {id: $user_id})
            match (postingUser:User)-[:COMMENTED]->(comment:Comment {id: $comment_id})
            optional match (user)-[likedByCurrentUser:LIKES]->(comment)
            optional match (comment)-[:REPLIED_TO]->(repliedToComment:Comment)
            return comment, 
                postingUser, 
                repliedToComment.id as repliedToCommentId,
                CASE WHEN likedByCurrentUser IS NOT NULL THEN true ELSE false END AS islikedByCurrentUser
        """

        result = tx.run(
            query, 
            user_id=user_id,  
            comment_id=comment_id)
        
        data = result.single()
        
        comment_data = data.get('comment')
        comment_author = data.get('postingUser')

        comment = Comment(
            id=comment_id,
            created_date=comment_data['created_date'],
            liked_by_current_user=data.get('islikedByCurrentUser'),
            post_id=post_id,
            user_id=comment_author['id'],
            username=comment_author['username'],
            text=comment_data.get("text",""),
            replied_to=data.get('repliedToCommentId'),
            posted_by_current_user=comment_author['id'] == user_id,
            likes=comment_data.get('likes',0),
            num_replies=comment_data.get('num_replies',0)
        )

        return comment
    
    def get_parent_comment_for_book_club(
            self,
            comment_id: str,
            user_id: str,
            book_club_id: str,
            post_id: str,
    ):
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_parent_comment_for_book_club_query,  
                comment_id, 
                user_id,
                book_club_id,
                post_id,
            )  
        return(result)

    @staticmethod
    def get_parent_comment_for_book_club_query(
            tx,
            comment_id,
            user_id,
            book_club_id,
            post_id,
    ):
        """
        
        """
        query = """
            match (user:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            match (postingUser:User)-[:COMMENTED]->(comment:Comment {id: $comment_id})
            optional match (user)-[likedByCurrentUser:LIKES]->(comment)
            optional match (comment)-[:REPLIED_TO]->(repliedToComment:Comment)
            return comment, 
                postingUser, 
                repliedToComment.id as repliedToCommentId,
                CASE WHEN likedByCurrentUser IS NOT NULL THEN true ELSE false END AS islikedByCurrentUser
        """

        result = tx.run(query, user_id=user_id, book_club_id=book_club_id, comment_id=comment_id)
        
        data = result.single()
        
        comment_data = data.get('comment')
        comment_author = data.get('postingUser')

        comment = Comment(
            id=comment_id,
            created_date=comment_data['created_date'],
            liked_by_current_user=data.get('islikedByCurrentUser'),
            post_id=post_id,
            user_id=comment_author['id'],
            username=comment_author['username'],
            text=comment_data.get("text",""),
            replied_to=data.get('repliedToCommentId'),
            posted_by_current_user=comment_author['id'] == user_id,
            likes=comment_data.get('likes',0),
            num_replies=comment_data.get('num_replies',0)
        )

        return comment

    def get_paginated_comments_for_book_club_comment(
            self, 
            post_id,
            comment_id, 
            user_id, 
            skip, 
            limit,
            book_club_id,
            depth
        ):
        """
        Gets all the comments on the comment for a bookclub. 
        For comments with replies, it returns
        the top liked reply at each depth, up to the specified depth

        Args:
            post_id: PK of the post for which to return comments    
            comment_id: The ID of the comment to grab replies to
            user_id: id of the current user
            skip: Low index of comments to grab
            limit: high index of comments to grab 
            book_club_id: ID of the bookclub
            depth: The maximum depth for threads
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_paginated_comments_for_book_club_comment_query, 
                post_id, 
                comment_id, 
                user_id,
                skip, 
                limit,
                book_club_id,
                depth
                )  
        return(result)

    @staticmethod
    def get_paginated_comments_for_book_club_comment_query(
        tx, 
        post_id,
        comment_id, 
        user_id, 
        skip,
        limit,
        book_club_id, 
        depth
        ):
        query = build_get_comments_for_comment_query(
            depth, 
            book_club_posts=True
            )

        result = tx.run(
            query, 
            user_id=user_id, 
            post_id=post_id,
            comment_id=comment_id,
            book_club_id=book_club_id, 
            skip=skip, 
            limit=limit
        )

        comments = []
        for response in result:
            comment_data = response['parentWithChain']
            comment_author = comment_data['parentAuthor']
            parent_comment_data = comment_data['parentComment']
            comment = build_comment_object(
                parent_comment_data,
                comment_author,
                comment_data['parentLikedByUser'],
                post_id,
                user_id,
                comment_id
            )
            prev_comment_id = comment.id
            thread = []
            for thread_comment in comment_data['chainedReplies']:
                if not thread_comment['node']:
                    break

                thread_comment_data = thread_comment['node']
                thread_comment_author = thread_comment['author']
                thread_comment_object = build_comment_object(
                    thread_comment_data,
                    thread_comment_author,
                    thread_comment['likedByUser'],
                    post_id,
                    user_id,
                    prev_comment_id
                )
                thread.append(thread_comment_object)
                prev_comment_id = thread_comment_object.id
            
            comment.thread = thread
            comments.append(comment)
        
        return comments
    
    def get_all_parent_comments_for_comment(
            self, 
            post_id,
            comment_id, 
            user_id
        ):
        """
        Gets all the parent comments for a comment in a bookclub

        Args:
            post_id: PK of the post for which to return comments    
            comment_id: The ID of the comment to grab replies to
            user_id: id of the current user
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self. get_all_parent_comments_for_comment_query, 
                post_id, 
                comment_id, 
                user_id
                )  
        return(result)

    @staticmethod
    def  get_all_parent_comments_for_comment_query(
        tx, 
        post_id,
        comment_id, 
        user_id
        ):

        query = """
            Match (user:User {id: $user_id})
            MATCH (lowestComment:Comment {id: $comment_id})
            // Traverse zero or more REPLIED_TO steps from this comment up the chain
            // until you get to a top-level comment (one with is_reply = false):
            OPTIONAL MATCH path = (lowestComment)-[:REPLIED_TO*0..]->(topComment:Comment)
            WHERE topComment.is_reply = false
            OR NOT (topComment)-[:REPLIED_TO]->(:Comment)

            // path now includes every comment along the chain from lowestComment up to the top-level comment
            // UNWIND the path to retrieve each comment node in that chain:
            UNWIND nodes(path)[1..] AS commentInChain

            // (Optional) You can now match users, likes, etc. for each commentInChain:
            OPTIONAL MATCH (commentInChain)<-[likeRel:LIKES]-(user)
            OPTIONAL MATCH (commentInChain)<-[:COMMENTED]-(postingUser:User)

            // Return the comment node and any other info you need:
            RETURN DISTINCT 
                commentInChain AS comment, 
                postingUser,
                CASE WHEN likeRel IS NOT NULL THEN true ELSE false END AS isLikedByCurrentUser
            ORDER BY commentInChain.depth ASC
        """

        result = tx.run(
            query, 
            user_id=user_id,
            comment_id=comment_id
        )

        comments = []
        for response in result:
            comment_data = response['comment']
            comment_author = response['postingUser']
            comment = build_comment_object(
                comment_data,
                comment_author,
                response['isLikedByCurrentUser'],
                post_id,
                user_id
            )
        
            comments.append(comment)
        
        return comments
    
    def get_all_parent_comments_for_book_club_comment(
            self, 
            post_id,
            comment_id, 
            user_id,
            book_club_id
        ):
        """
        Gets all the parent comments for a comment in a bookclub

        Args:
            post_id: PK of the post for which to return comments    
            comment_id: The ID of the comment to grab replies to
            user_id: id of the current user
            book_club_id: ID of the bookclub
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self. get_all_parent_comments_for_book_club_comment_query, 
                post_id, 
                comment_id, 
                user_id,
                book_club_id
                )  
        return(result)

    @staticmethod
    def  get_all_parent_comments_for_book_club_comment_query(
        tx, 
        post_id,
        comment_id, 
        user_id,
        book_club_id,
        ):

        query = """
            Match (user:User {id: $user_id})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(b:BookClub {id: $book_club_id})
            MATCH (lowestComment:Comment {id: $comment_id})
            // Traverse zero or more REPLIED_TO steps from this comment up the chain
            // until you get to a top-level comment (one with is_reply = false):
            OPTIONAL MATCH path = (lowestComment)-[:REPLIED_TO*0..]->(topComment:Comment)
            WHERE topComment.is_reply = false
            OR NOT (topComment)-[:REPLIED_TO]->(:Comment)

            // path now includes every comment along the chain from lowestComment up to the top-level comment
            // UNWIND the path to retrieve each comment node in that chain:
            UNWIND nodes(path)[1..] AS commentInChain

            // (Optional) You can now match users, likes, etc. for each commentInChain:
            OPTIONAL MATCH (commentInChain)<-[likeRel:LIKES]-(user)
            OPTIONAL MATCH (commentInChain)<-[:COMMENTED]-(postingUser:User)

            // Return the comment node and any other info you need:
            RETURN DISTINCT 
                commentInChain AS comment, 
                postingUser,
                CASE WHEN likeRel IS NOT NULL THEN true ELSE false END AS isLikedByCurrentUser
            ORDER BY commentInChain.depth ASC
        """

        result = tx.run(
            query, 
            user_id=user_id,
            book_club_id=book_club_id,
            comment_id=comment_id
        )

        comments = []
        for response in result:
            comment_data = response['comment']
            comment_author = response['postingUser']
            comment = build_comment_object(
                comment_data,
                comment_author,
                response['isLikedByCurrentUser'],
                post_id,
                user_id
            )
        
            comments.append(comment)
        
        return comments

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
            comment = Comment(id=response['c']['id'],
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
                reply = Comment(id=response['top_liked_reply']['id'],
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
                id=response['cr']['id'],
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
    
    def create_comment(self, comment:CommentCreate):
        """
        Creates a comment in the database
        Args:
            comment: Comment object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            comment_id: PK of the comment in the db
        """
        with self.driver.session() as session:
            comment_result = session.execute_write(self.create_comment_query, comment)
        return(comment_result)
    
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
            pinned:false,
            deleted:false,
            depth:parent.depth + 1,
            num_replies:0
        })
        merge (pp)-[h:HAS_COMMENT]->(c)
        merge (u)-[cc:COMMENTED]->(c)
        MERGE (c)-[:REPLIED_TO]->(parent)
        SET parent.num_replies = parent.num_replies + 1

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
            pinned:false,
            deleted:false,
            depth:0,
            num_replies:0
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
            comment_result = Comment(
                post_id = comment.post_id,
                replied_to = comment.replied_to,
                text = comment.text,
                username = comment.username,
                id = response['c.id'],
                created_date = response['c.created_date']
            )
            return(comment_result)
        else:
            return None
        
    def create_comment_for_club(self, comment:CommentCreate):
        """
        Creates a comment in the database for a book club post
        Args:
            comment: Comment object to be pushed to DB
        Returns:
            created_date: Exact datetime of creation from Neo4j
            comment_id: PK of the comment in the db
        """
        with self.driver.session() as session:
            comment_result = session.execute_write(self.create_comment_for_club_query, comment)
        return(comment_result)
    
    @staticmethod
    def create_comment_for_club_query(tx, comment):
        print("creating comment for club")
        query_w_reply = """
        match (pp {id:$post_id, deleted:false})-[:POST_FOR_CLUB_BOOK]->(:BookClubBook)-[]-(club:BookClub)
        match (u:User {username:$username})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club)
        MATCH (parent:Comment {id: $replied_to, deleted:false})
        create (c:Comment {
            id:randomUUID(),
            created_date:datetime(),
            text:$text,
            likes:0,
            is_reply:True,
            pinned:false,
            deleted:false,
            depth:parent.depth + 1,
            num_replies:0
        })
        merge (pp)-[h:HAS_COMMENT]->(c)
        merge (u)-[cc:COMMENTED]->(c)
        MERGE (c)-[:REPLIED_TO]->(parent)
        SET parent.num_replies = parent.num_replies + 1

        return c.id, c.created_date
        """
        query_no_reply = """
        match (pp {id:$post_id, deleted:false})-[:POST_FOR_CLUB_BOOK]->(:BookClubBook)-[]-(club:BookClub)
        match (u:User {username:$username})-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club)
        create (c:Comment {
            id:randomUUID(),
            created_date:datetime(),
            text:$text,
            likes:0,
            is_reply:False,
            pinned:false,
            deleted:false,
            depth:0,
            num_replies:0
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
        
        response = result.single()
        if response:
            print(response)
            comment_result = Comment(
                post_id = comment.post_id,
                replied_to = comment.replied_to,
                text = comment.text,
                username = comment.username,
                id = response['c.id'],
                created_date = response['c.created_date']
            )
            return(comment_result)
        else:
            return None
        
    def create_comment_like(self, liked_comment: LikedComment):
        """
        Adds a liked comment for a user
        
        Args:
            username: users PK
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_comment_like_query, liked_comment)
        return result
        
    @staticmethod
    def create_comment_like_query(tx, liked_comment):
        query = """
                match (uu:User {username: $username}) 
                match (rr:Comment {id: $comment_id})
                with uu, rr
                where not exists ((uu)-[:LIKES]-(rr))
                    create (uu)-[ll:LIKES {created_date:datetime()}]->(rr)
                    set rr.likes = rr.likes + 1
                return rr.likes
                """
        result = tx.run(query, username=liked_comment.username, comment_id=liked_comment.comment_id)
        response = result.single()
        return response is not None
    
    def create_comment_pin(self, user_id: str, pinned_comment: PinnedComment):
        """
        Adds a pinned comment for a post
        
        Args:
            comment_id: comment's PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_comment_pin_query, user_id, pinned_comment)
        return result
        
    @staticmethod
    def create_comment_pin_query(tx, user_id, pinned_comment):
        query = """
                match (u:User {id: $user_id})-[postRel:POSTED]->(pp {id: $post_id}) 
                match (pp)-[hc:HAS_COMMENT]->(rr:Comment {id: $comment_id, is_reply: False})
                with pp,rr
                merge (pp)-[pinned:PINNED]->(rr)
                on create set
                    pinned.created_date = datetime(),
                    rr.pinned = True
                return rr
                """
        result = tx.run(query, 
                    comment_id=pinned_comment.comment_id, 
                    post_id=pinned_comment.post_id,
                    user_id=user_id,
                )
        
        response = result.single()
        return response is not None
        
    def update_comment_to_deleted(self,comment_id, username):
        """
        Set deleted flag of a comment to True
        
        Args:
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_comment_to_deleted_query, comment_id, username) 
        return result

    @staticmethod
    def update_comment_to_deleted_query(tx, comment_id, username):
        query = """
                match (u:User {username: $username})-[commentRel:COMMENTED]->(comment {id: $comment_id})
                optional match (commentReply:Comment)-[replyRel:REPLIED_TO]->(comment)
                set comment.deleted=true
                set commentReply.deleted=true
                return comment.id
                """
        result = tx.run(query, comment_id=comment_id, username=username)
        response = result.single()
        return response is not None

    def delete_comment(self,comment_id):
        """
        Deletes a comment from the database
        
        Args:
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_comment_query, comment_id) 
               
    @staticmethod
    def delete_comment_query(tx, comment_id):
        query = """
                match (comment {id: $comment_id})
                optional match (commentReply:Comment)-[replyRel:REPLIED_TO]->(comment)
                detach delete comment
                detach delete commentReply
                """
        result = tx.run(query, comment_id=comment_id)

    def delete_comment_like(self, liked_comment: LikedComment):
        """
        removes a liked comment for a user
        
        Args:
            username: users PK
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_comment_like_query, liked_comment)    
        return result
    
    @staticmethod
    def delete_comment_like_query(tx, liked_comment):
        query = """
                match (uu:User {username: $username}) 
                match (rr:Comment {id: $comment_id}) 
                match (uu)-[ll:LIKES]->(rr)
                delete ll
                WITH rr
                WHERE rr.likes > 0
                SET rr.likes = rr.likes - 1
                return rr.likes
                """
        result = tx.run(query, username=liked_comment.username, comment_id=liked_comment.comment_id)
        response = result.single()
        return response is not None
    
    def delete_comment_pin(self, pinned_comment: PinnedComment):
        """
        removes a pinned comment for a post
        
        Args:
            comment_id: comment's PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.delete_comment_pin_query, pinned_comment)
        return result
            
    @staticmethod
    def delete_comment_pin_query(tx, pinned_comment):
        query = """
                match (u:User {username:$username})-[postRel:POSTED]->(pp {id: $post_id})
                match (rr:Comment {id: $comment_id}) 
                match (pp)-[ll:PINNED]->(rr)
                delete ll
                set rr.pinned = False
                return rr
                """
        result = tx.run(query, 
                        comment_id=pinned_comment.comment_id, 
                        post_id=pinned_comment.post_id,
                        username=pinned_comment.username)
        response = result.single()
        return response is not None
