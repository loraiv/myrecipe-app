from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
import os
from app.models import User

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'recipes.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecretkey123'
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Models
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(128))
        
        def set_password(self, password):
            from werkzeug.security import generate_password_hash
            self.password_hash = generate_password_hash(password)
            
        def check_password(self, password):
            from werkzeug.security import check_password_hash
            return check_password_hash(self.password_hash, password)
    
    class Recipe(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text, nullable=False)
    
    # Routes
    @app.route('/')
    def index():
        recipes = Recipe.query.all()
        return render_template('index.html', recipes=recipes)
    
    @app.route('/add', methods=['GET', 'POST'])
    def add_recipe():
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            new_recipe = Recipe(title=title, description=description)
            db.session.add(new_recipe)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('add_recipe.html')
    
    @app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
    def edit_recipe(recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        if request.method == 'POST':
            recipe.title = request.form['title']
            recipe.description = request.form['description']
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('edit_recipe.html', recipe=recipe)
    
    @app.route('/delete/<int:recipe_id>')
    def delete_recipe(recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        return redirect(url_for('index'))
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
    
            if User.query.filter_by(username=username).first():
                flash('Username already exists.')
                return redirect(url_for('signup'))
            if len(password) < 6:
                flash('Password must be at least 6 characters.')
                return redirect(url_for('signup'))
            if '@' not in email:
                flash('Please enter a valid email address.')
                return redirect(url_for('signup'))
    
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
    
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
    
        return render_template('signup.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
    
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.')
                return redirect(url_for('login'))
    
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
