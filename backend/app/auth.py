from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User
from .database import get_db_connection
import sqlite3

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'authenticated': current_user.is_authenticated})
    return render_template('index.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    # Get data from either form or JSON
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
    else:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

    if not username or not email or not password:
        message = 'Please fill out all fields'
        return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)

    try:
        conn = get_db_connection()
        # Check for existing username
        if conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            message = 'Username already exists'
            return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)

        # Check for existing email
        if conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone():
            message = 'Email already exists'
            return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)

        if len(password) < 6:
            message = 'Password must be at least 6 characters'
            return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)

        if '@' not in email:
            message = 'Please enter a valid email address'
            return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)

        password_hash = generate_password_hash(password)
        cursor = conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (username, email, password_hash))
        user_id = cursor.lastrowid
        conn.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': 'Registration successful! Please log in.'})
        else:
            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))

    except sqlite3.IntegrityError as e:
        message = 'Registration failed. Username or email already exists.'
        return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)
    except sqlite3.OperationalError as e:
        message = 'Registration failed. Please try again.'
        return jsonify({'error': message}) if request.is_json else render_template('signup.html', error=message)
    finally:
        conn.close()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # Get data from either form or JSON
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    print(f"Login attempt for username: {username}")  # Debug log

    if not username or not password:
        message = 'Please fill out all fields'
        return jsonify({'error': message, 'success': False}), 400

    try:
        # Get database connection and check user directly
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        print(f"User found in database: {user_data is not None}")  # Debug log
        
        if user_data:
            user = User(user_data['id'], user_data['username'], user_data['email'], user_data['password_hash'])
            print(f"Password check result: {user.check_password(password)}")  # Debug log
            
            if user.check_password(password):
                login_user(user, remember=True)
                print("Login successful")  # Debug log
                
                if request.is_json:
                    response = jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email
                        }
                    })
                    response.headers.add('Access-Control-Allow-Credentials', 'true')
                    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin'))
                    return response
                    
                return redirect(url_for('auth.index'))
            
        message = 'Invalid username or password'
        print(f"Login failed: {message}")  # Debug log
        return jsonify({'error': message, 'success': False}), 401

    except Exception as e:
        print(f"Error during login: {str(e)}")  # Debug log
        message = 'Login failed. Please try again.'
        return jsonify({'error': message, 'success': False}), 500
    finally:
        conn.close()

@auth.route('/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        })
    return jsonify({'authenticated': False}), 401

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True})
    return redirect(url_for('auth.index')) 