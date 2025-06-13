from flask import Flask
from app.extensions import mongo, login_manager
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    
    # Завантаження змінних середовища
    load_dotenv()
    
    # Конфігурація
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    
    # Ініціалізація розширень
    mongo.init_app(app)
    login_manager.init_app(app)

     # Завантажувач користувачів для Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({'_id': user_id})
        if user_data:
            return User(user_data)
        return None
    
    # Реєстрація блюпринтів
    from routers.auth import auth_bp
    from routers.main import main_bp
    from routers.posts import posts_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    return app