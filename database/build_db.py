from neo4j import GraphDatabase

class neo4jDriver():
    def __init__(self):
        uri = "bolt://localhost:7687"
        self.driver = GraphDatabase.driver(uri, auth = ("neo4j","password"))
    def run_load_from_csv(self,path):
        with self.driver.session() as session:
            result = session.execute_write(self.load_from_csv, path)
    @staticmethod
    def load_from_csv(tx,path):
        query = f"""
                load csv with headers from "file:///{path}" as csvLine
                create (b:Book {{gr_id: toInteger(csvLine.goodreads_book_id), id: toInteger(csvLine.book_id), originalPublicationYear: toInteger(csvLine.original_publication_year), title:csvLine.title, lang:csvLine.language_code, img_url: csvLine.image_url, small_img_url:csvLine.small_image_url, isbn24:csvLine.isbn13, pages:csvLine.pages,description:csvLine.description}})
                """
        # query = f""":auto load csv with headers from 'file:///C:/Users/Kyle/bookmarx/data/ratings_small_ids.csv' as csvLine
        #         Call {{ with csvLine match (b:Book {{id:toInteger(csvLine.book_id)}})
        #         merge (rev:Review {{id:toInteger(csvLine.rating_id),rating:toInteger(csvLine.rating)}})
        #         merge (rev)-[r:IS_REVIEW_OF]->(b)}} In transactions of 1000 rows
        #         """
        # query = f""":auto load csv with headers from 'file:///C:/Users/Kyle/bookmarx/data/ratings_small_ids.csv' as csvLine
        #         Call {{ with csvLine match (rev:Review {{id:toInteger(csvLine.rating_id)}})
        #         merge (u:User {{id:toInteger(csvLine.user_id)}})
        #         merge (u)-[r:WROTE_REVIEW]->(rev)}} In transactions of 1000 rows
        #         """
        # query = f"""
        #          load csv with headers from "file:///{path}" as csvLine
        #          create (t:Tag {{id: toInteger(csvLine.tag_id), name: csvLine.tag_name}})
        #          """
        # query = f"""
        #         load csv with headers from "file:///{path}" as csvLine
        #          Call {{ with csvLine match (b:Book {{gr_id:toInteger(csvLine.goodreads_book_id)}})
        #          match (t:Tag {{id:toInteger(csvLine.tag_id)}})
        #          merge (b)-[has_t:HAS_TAG{{count:toInteger(csvLine.count)}}]->(t)}}
        #         """
        # query = f"""
        #         load csv with headers from "file:///{path}" as csvLine
        #         Call {{ with csvLine match (b:Book {{id:toInteger(csvLine.book_id)}})
        #          merge (a:Author {{id:toInteger(csvLine.author_id), name:csvLine.authors}})
        #          merge (a)-[w:WROTE]->(b)}}
        #         """
        # query = f"""
        #         load csv with headers from "file:///{path}" as csvLine
        #          Call {{ with csvLine match (b:Book {{id:toInteger(csvLine.book_id)}})
        #           merge (g:Genre {{id:toInteger(csvLine.genre_id), name:csvLine.genres}})
        #           merge (b)-[hg:HAS_GENRE]->(g)}}
        #          """
        # query = f""":auto load csv with headers from 'file:///C:/Users/Kyle/bookmarx/data/to_read.csv' as csvLine
        #         Call {{ with csvLine match (b:Book {{id:toInteger(csvLine.book_id)}})
        #         match (u:User {{id:toInteger(csvLine.user_id)}})
        #         merge (u)-[r:TO_READ]->(b)}} In transactions of 1000 rows
        #         """
        # query = f"""
        #             load csv with headers from "file:///{path}" as csvLine
        #             Call {{ with csvLine match (u:User {{id:toInteger(csvLine.user_id)}})
        #             set u += {{username:csvLine.username,created_date:date(csvLine.account_created)}}
        # """
        # query = f""":auto load csv with headers from 'C:/Users/Kyle/bookmarx/data/user_data.csv' as csvLine
        #          Call {{ with csvLine match (f:User {{id:toInteger(csvLine.friend_id)}})
        #          match (u:User {{id:toInteger(csvLine.user_id)}})
        #          match (r:Review {{id:toInteger(csvLine.liked_review)}})
        #          match (r_b:Book {{id:toInteger(csvLine.is_reading)}})
        #          match (g:Genre {{id:toInteger(csvLine.favorite_genre)}})
        #          match (a:Author {{id:toInteger(csvLine.favorite_author)}})
        #          merge (u)-[has_f:HAS_FRIEND]-(f)
        #          merge (u)-[l_r:LIKES]->(r)
        #          merge (u)-[ir:IS_READING]->(r_b)
        #          merge (u)-[l_r_g]:LIKES]->(g)
        #          merge (u)-[l_r_a]:LIKES]->(a)}} In transactions of 1000 rows
        #          """
        result = tx.run(query)
        return(result)
    def close(self):
        self.driver.close()

driver = neo4jDriver()
driver.run_load_from_csv("C:/Users/Kyle/bookmarx/data/user_data.csv")
driver.close()