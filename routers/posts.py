from datetime import datetime

class Post:
    def __init__(self, title, content, author, image=None, is_published=False, created_at=None, updated_at=None):
        self.title = title
        self.content = content
        self.author = author  # username автора
        self.image = image  # шлях до зображення
        self.is_published = is_published  # чи опубліковано адміном
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.comments = []  # список коментарів
    
    def to_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'image': self.image,
            'is_published': self.is_published,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'comments': self.comments
        }