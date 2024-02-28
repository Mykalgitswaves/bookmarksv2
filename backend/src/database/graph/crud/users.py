from fastapi import HTTPException
from src.database.graph.crud.base import BaseCRUDRepositoryGraph
from src.models.schemas.users import UserCreate, User, UserLogin, UserWithPassword, UserSettings

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
    
