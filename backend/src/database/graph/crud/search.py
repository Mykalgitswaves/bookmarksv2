from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.search import SearchResultUser, SearchResultBookClub

class SearchCRUDRepositoryGraph(BaseCRUDRepositoryGraph):
    def search_for_param(self, param: str, skip: int, limit: int):
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
    
    def get_users_full_text_search(self, 
                                   search_query:str, 
                                   skip:int, 
                                   limit:int, 
                                   current_user_id:str):
        
        """
        Searches all user by the full text index (username and full name)
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_users_full_text_search_query, search_query=search_query, skip=skip, limit=limit, current_user_id=current_user_id)
        return(result)
    
    @staticmethod
    def get_users_full_text_search_query(tx, 
                                         search_query:str, 
                                         skip:int, 
                                         limit:int, 
                                         current_user_id:str):
        query = """
        MATCH (currentUser:User {id: $current_user_id})
        CALL db.index.fulltext.queryNodes('userFullText', $search_query)
        YIELD node, score
        OPTIONAL MATCH (currentUser)<-[incomingFriendStatus:FRIENDED]-(node)
        OPTIONAL MATCH (currentUser)-[outgoingFriendStatus:FRIENDED]->(node)
        OPTIONAL MATCH (currentUser)<-[incomingBlockStatus:BLOCKED]-(node)
        OPTIONAL MATCH (currentUser)-[outgoingBlockStatus:BLOCKED]->(node)
        OPTIONAL MATCH (currentUser)<-[incomingFollowStatus:FOLLOWS]-(node)
        OPTIONAL MATCH (currentUser)-[outgoingFollowStatus:FOLLOWS]->(node)
        RETURN node, currentUser,
            incomingFriendStatus.status AS incomingFriendStatus,
            incomingBlockStatus,
            incomingFollowStatus,
            outgoingFriendStatus.status AS outgoingFriendStatus,
            outgoingBlockStatus,
            outgoingFollowStatus, 
            score
        ORDER BY score DESC
        SKIP $skip
        LIMIT $limit
        """

        result = tx.run(query, 
                        search_query=search_query, 
                        skip=skip, 
                        limit=limit, 
                        current_user_id=current_user_id)
        
        user_list = []
        for response in result:
            if 'profile_img_url' in response['node']:
                profile_img_url = response['node']['profile_img_url']
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
            elif response['node']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'stranger'

            user = SearchResultUser(
                id=response['node']['id'],
                username=response['node']['username'],
                disabled=False,
                created_date=response['node']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user
            )

            user_list.append(user)

        return user_list
    
    def get_friends_full_text_search(self, 
                                   search_query:str, 
                                   skip:int, 
                                   limit:int, 
                                   current_user_id:str):
        
        """
        Searches all user by the full text index (username and full name)
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_friends_full_text_search_query, search_query=search_query, skip=skip, limit=limit, current_user_id=current_user_id)
        return(result)
    
    @staticmethod
    def get_friends_full_text_search_query(tx, 
                                         search_query:str, 
                                         skip:int, 
                                         limit:int, 
                                         current_user_id:str):
        query = """
        MATCH (currentUser:User {id: $current_user_id})-[:FRIENDED {status:"friends"}]-(friend:User)
        WITH collect(friend) as friends
        CALL db.index.fulltext.queryNodes('userFullText', $search_query)
        YIELD node, score
        WHERE node IN friends
        RETURN node, score
        ORDER BY score DESC
        SKIP $skip
        LIMIT $limit
        """

        result = tx.run(query, 
                        search_query=search_query, 
                        skip=skip, 
                        limit=limit, 
                        current_user_id=current_user_id)
        user_list = []
        for response in result:
            if 'profile_img_url' in response['node']:
                profile_img_url = response['node']['profile_img_url']
            else:
                profile_img_url = None

            if response['node']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'friend'

            user = SearchResultUser(
                id=response['node']['id'],
                username=response['node']['username'],
                disabled=False,
                created_date=response['node']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user
            )

            user_list.append(user)

        return user_list
    
    def get_friends_full_text_search_no_bookshelf_access(self, 
                                                        search_query:str, 
                                                        skip:int, 
                                                        limit:int, 
                                                        current_user_id:str,
                                                        bookshelf_id:str):
        
        """
        Searches all user by the full text index (username and full name)
        """
        with self.driver.session() as session:
            result = session.execute_read(self.get_friends_full_text_search_no_bookshelf_access_query, 
                                          search_query=search_query, 
                                          skip=skip, 
                                          limit=limit, 
                                          current_user_id=current_user_id,
                                          bookshelf_id=bookshelf_id)
        return(result)
    
    @staticmethod
    def get_friends_full_text_search_no_bookshelf_access_query(tx, 
                                                                search_query:str, 
                                                                skip:int, 
                                                                limit:int, 
                                                                current_user_id:str,
                                                                bookshelf_id:str):
        query = """
        MATCH (currentUser:User {id: $current_user_id})-[:FRIENDED {status:"friends"}]-(friend:User)
        WHERE NOT (friend)-[:HAS_BOOKSHELF_ACCESS]->(:Bookshelf {id: $bookshelf_id})
        WITH friend
        WITH collect(friend) as friends
        CALL db.index.fulltext.queryNodes('userFullText', $search_query + "*")
        YIELD node, score
        WHERE node IN friends
        RETURN node, score
        ORDER BY score DESC
        SKIP $skip
        LIMIT $limit
        """
        result = tx.run(query, 
                        search_query=search_query, 
                        skip=skip, 
                        limit=limit, 
                        current_user_id=current_user_id,
                        bookshelf_id=bookshelf_id)
        user_list = []
        for response in result:
            if 'profile_img_url' in response['node']:
                profile_img_url = response['node']['profile_img_url']
            else:
                profile_img_url = None

            if response['node']['id'] == current_user_id:
                relationship_to_current_user = 'is_current_user'
            else:
                relationship_to_current_user = 'friend'

            user = SearchResultUser(
                id=response['node']['id'],
                username=response['node']['username'],
                disabled=False,
                created_date=response['node']['created_date'],
                profile_img_url=profile_img_url,
                relationship_to_current_user=relationship_to_current_user
            )

            user_list.append(user)

        return user_list
    
    def get_bookclubs_full_text_search(
            self, 
            search_query:str, 
            skip:int, 
            limit:int):
        
        """
        Searches all user by the full text index (username and full name)
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_bookclubs_full_text_search_query, 
                search_query=search_query, 
                skip=skip, 
                limit=limit
                )
        return(result)
    
    @staticmethod
    def get_bookclubs_full_text_search_query(
        tx, 
        search_query:str, 
        skip:int, 
        limit:int):

        query = (
            """
        CALL db.index.fulltext.queryNodes('bookclubsFullText', "*" + $search_query + "*")
        YIELD node, score
        MATCH (node)-[:IS_MEMBER_OF|OWNS_BOOK_CLUB]-(members:User)
        OPTIONAL MATCH (node)-[:IS_READING]->(bc_book:BookClubBook)-[:IS_EQUIVALENT_TO]->(book:Book)
        RETURN node, 
        score,
        count(members) as number_of_members,
        book.title as current_book_title, 
        book.id as current_book_id, 
        book.small_img_url as current_book_small_img_url
        ORDER BY score DESC
        SKIP $skip
        LIMIT $limit
        """
        )

        result = tx.run(
            query, 
            search_query=search_query, 
            skip=skip, 
            limit=limit
            )
        
        bookclub_list = []

        for response in result:
            if response['current_book_title'] != None:
                current_book = {
                    'title': response.get('current_book_title'),
                    'id': response['current_book_id'],
                    'small_img_url': response.get('current_book_small_img_url')
                }
            else:
                current_book = None

            bookclub = SearchResultBookClub(
                current_book=current_book,
                name=response['node'].get("name"),
                number_of_members=response.get("number_of_members", 0),
                id=response['node'].get("id")
            )
            bookclub_list.append(bookclub)

        return bookclub_list
    
    def get_bookshelves_full_text_search(
            self, 
            search_query:str, 
            skip:int, 
            limit:int):
        
        """
        Searches all user by the full text index (username and full name)
        """
        with self.driver.session() as session:
            result = session.execute_read(
                self.get_bookshelves_full_text_search_query, 
                search_query=search_query, 
                skip=skip, 
                limit=limit
                )
        return(result)
    
    @staticmethod
    def get_bookshelves_full_text_search_query(
        tx, 
        search_query:str, 
        skip:int, 
        limit:int):

        query = (
            """
        CALL db.index.fulltext.queryNodes('bookshelvesFullText', "*" + $search_query + "*")
        YIELD node, score
        MATCH (node)-[:HAS_BOOKSHELF_ACCESS {type:"owner"}]-(owner:User)
        OPTIONAL MATCH (node)-[:CONTAINS_BOOK]->(book:Book)
        RETURN node, 
        score,
        collect(book) as books,
        count(book) as number_of_books,
        owner.username as owner_username
        ORDER BY score DESC
        SKIP $skip
        LIMIT $limit
        """
        )

        result = tx.run(
            query, 
            search_query=search_query, 
            skip=skip, 
            limit=limit
            )
        
        bookshelf_list = []

        for response in result:
            print(response['node'].get("books"))
            print(response.get("books"))
            first_book = None
            if response['node'].get("books") and response.get("books"):
                first_book_id = response['node'].get("books")[0]
                for book in response.get("books"):
                    if book.get("id") == first_book_id:
                        first_book = {
                            'title': book.get("title"),
                            'id': book.get("id"),
                            'small_img_url': book.get("small_img_url")
                        }
                        break
            

            bookshelf = {
                'name': response['node'].get("title"),
                'description': response['node'].get("description"),
                'number_of_books': response.get("number_of_books", 0),
                'first_book': first_book,
                'owner_username': response.get("owner_username", None),
                'id': response['node'].get("id")
            }
            bookshelf_list.append(bookshelf)

        return bookshelf_list