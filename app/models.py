from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import mongo

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password']
        self.role = user_data.get('role', 'user')
        self._is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at', datetime.utcnow())

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_author(self):
        return self.role in ['author', 'admin']

    @staticmethod
    def get_by_email(email):
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def create(username, email, password, role='user'):
        if mongo.db.users.find_one({'email': email}):
            return None
            
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

        
class Post:
    def __init__(self, post_data):
        self.id = str(post_data.get('_id', ObjectId()))
        self.title = post_data['title']
        self.content = post_data['content']
        self.author_id = post_data['author_id']
        self.is_published = post_data.get('is_published', False)
        self.created_at = post_data.get('created_at', datetime.utcnow())
        self.updated_at = post_data.get('updated_at', datetime.utcnow())
        self.comments = post_data.get('comments', [])

    def save(self):
        post_data = {
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'is_published': self.is_published,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'comments': self.comments
        }
        
        if hasattr(self, '_id'):
            mongo.db.posts.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': post_data}
            )
        else:
            result = mongo.db.posts.insert_one(post_data)
            self.id = str(result.inserted_id)

    @staticmethod
    def get_by_id(post_id):
        try:
            post_data = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
            if post_data:
                return Post(post_data)
            return None
        except:
            return None

    @staticmethod
    def get_all_published():
        posts = mongo.db.posts.find({'is_published': True}).sort('created_at', -1)
        return [Post(post) for post in posts]

    def add_comment(self, user_id, content):
        comment = {
            'user_id': user_id,
            'content': content,
            'created_at': datetime.utcnow()
        }
        self.comments.append(comment)
        mongo.db.posts.update_one(
            {'_id': ObjectId(self.id)},
            {'$push': {'comments': comment}}
        )