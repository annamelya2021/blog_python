from flask import Blueprint, render_template_string, url_for, redirect, flash, request
from flask_login import login_required, current_user
from bson import ObjectId
from app.models import Post
from app.extensions import mongo

posts_bp = Blueprint('posts', __name__)

def get_nav_links():
    links = []
    if current_user.is_authenticated:
        links.append(f'<a href="{url_for("main.home")}">Головна</a>')
        links.append(f'<a href="{url_for("posts.list_posts")}">Всі пости</a>')
        # Змінити на перевірку ролі, як у new_post
        if current_user.role in ['author', 'admin']:
            links.append(f'<a href="{url_for("posts.new_post")}">Створити пост</a>')
        links.append(f'<a href="{url_for("auth.logout")}">Вийти ({current_user.username})</a>')
    else:
        links = [
            f'<a href="{url_for("main.home")}">Головна</a>',
            f'<a href="{url_for("posts.list_posts")}">Всі пости</a>',
            f'<a href="{url_for("auth.login")}">Увійти</a>',
            f'<a href="{url_for("auth.register")}">Реєстрація</a>'
        ]
    return ' | '.join(links)

@posts_bp.route('/posts')
def list_posts():
    posts = Post.get_all_published()
    posts_html = ""
    for post in posts:
        posts_html += f"""
        <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;">
            <h3><a href="{url_for('posts.view_post', post_id=post.id)}">{post.title}</a></h3>
            <p>{post.content[:100]}...</p>
        </div>
        """
    
    return f"""
    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>Всі пости</h1>
        <div style="margin-bottom: 20px; padding: 10px; background: #f5f5f5;">
            {get_nav_links()}
        </div>
        {posts_html if posts_html else "<p>Ще немає жодного поста.</p>"}
    </div>
    """

@posts_bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.role not in ['author', 'admin']:
        flash('Тільки автори можуть створювати пости', 'error')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            post = Post({
                'title': title,
                'content': content,
                'author_id': str(current_user.id),
                'author_name': current_user.username,
                'is_published': True
            })
            post.save()
            flash('Пост успішно створено!', 'success')
            return redirect(url_for('posts.view_post', post_id=post.id))
    
    return f"""
    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>Створити новий пост</h1>
        <div style="margin-bottom: 20px; padding: 10px; background: #f5f5f5;">
            {get_nav_links()}
        </div>
        <form method="POST" style="margin-top: 20px;">
            <div style="margin-bottom: 15px;">
                <label>Заголовок:</label><br>
                <input type="text" name="title" required style="width: 100%; padding: 5px;">
            </div>
            <div style="margin-bottom: 15px;">
                <label>Зміст:</label><br>
                <textarea name="content" required style="width: 100%; height: 200px; padding: 5px;"></textarea>
            </div>
            <button type="submit" style="padding: 5px 10px;">Опублікувати</button>
        </form>
        <p style="margin-top: 20px;"><a href="{url_for('posts.list_posts')}">← Назад до всіх постів</a></p>
    </div>
    """

@posts_bp.route('/posts/<post_id>')
def view_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        return "Пост не знайдено", 404
    
    author = getattr(post, 'author_name', 'Невідомий автор')
    
    return f"""
    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <div style="margin-bottom: 20px; padding: 10px; background: #f5f5f5;">
            {get_nav_links()}
        </div>
        <h1>{post.title}</h1>
        <p><small>Автор: {author} | {post.created_at.strftime('%d.%m.%Y %H:%M')}</small></p>
        <div style="margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; line-height: 1.6;">
            {post.content.replace('\n', '<br>')}
        </div>
        <p><a href="{url_for('posts.list_posts')}">← Назад до всіх постів</a></p>
    </div>
    """