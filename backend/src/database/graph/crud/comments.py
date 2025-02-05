from typing import Dict
from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.comments import (
    Comment, 
    CommentCreate, 
    LikedComment, 
    PinnedComment, 
    build_comment_thread,
)
from src.database.graph.utils.comments import build_get_comments_query, build_comment_object


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
        query = build_get_comments_query(depth, book_club_posts=False)

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

        return({"comments":comments, "pinned_comments":{}})

    @staticmethod
    def get_all_comments_for_post_query_v2(tx, post_id, username, bookclub_id, skip=0, limit=20):
        query = """
            MATCH (rr:ClubUpdate {id: $post_id, deleted: false}) 
            MATCH (rr)-[r:HAS_COMMENT]->(parent_comment:Comment {is_reply: false, deleted: false})
            WITH parent_comment

            // Get the top-level comment and its details
            CALL {
                WITH parent_comment
                MATCH (commenter:User)-[:COMMENTED]->(parent_comment)
                OPTIONAL MATCH (username:User {username: $username})-[likedParent:LIKES]->(parent_comment)
                RETURN commenter, 
                    CASE WHEN likedParent IS NOT NULL THEN true ELSE false END AS parent_liked_by_user,
                    CASE WHEN commenter.username = $username THEN true ELSE false END AS posted_by_current_user
            }

            // First collect ALL comments and their user info into a map
            WITH parent_comment, commenter, parent_liked_by_user, posted_by_current_user
            CALL {
                WITH parent_comment
                MATCH (reply:Comment)-[:REPLIED_TO*0..4]->(parent_comment)
                MATCH (reply_commenter:User)-[:COMMENTED]->(reply)
                OPTIONAL MATCH (username:User {username: $username})-[liked:LIKES]->(reply)
                RETURN collect({
                    id: reply.id,
                    commenter: reply_commenter.username,
                    commenter_id: reply_commenter.id,
                    liked: CASE WHEN liked IS NOT NULL THEN true ELSE false END,
                    posted_by_current_user: CASE WHEN reply_commenter.username = $username THEN true ELSE false END
                }) as user_info_map
            }

            // Now get the paths for tree structure
            MATCH path = (reply:Comment {deleted: false})-[:REPLIED_TO*0..4]->(parent_comment)
            WITH parent_comment, commenter, parent_liked_by_user, posted_by_current_user,
                 user_info_map, COLLECT(path) as paths

            // Convert to tree and enrich with user info
            CALL apoc.convert.toTree(paths) YIELD value as reply_tree
            WITH {
                comment: parent_comment,
                commenter: commenter.username,
                commenter_id: commenter.id,
                liked: parent_liked_by_user,
                created_date: parent_comment.created_date,
                posted_by_current_user: posted_by_current_user,
                replies: CASE 
                    WHEN reply_tree IS NOT NULL AND reply_tree.replied_to IS NOT NULL
                    THEN reply_tree {
                        .*,
                        replied_to: [reply IN reply_tree.replied_to WHERE reply IS NOT NULL | 
                            reply {
                                .*,
                                commenter: ([ u IN user_info_map WHERE u.id = reply.id ][0]).commenter,
                                commenter_id: ([ u IN user_info_map WHERE u.id = reply.id ][0]).commenter_id,
                                liked_by_current_user: ([ u IN user_info_map WHERE u.id = reply.id ][0]).liked,
                                posted_by_current_user: ([ u IN user_info_map WHERE u.id = reply.id ][0]).posted_by_current_user,
                                replied_to: COALESCE(reply.replied_to, [])
                            }
                        ]
                    }
                    ELSE null
                END
            } AS comment_thread
            ORDER BY comment_thread.created_date DESC
            SKIP $skip
            LIMIT $limit
            RETURN comment_thread
        """

        result = tx.run(query, username=username, post_id=post_id, skip=skip, limit=limit)
        # result = [record for record in result.data()]
        # comment_response = {}
        comment_threads = []

        for record in result:
            # top_level_comment = record["comment_thread"].get("comment")
            # tlc_id = top_level_comment.get('id')

            # if tlc_id not in comment_response:
            #     comment_response[top_level_comment.get('id')] = {}

            # comment_response[tlc_id].comment = Comment(
            #     id=tlc_id,
            #     post_id=post_id,
            #     text=top_level_comment.get('text'),
            #     username=record['comment_thread'].get('commenter'),
            #     user_id=top_level_comment.get('id'),
            #     created_date=top_level_comment.get("created_date"),
            #     likes=top_level_comment.get('likes'),
            #     pinned=top_level_comment.get('pinned'),
            #     liked_by_current_user=record['comment_thread'].get('liked'),
            #     posted_by_current_user=record['comment_thread'].get('posted_by_current_user'),
            # )
            
            # if not comment_response[tlc_id].replies:
            #     comment_response[top_level_comment.get('id')].replies = {}
            
            # if record['comment_thread'].get('replies'):
            #     # recursively look into list of replies here.
            #     comment_response[tlc_id]
            thread = build_comment_thread(record=record, post_id=post_id)
            if thread:
                comment_threads.append(thread)
        return(comment_threads)

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

        return(comments)

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
    
    def create_comment_pin(self, pinned_comment: PinnedComment):
        """
        Adds a pinned comment for a post
        
        Args:
            comment_id: comment's PK
            post_id: post's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.create_comment_pin_query, pinned_comment)
        return result
        
    @staticmethod
    def create_comment_pin_query(tx, pinned_comment):
        query = """
                match (u:User {username:$username})-[postRel:POSTED]->(pp {id: $post_id}) 
                match (rr:Comment {id: $comment_id})
                with pp,rr
                where not exists ((pp)-[:PINNED]->(rr)) 
                    create (pp)-[ll:PINNED {created_date:datetime()}]->(rr)
                    set rr.pinned = True
                    return rr
                """
        result = tx.run(query, 
                        comment_id=pinned_comment.comment_id, 
                        post_id=pinned_comment.post_id,
                        username=pinned_comment.username)
        
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
