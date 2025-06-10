from flask import Blueprint, request, redirect, url_for, render_template_string, current_app
from werkzeug.security import generate_password_hash
from app.extensions import mongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    users_collection = mongo.db.users

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if users_collection.find_one({'email': email}):
            return "Користувач з таким email вже існує. <a href='/register'>Спробувати ще раз</a>"

        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': password,
            'role': 'user'
        })

        return redirect(url_for('main.home'))

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
