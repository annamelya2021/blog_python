from flask import Flask
from app.extensions import mongo
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    
    # Завантаження змінних середовища
    load_dotenv()
    
    # Конфігурація
    app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    
    # Ініціалізація розширень
    mongo.init_app(app)
    
    # Реєстрація блюпринтів
    from routers.auth import auth_bp
    from routers.main import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    return app