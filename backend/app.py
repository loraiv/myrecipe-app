from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)

# Configure app
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'recipe_pics'), exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profile_picture = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    recipes = db.relationship('Recipe', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    cooking_time = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='recipe', lazy=True)
    favorites = db.relationship('Favorite', backref='recipe', lazy=True)

    @property
    def average_rating(self):
        if not self.comments:
            return None
        return sum(comment.rating for comment in self.comments) / len(self.comments)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.args.get('q', '').strip()
    sort = request.args.get('sort', '')
    recipes_query = Recipe.query
    if query:
        recipes_query = recipes_query.join(User).filter(
            (Recipe.title.ilike(f'%{query}%')) |
            (Recipe.description.ilike(f'%{query}%')) |
            (Recipe.ingredients.ilike(f'%{query}%')) |
            (User.username.ilike(f'%{query}%'))
        )
    if sort == 'rating':
        recipes = sorted(recipes_query.all(), key=lambda r: r.average_rating or 0, reverse=True)
    else:
        recipes = recipes_query.order_by(Recipe.id.desc()).all()
    return render_template('index.html', recipes=recipes, search_query=query, sort=sort)

@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if request.method == 'POST' and current_user.is_authenticated:
        if 'delete_recipe' in request.form and recipe.author == current_user:
            db.session.delete(recipe)
            db.session.commit()
            flash('Рецептата е изтрита!')
            return redirect(url_for('profile', username=current_user.username))
        content = request.form.get('content')
        rating = request.form.get('rating', type=int)
        if content and rating:
            comment = Comment(content=content, rating=rating, user_id=current_user.id, recipe_id=recipe.id)
            db.session.add(comment)
            db.session.commit()
            flash('Коментарът е добавен!')
            return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    comments = Comment.query.filter_by(recipe_id=recipe.id).order_by(Comment.id.desc()).all()
    return render_template('recipe_detail.html', recipe=recipe, comments=comments)

@app.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def favorite_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if not Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe.id).first():
        fav = Favorite(user_id=current_user.id, recipe_id=recipe.id)
        db.session.add(fav)
        db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/unfavorite/<int:recipe_id>', methods=['POST'])
@login_required
def unfavorite_recipe(recipe_id):
    fav = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        cooking_time = request.form.get('cooking_time', type=int)
        image = request.files.get('image')
        filename = None
        if image and image.filename:
            filename = secure_filename(str(uuid.uuid4()) + '_' + image.filename)
            image_path = os.path.join(app.static_folder, 'recipe_images')
            os.makedirs(image_path, exist_ok=True)
            image.save(os.path.join(image_path, filename))
        new_recipe = Recipe(
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            image=filename,
            user_id=current_user.id,
            cooking_time=cooking_time
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash('Рецептата е добавена!')
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        abort(403)
    if request.method == 'POST':
        recipe.title = request.form['title']
        recipe.description = request.form['description']
        recipe.ingredients = request.form['ingredients']
        recipe.instructions = request.form['instructions']
        recipe.cooking_time = request.form.get('cooking_time', type=int)
        image = request.files.get('image')
        if image and image.filename:
            filename = secure_filename(str(uuid.uuid4()) + '_' + image.filename)
            image_path = os.path.join(app.static_folder, 'recipe_images')
            os.makedirs(image_path, exist_ok=True)
            image.save(os.path.join(image_path, filename))
            recipe.image = filename
        db.session.commit()
        flash('Рецептата е обновена!')
        return redirect(url_for('recipe_detail', recipe_id=recipe.id))
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete/<int:recipe_id>', methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.author != current_user:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash('Рецептата е изтрита!')
    return redirect(url_for('profile', username=current_user.username))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        profile_picture = request.files.get('profile_picture')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('signup'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.')
            return redirect(url_for('signup'))
        if '@' not in email:
            flash('Please enter a valid email address.')
            return redirect(url_for('signup'))
        filename = None
        if profile_picture and profile_picture.filename:
            filename = secure_filename(str(uuid.uuid4()) + '_' + profile_picture.filename)
            profile_pic_path = os.path.join(app.static_folder, 'profile_pics')
            os.makedirs(profile_pic_path, exist_ok=True)
            profile_picture.save(os.path.join(profile_pic_path, filename))
        new_user = User(username=username, email=email, profile_picture=filename)
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

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    recipes = user.recipes
    favorites = Recipe.query.join(Favorite).filter(Favorite.user_id == user.id).all()
    return render_template('profile.html', user=user, recipes=recipes, favorites=favorites)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        profile_picture = request.files.get('profile_picture')
        if profile_picture and profile_picture.filename:
            filename = secure_filename(str(uuid.uuid4()) + '_' + profile_picture.filename)
            profile_pic_path = os.path.join(app.static_folder, 'profile_pics')
            os.makedirs(profile_pic_path, exist_ok=True)
            profile_picture.save(os.path.join(profile_pic_path, filename))
            current_user.profile_picture = filename
            db.session.commit()
            flash('Профилната снимка е обновена!')
            return redirect(url_for('profile', username=current_user.username))
    return render_template('edit_profile.html', user=current_user)

@app.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
    if request.method == 'POST':
        user = User.query.get(current_user.id)
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('Акаунтът е изтрит!')
        return redirect(url_for('signup'))
    return render_template('delete_account.html')

@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    recipes = Recipe.query.all()
    comments = Comment.query.all()
    return render_template('admin.html', users=users, recipes=recipes, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
