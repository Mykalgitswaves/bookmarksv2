from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.users import UserCreate, User, UserLogin, UserWithPassword

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
    
