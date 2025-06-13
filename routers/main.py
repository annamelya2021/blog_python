from flask import Blueprint, render_template_string, url_for, redirect, flash, get_flashed_messages
from flask_login import current_user, login_required
from pymongo.errors import ConnectionFailure
from app.extensions import mongo
from app.models import Post

main_bp = Blueprint('main', __name__)

def get_nav_links():
    """Повертає HTML з посиланнями навігації залежно від статусу користувача"""
    if current_user.is_authenticated:
        links = [
            f'<a href="{url_for("main.home")}">Головна</a>',
            f'<a href="{url_for("posts.list_posts")}">Всі пости</a>'
        ]
        
        # Додаємо посилання для авторів та адміністраторів
        if current_user.role in ['author', 'admin']:
            links.append(f'<a href="{url_for("posts.new_post")}">Створити пост</a>')
            
        # Додаємо посилання для виходу
        links.append(f'<a href="{url_for("auth.logout")}">Вийти ({current_user.username})</a>')
    else:
        links = [
            f'<a href="{url_for("main.home")}">Головна</a>',
            f'<a href="{url_for("posts.list_posts")}">Всі пости</a>',
            f'<a href="{url_for("auth.login")}">Увійти</a>',
            f'<a href="{url_for("auth.register")}">Реєстрація</a>'
        ]
    
    return ' | '.join(links)

@main_bp.route('/')
def home():
    # Отримуємо останні 5 опублікованих постів
    recent_posts = Post.get_all_published()[:5]
    
    # Створюємо HTML для постів
    posts_html = ""
    if recent_posts:
        for post in recent_posts:
            posts_html += f"""
            <div class="post-preview">
                <h2><a href="{url_for('posts.view_post', post_id=post.id)}">{post.title}</a></h2>
                <p class="post-meta">Опубліковано {post.published_at.strftime('%d.%m.%Y') if post.published_at else 'Чернетка'}</p>
                <p>{post.content[:200]}...</p>
                <a href="{url_for('posts.view_post', post_id=post.id)}">Читати далі</a>
            </div>
            <hr>
            """
    else:
        posts_html = "<p>Ще немає опублікованих постів.</p>"
    
    # Отримуємо повідомлення
    messages_html = ''
    for category, message in get_flashed_messages(with_categories=True):
        messages_html += f'<div class="alert alert-{category}">{message}</div>'
    
    # Головна сторінка
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Головна - Блог</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px; 
                line-height: 1.6;
            }}
            .nav {{ 
                background: #f8f9fa; 
                padding: 15px; 
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            .nav a {{ 
                margin-right: 15px; 
                text-decoration: none;
                color: #007bff;
            }}
            .nav a:hover {{ 
                text-decoration: underline;
            }}
            .post-preview {{ 
                margin-bottom: 30px; 
                padding: 15px;
                border: 1px solid #eee;
                border-radius: 5px;
            }}
            .post-meta {{ 
                color: #6c757d; 
                font-size: 0.9em;
                margin-bottom: 10px;
            }}
            .alert {{
                padding: 10px;
                margin-bottom: 20px;
                border: 1px solid transparent;
                border-radius: 4px;
            }}
            .alert-success {{
                color: #155724;
                background-color: #d4edda;
                border-color: #c3e6cb;
            }}
            .alert-error, .alert-danger {{
                color: #721c24;
                background-color: #f8d7da;
                border-color: #f5c6cb;
            }}
            h1 {{ color: #333; }}
            a {{ color: #007bff; }}
            a:hover {{ text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="nav">
            {get_nav_links()}
        </div>
        
        {messages_html}
        
        <h1>Останні публікації</h1>
        
        {posts_html}
        
        <div class="actions">
            <p><a href="{url_for('posts.list_posts')}">Переглянути всі пости →</a></p>
        </div>
    </body>
    </html>
    """

@main_bp.route('/check_db')
def check_db():
    try:
        # Спроба отримати дані з БД
        mongo.db.command('ping')
        return """
            <h1>Підключення до бази даних успішне!</h1>
            <p>Статус: <span style="color: green;">Працює</span></p>
            <a href="{}">На головну</a>
        """.format(url_for('main.home'))
    except ConnectionFailure as e:
        return """
            <h1>Помилка підключення до бази даних!</h1>
            <p>Статус: <span style="color: red;">Не працює</span></p>
            <p>Помилка: {}</p>
            <a href="{}">На головну</a>
        """.format(str(e), url_for('main.home'))

# Додаткові маршрути для головної сторінки
@main_bp.route('/about')
def about():
    return "<h1>Про блог</h1><p>Це простий блог, створений на Flask.</p>"

@main_bp.route('/contact')
def contact():
    return "<h1>Контакти</h1><p>Зв'яжіться з нами за адресою example@example.com</p>"

# Додаткові маршрути для адміністратора
@main_bp.route('/admin')
@login_required
def admin_panel():
    if not current_user.role == 'admin':
        flash('Доступ заборонено. Потрібні права адміністратора.', 'error')
        return redirect(url_for('main.home'))
    
    # Тут буде адмін-панель
    return "<h1>Панель адміністратора</h1><p>Тут буде керування сайтом</p>"
