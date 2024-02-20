from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.comments import Comment, CommentCreate

class CommentCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
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
        
    def update_comment_to_deleted(self,comment_id):
        """
        Set deleted flag of a comment to True
        
        Args:
            comment_id: comment's PK
        Returns:
            None
        """
        with self.driver.session() as session:
            result = session.execute_write(self.update_comment_to_deleted_query, comment_id) 
               
    @staticmethod
    def update_comment_to_deleted_query(tx, comment_id):
        query = """
                match (comment {id: $comment_id})
                optional match (commentReply:Comment)-[replyRel:REPLIED_TO]->(comment)
                set comment.deleted=true
                set commentReply.deleted=true
                """
        result = tx.run(query, comment_id=comment_id)