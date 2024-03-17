from src.database.graph.crud.base import BaseCRUDRepositoryGraph

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
        