from flask import Blueprint, request, redirect, url_for, flash, render_template_string
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User
from app.extensions import mongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_email(email)
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            flash('Ви успішно увійшли!', 'success')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Невірний email або пароль', 'error')
    
    return """
    <h2>Вхід</h2>
    <form method="POST">
        <div>
            <label>Email:</label><br>
            <input type="email" name="email" required>
        </div>
        <div>
            <label>Пароль:</label><br>
            <input type="password" name="password" required>
        </div>
        <button type="submit">Увійти</button>
    </form>
    <p>Ще не маєте акаунту? <a href="{}">Зареєструватися</a></p>
    <a href="{}">На головну</a>
    """.format(url_for('auth.register'), url_for('main.home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.create(username, email, password)
        if user:
            login_user(user)
            flash('Реєстрація успішна!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Користувач з таким email вже існує', 'error')
    
    return """
    <h2>Реєстрація</h2>
    <form method="POST">
        <div>
            <label>Ім'я користувача:</label><br>
            <input type="text" name="username" required>
        </div>
        <div>
            <label>Email:</label><br>
            <input type="email" name="email" required>
        </div>
        <div>
            <label>Пароль:</label><br>
            <input type="password" name="password" required>
        </div>
        <button type="submit">Зареєструватися</button>
    </form>
    <p>Вже маєте акаунт? <a href="{}">Увійти</a></p>
    <a href="{}">На головну</a>
    """.format(url_for('auth.login'), url_for('main.home'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з акаунту', 'info')
    return redirect(url_for('main.home'))