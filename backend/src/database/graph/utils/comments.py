from typing import Optional

from src.models.schemas.comments import Comment

def build_get_comments_query(
        depth: int,
        book_club_posts: bool = False,
        pinned: bool = False
    ) -> str:
    """
    Builds the comments query for threds to a certain depth

    Args:
        depth: The maximum depth to make comments until
        book_club_posts: Whether the post is from a book club
        pinned: Whether or not to only grab pinned comments

    Returns:
        query (str): The query to run with comments
    """

    if not book_club_posts:
        if not pinned:
            # SEE WHERE NOT STATEMENT
            query_start = """
                    MATCH (cu:User {id: $user_id, disabled: false})
                    MATCH (post {id: $post_id, deleted: false})
                    WHERE post:Review OR post:Milestone 
                        OR post:Update OR post:Comparison

                    // 1) Match the top-level "parent" comments on the post
                    MATCH (post)-[:HAS_COMMENT]->(c0:Comment {is_reply:false, deleted:false})
                    WHERE NOT (c0)<-[:PINNED]-(post)

                    // (Optional) Grab the parents author and whether current user liked the parent
                    MATCH (parentAuthor:User)-[:COMMENTED]->(c0)
                    OPTIONAL MATCH (cu)-[parentLike:LIKES]->(c0)

                    // Order the parents as needed
                    WITH cu, c0, parentAuthor, (parentLike IS NOT NULL) AS parentLikedByUser
                    ORDER BY c0.likes DESC, c0.created_date DESC
                    SKIP $skip
                    LIMIT $limit
                """
        else:
            query_start = """
                    MATCH (cu:User {id: $user_id, disabled: false})
                    MATCH (post {id: $post_id, deleted: false})
                    WHERE post:Review OR post:Milestone 
                        OR post:Update OR post:Comparison

                    // 1) Match the top-level "parent" comments on the post
                    MATCH (post)-[:HAS_COMMENT]->(c0:Comment {is_reply:false, deleted:false})
                    WHERE (c0)<-[:PINNED]-(post)

                    // (Optional) Grab the parents author and whether current user liked the parent
                    MATCH (parentAuthor:User)-[:COMMENTED]->(c0)
                    OPTIONAL MATCH (cu)-[parentLike:LIKES]->(c0)

                    // Order the parents as needed
                    WITH cu, c0, parentAuthor, (parentLike IS NOT NULL) AS parentLikedByUser
                    ORDER BY c0.likes DESC, c0.created_date DESC
                    SKIP $skip
                    LIMIT $limit
                """
    else:
        if not pinned:
            query_start = """
                    MATCH (cu:User {id: $user_id, disabled: false})
                    MATCH (post {id: $post_id, deleted: false})-[:POST_FOR_CLUB_BOOK]-(:BookClubBook)-[]-(club:BookClub {id:$book_club_id})
                    WHERE post:ClubUpdate OR post:ClubUpdateNoText 
                        OR post:ClubReview OR post:ClubReviewNoText
                    MATCH (cu)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club)

                    // 1) Match the top-level "parent" comments on the post
                    MATCH (post)-[:HAS_COMMENT]->(c0:Comment {is_reply:false, deleted:false})
                    WHERE NOT (c0)<-[:PINNED]-(post)

                    // (Optional) Grab the parents author and whether current user liked the parent
                    MATCH (parentAuthor:User)-[:COMMENTED]->(c0)
                    OPTIONAL MATCH (cu)-[parentLike:LIKES]->(c0)

                    // Order the parents as needed
                    WITH cu, c0, parentAuthor, (parentLike IS NOT NULL) AS parentLikedByUser
                    ORDER BY c0.likes DESC, c0.created_date DESC
                    SKIP $skip
                    LIMIT $limit
                """
        else:
            query_start = """
                    MATCH (cu:User {id: $user_id, disabled: false})
                    MATCH (post {id: $post_id, deleted: false})-[:POST_FOR_CLUB_BOOK]-(:BookClubBook)-[]-(club:BookClub {id:$book_club_id})
                    WHERE post:ClubUpdate OR post:ClubUpdateNoText 
                        OR post:ClubReview OR post:ClubReviewNoText
                    MATCH (cu)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club)

                    // 1) Match the top-level "parent" comments on the post
                    MATCH (post)-[:HAS_COMMENT]->(c0:Comment {is_reply:false, deleted:false})
                    WHERE (c0)<-[:PINNED]-(post)

                    // (Optional) Grab the parents author and whether current user liked the parent
                    MATCH (parentAuthor:User)-[:COMMENTED]->(c0)
                    OPTIONAL MATCH (cu)-[parentLike:LIKES]->(c0)

                    // Order the parents as needed
                    WITH cu, c0, parentAuthor, (parentLike IS NOT NULL) AS parentLikedByUser
                    ORDER BY c0.likes DESC, c0.created_date DESC
                    SKIP $skip
                    LIMIT $limit
                """

    depth_query_full = ""
    chain_nodes_list = []
    chain_authors_list = []
    chain_liked_bools_list = []
    running_with_statement_during_step = "WITH cu, c0, parentAuthor, parentLikedByUser"
    running_with_statement_after_step = "WITH cu, c0, parentAuthor, parentLikedByUser"
                
    for i in range(1, depth):
        chain_nodes_list.append(f"c{i}")
        chain_authors_list.append(f"c{i}Author{{.id, .username}}")
        chain_liked_bools_list.append(f"c{i}LikedByUser")

        step_before = i - 1
        depth_query_step_start = f"""
        Call {{
            WITH c{step_before}
            OPTIONAL MATCH (c{step_before})<-[:REPLIED_TO]-(c{i}:Comment {{deleted:false, is_reply:true}})
            WITH c{i}
            ORDER BY c{i}.likes DESC, c{i}.created_date DESC
            LIMIT 1
            RETURN c{i}
        }}
            """

        running_with_statement_during_step += f", c{i}"
        if i != 1:
            running_with_statement_during_step += f", c{step_before}Author, c{step_before}LikedByUser"

        depth_query_step_end = f"""
            OPTIONAL MATCH (c{i}Author:User)-[:COMMENTED]->(c{i})
            OPTIONAL MATCH (cu)-[c{i}Like:LIKES]->(c{i})
        """

        depth_query_step = depth_query_step_start + running_with_statement_during_step + depth_query_step_end

        running_with_statement_after_step += f""",
        c{i}, c{i}Author, (c{i}Like IS NOT NULL) AS c{i}LikedByUser"""

        running_with_statement_after_step = running_with_statement_after_step.replace(
            f"(c{step_before}Like IS NOT NULL) AS ", ""
        )

        depth_query_step += running_with_statement_after_step
        depth_query_full += depth_query_step

    chain_nodes_list = "[ " + ", ".join(chain_nodes_list) + "]"
    chain_authors_list = "[ " + ", ".join(chain_authors_list) + "]"
    chain_liked_bools_list = "[ " + ", ".join(chain_liked_bools_list) + "]"

    query_end = f"""
    WITH c0 as parentComment,
    parentAuthor,
    parentLikedByUser,

    {chain_nodes_list} AS chainNodes,
    {chain_authors_list} AS chainAuthors,
    {chain_liked_bools_list} AS chainLikedBools

    // We can zip these together if we like, or just do them in parallel:
    WITH parentComment, parentAuthor, parentLikedByUser,
        apoc.coll.zip(
        chainNodes,
        chainAuthors
        ) AS chain,
        chainLikedBools

    WITH parentComment, parentAuthor, parentLikedByUser,
        apoc.coll.zip(
        chain,
        chainLikedBools
        ) AS chain
        
    RETURN {{
    parentComment: parentComment,
    parentAuthor: parentAuthor{{.id, .username}},
    parentLikedByUser: parentLikedByUser,
    chainedReplies: [nodeAuthorLike IN chain |
        {{
        node: nodeAuthorLike[0][0],
        author: nodeAuthorLike[0][1],
        likedByUser: nodeAuthorLike[1]
        }}
    ]
    }} AS parentWithChain
    """

    # query = query_start + depth_query_full + return_depth_full + query_end
    query = query_start + depth_query_full + query_end

    return query

def build_get_comments_for_comment_query(
        depth: int,
        book_club_posts: bool = False
    ) -> str:
    """
    Builds the comments query when using a specific comment
    for threads to a certain depth

    Args:
        depth: The maximum depth to make comments until
        book_club_posts: Whether the post is from a book club
        pinned: Whether or not to only grab pinned comments

    Returns:
        query (str): The query to run with comments
    """

    if not book_club_posts:
        query_start = """
                MATCH (cu:User {id: $user_id, disabled: false})
                MATCH (post {id: $post_id, deleted: false})
                WHERE post:Review OR post:Milestone 
                    OR post:Update OR post:Comparison

                // 1) Match the top-level "parent" comments on the post
                MATCH (post)-[:HAS_COMMENT]->(comment:Comment {id: $comment_id, deleted:false})
                MATCH (comment)<-[:REPLIED_TO]-(c0:Comment {deleted:false})

                // (Optional) Grab the parents author and whether current user liked the parent
                MATCH (parentAuthor:User)-[:COMMENTED]->(c0)
                OPTIONAL MATCH (cu)-[parentLike:LIKES]->(c0)

                // Order the parents as needed
                WITH cu, c0, parentAuthor, (parentLike IS NOT NULL) AS parentLikedByUser
                ORDER BY c0.likes DESC, c0.created_date DESC
                SKIP $skip
                LIMIT $limit
            """
    else:
        query_start = """
                MATCH (cu:User {id: $user_id, disabled: false})
                MATCH (post {id: $post_id, deleted: false})-[:POST_FOR_CLUB_BOOK]-(:BookClubBook)-[]-(club:BookClub {id:$book_club_id})
                WHERE post:ClubUpdate OR post:ClubUpdateNoText 
                    OR post:ClubReview OR post:ClubReviewNoText
                MATCH (cu)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]->(club)

                // 1) Match the top-level "parent" comments on the post
                MATCH (post)-[:HAS_COMMENT]->(comment:Comment {id: $comment_id, deleted:false})
                MATCH (comment)<-[:REPLIED_TO]-(c0:Comment {deleted:false})

                // (Optional) Grab the parents author and whether current user liked the parent
                MATCH (parentAuthor:User)-[:COMMENTED]->(c0)
                OPTIONAL MATCH (cu)-[parentLike:LIKES]->(c0)

                // Order the parents as needed
                WITH cu, c0, parentAuthor, (parentLike IS NOT NULL) AS parentLikedByUser
                ORDER BY c0.likes DESC, c0.created_date DESC
                SKIP $skip
                LIMIT $limit
            """
       
    depth_query_full = ""
    chain_nodes_list = []
    chain_authors_list = []
    chain_liked_bools_list = []
    running_with_statement_during_step = "WITH cu, c0, parentAuthor, parentLikedByUser"
    running_with_statement_after_step = "WITH cu, c0, parentAuthor, parentLikedByUser"
                
    for i in range(1, depth):
        chain_nodes_list.append(f"c{i}")
        chain_authors_list.append(f"c{i}Author{{.id, .username}}")
        chain_liked_bools_list.append(f"c{i}LikedByUser")

        step_before = i - 1
        depth_query_step_start = f"""
        Call {{
            WITH c{step_before}
            OPTIONAL MATCH (c{step_before})<-[:REPLIED_TO]-(c{i}:Comment {{deleted:false, is_reply:true}})
            WITH c{i}
            ORDER BY c{i}.likes DESC, c{i}.created_date DESC
            LIMIT 1
            RETURN c{i}
        }}
            """

        running_with_statement_during_step += f", c{i}"
        if i != 1:
            running_with_statement_during_step += f", c{step_before}Author, c{step_before}LikedByUser"

        depth_query_step_end = f"""
            OPTIONAL MATCH (c{i}Author:User)-[:COMMENTED]->(c{i})
            OPTIONAL MATCH (cu)-[c{i}Like:LIKES]->(c{i})
        """

        depth_query_step = depth_query_step_start + running_with_statement_during_step + depth_query_step_end

        running_with_statement_after_step += f""",
        c{i}, c{i}Author, (c{i}Like IS NOT NULL) AS c{i}LikedByUser"""

        running_with_statement_after_step = running_with_statement_after_step.replace(
            f"(c{step_before}Like IS NOT NULL) AS ", ""
        )

        depth_query_step += running_with_statement_after_step
        depth_query_full += depth_query_step

    chain_nodes_list = "[ " + ", ".join(chain_nodes_list) + "]"
    chain_authors_list = "[ " + ", ".join(chain_authors_list) + "]"
    chain_liked_bools_list = "[ " + ", ".join(chain_liked_bools_list) + "]"

    query_end = f"""
    WITH c0 as parentComment,
    parentAuthor,
    parentLikedByUser,

    {chain_nodes_list} AS chainNodes,
    {chain_authors_list} AS chainAuthors,
    {chain_liked_bools_list} AS chainLikedBools

    // We can zip these together if we like, or just do them in parallel:
    WITH parentComment, parentAuthor, parentLikedByUser,
        apoc.coll.zip(
        chainNodes,
        chainAuthors
        ) AS chain,
        chainLikedBools

    WITH parentComment, parentAuthor, parentLikedByUser,
        apoc.coll.zip(
        chain,
        chainLikedBools
        ) AS chain
        
    RETURN {{
    parentComment: parentComment,
    parentAuthor: parentAuthor{{.id, .username}},
    parentLikedByUser: parentLikedByUser,
    chainedReplies: [nodeAuthorLike IN chain |
        {{
        node: nodeAuthorLike[0][0],
        author: nodeAuthorLike[0][1],
        likedByUser: nodeAuthorLike[1]
        }}
    ]
    }} AS parentWithChain
    """

    # query = query_start + depth_query_full + return_depth_full + query_end
    query = query_start + depth_query_full + query_end

    return query

def build_comment_object(
    comment_data: dict,
    comment_author: dict,
    liked_by_user: bool,
    post_id: str,
    current_user_id:str,
    parent_comment_id: Optional[str] = None     
) -> Comment:
    """
    Builds a comment object from query response

    Args:
        comment_data: The data from the Comment node
        comment_auth: The data from the comments Author node
        liked_by_user: If the current user liked to comment
        post_id: The id of the post for the comment
        current_user_id: The id of the current user
        parent_comment_id: If the comment is a reply, this is the id of the parent comment
    """
    return Comment(
                id=comment_data['id'],
                created_date=comment_data['created_date'],
                liked_by_current_user=liked_by_user,
                post_id=post_id,
                user_id=comment_author['id'],
                username=comment_author['username'],
                text=comment_data.get("text",""),
                replied_to=parent_comment_id,
                posted_by_current_user=comment_author['id'] == current_user_id,
                likes=comment_data.get('likes',0),
                num_replies=comment_data.get('num_replies',0)
            )