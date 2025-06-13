from flask import Flask, request, redirect, url_for, render_template, session, flash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

MONGO_URI = 'mongodb+srv://annabasyuk:YR4xMbWSTHp7M1Pq@cluster0.n0doxn9.mongodb.net/blogdb?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client.blogdb
users_collection = db.users
posts_collection = db.posts  # Додаємо колекцію для постів

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Будь ласка, увійдіть, щоб переглянути цю сторінку.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Головна
@app.route('/')
def home():
    # Отримуємо всі пости з бази даних, відсортовані за датою створення (нові спочатку)
    posts = list(posts_collection.find().sort('created_at', -1))
    print(f"Знайдено постів: {len(posts)}")  # Додамо для налагодження
    return render_template('home.html', posts=posts)
# Перевірка підключення
@app.route('/check_db')
def check_db():
    try:
        client.admin.command('ping')
        users_count = users_collection.count_documents({})
        return f"<h1>Підключено </h1><p>Користувачів у базі: {users_count}</p><a href='/'>На головну</a>"
    except ConnectionFailure as e:
        return f"<h1>Помилка </h1><p>{str(e)}</p><a href='/'>На головну</a>"

# Логін
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Спроба входу з email: {email}")  # Додано для налагодження
        
        if not email or not password:
            flash('Будь ласка, заповніть усі поля')
            return redirect(url_for('login'))
        
        user = users_collection.find_one({'email': email})
        print(f"Знайдено користувача: {user}")  # Додано для налагодження
        
        if user:
            print(f"Хеш паролю з БД: {user['password']}")  # Додано для налагодження
            print(f"Введений пароль: {password}")  # Добавлено для налагодження
            password_match = check_password_hash(user['password'], password)
            print(f"Паролі збігаються: {password_match}")  # Додано для налагодження
        
        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['email'] = user['email']
            print(f"Сесія після входу: {dict(session)}")  # Додано для налагодження
            flash(f'Вітаємо, {user["username"]}! Ви успішно увійшли.')
            return redirect(url_for('home'))
        else:
            flash('Невірний email або пароль')
    
    return render_template('login.html')

# Вихід
@app.route('/logout')
def logout():
    print(f"Сесія перед виходом: {dict(session)}")  # Додано для налагодження
    session.clear()
    print("Сесія очищена")  # Додано для налагодження
    flash('Ви вийшли з акаунту')
    return redirect(url_for('home'))

# Реєстрація користувача
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        if users_collection.find_one({'email': email}):
            flash('Користувач з таким email вже існує')
            return redirect(url_for('register'))

        new_user = {
            'username': username,
            'email': email,
            'password': password,
            'role': 'user',
            'is_active': True,
            'created_at': datetime.utcnow()
        }

        users_collection.insert_one(new_user)
        flash('Реєстрація успішна! Будь ласка, увійдіть.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Новий пост (приклад захищеного маршруту)
@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Будь ласка, заповніть усі поля')
            return redirect(url_for('new_post'))
        
        # Створюємо новий пост
        new_post = {
            'title': title,
            'content': content,
            'author_id': session['user_id'],
            'author_username': session['username'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Зберігаємо пост у базі даних
        posts_collection.insert_one(new_post)
        
        flash('Пост успішно створено!')
        return redirect(url_for('home'))
    
    return render_template('new_post.html')

# Редагування посту
@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    
    # Перевіряємо, чи існує пост і чи є користувач його автором
    if not post:
        flash('Пост не знайдено')
        return redirect(url_for('home'))
    
    if str(post['author_id']) != session['user_id']:
        flash('Ви не маєте прав на редагування цього посту')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Будь ласка, заповніть усі поля')
            return redirect(url_for('edit_post', post_id=post_id))
        
        # Оновлюємо пост
        posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$set': {
                'title': title,
                'content': content,
                'updated_at': datetime.utcnow()
            }}
        )
        
        flash('Пост успішно оновлено')
        return redirect(url_for('home'))
    
    return render_template('edit_post.html', post=post)

# Видалення посту
@app.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = posts_collection.find_one({'_id': ObjectId(post_id)})
    
    if not post:
        flash('Пост не знайдено')
        return redirect(url_for('home'))
    
    if str(post['author_id']) != session['user_id']:
        flash('Ви не маєте прав на видалення цього посту')
        return redirect(url_for('home'))
    
    # Видаляємо пост
    posts_collection.delete_one({'_id': ObjectId(post_id)})
    
    flash('Пост успішно видалено')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)