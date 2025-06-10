from flask import Flask, request, redirect, url_for, render_template_string
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from werkzeug.security import generate_password_hash

app = Flask(__name__)

MONGO_URI = 'mongodb+srv://annabasyuk:YR4xMbWSTHp7M1Pq@cluster0.n0doxn9.mongodb.net/blogdb?retryWrites=true&w=majority'
client = MongoClient(MONGO_URI)
db = client.blogdb
users_collection = db.users

# 🌐 Головна
@app.route('/')
def home():
    return "Головна сторінка блогу. <a href='/register'>Реєстрація</a> | <a href='/check_db'>Перевірити БД</a>"

# 🧪 Перевірка підключення
@app.route('/check_db')
def check_db():
    try:
        client.admin.command('ping')
        users_count = users_collection.count_documents({})
        return f"<h1>Підключено ✅</h1><p>Користувачів у базі: {users_count}</p><a href='/'>На головну</a>"
    except ConnectionFailure as e:
        return f"<h1>Помилка ❌</h1><p>{str(e)}</p><a href='/'>На головну</a>"

# 🧾 Реєстрація користувача
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        if users_collection.find_one({'email': email}):
            return "Користувач з таким email вже існує. <a href='/register'>Спробувати ще раз</a>"

        new_user = {
            'username': username,
            'email': email,
            'password': password,
            'role': 'user'  # роль за замовчуванням
        }

        users_collection.insert_one(new_user)
        return redirect(url_for('home'))

    return render_template_string("""
        <h2>Реєстрація</h2>
        <form method="POST">
            <input name="username" placeholder="Ім'я користувача" required><br>
            <input name="email" type="email" placeholder="Email" required><br>
            <input name="password" type="password" placeholder="Пароль" required><br>
            <button type="submit">Зареєструватися</button>
        </form>
        <a href="/">На головну</a>
    """)
    
if __name__ == '__main__':
    app.run(debug=True)
