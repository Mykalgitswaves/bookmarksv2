from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.comments import Comment, CommentCreate

class CommentCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
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
                comment = Comment(id=response['c']['id'],
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
                    reply = Comment(id=response['top_liked_reply']['id'],
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
                comment = Comment(id=response['c']['id'],
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
                    reply = Comment(id=response['top_liked_reply']['id'],
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
            pinned:false,
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