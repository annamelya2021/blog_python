from flask import Blueprint
from pymongo.errors import ConnectionFailure
from app.extensions import mongo

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return "Головна сторінка блогу. <a href='/auth/register'>Реєстрація</a> | <a href='/check_db'>Перевірити БД</a>"

@main_bp.route('/check_db')
def check_db():
    try:
        # Отримуємо колекцію через mongo.db
        users_collection = mongo.db.users
        # Перевіряємо підключення
        mongo.cx.admin.command('ping')
        users_count = users_collection.count_documents({})
        return f"<h1>Підключено ✅</h1><p>Користувачів у базі: {users_count}</p><a href='/'>На головну</a>"
    except ConnectionFailure as e:
        return f"<h1>Помилка ❌</h1><p>Помилка підключення до бази даних: {str(e)}</p><a href='/'>На головну</a>"
    except Exception as e:
        return f"<h1>Помилка ❌</h1><p>Сталася помилка: {str(e)}</p><a href='/'>На головну</a>"
