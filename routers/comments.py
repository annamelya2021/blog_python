from datetime import datetime

class Comment:
    def __init__(self, content, author, post_id, created_at=None):
        self.content = content
        self.author = author  # username автора
        self.post_id = post_id  # ID поста
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            'content': self.content,
            'author': self.author,
            'post_id': self.post_id,
            'created_at': self.created_at
        }