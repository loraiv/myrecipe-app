from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
import os
from app.models import db, User, Recipe, Comment
import uuid
from werkzeug.utils import secure_filename

# Initialize extensions
# db = SQLAlchemy()  # Already imported from app.models
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    CORS(app)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'recipes.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'supersecretkey123'
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        recipes = Recipe.query.order_by(Recipe.id.desc()).all()
        return render_template('index.html', recipes=recipes)

    @app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
    def recipe_detail(recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        if request.method == 'POST' and current_user.is_authenticated:
            content = request.form['content']
            rating = int(request.form['rating'])
            comment = Comment(content=content, rating=rating, user_id=current_user.id, recipe_id=recipe.id)
            db.session.add(comment)
            db.session.commit()
            flash('Коментарът е добавен!')
            return redirect(url_for('recipe_detail', recipe_id=recipe.id))
        comments = Comment.query.filter_by(recipe_id=recipe.id).order_by(Comment.created_at.desc()).all()
        return render_template('recipe_detail.html', recipe=recipe, comments=comments)

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_recipe():
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            ingredients = request.form['ingredients']
            instructions = request.form['instructions']
            image = request.files.get('image')
            filename = None
            if image and image.filename:
                filename = secure_filename(str(uuid.uuid4()) + '_' + image.filename)
                image_path = os.path.join(app.static_folder, 'recipe_images')
                os.makedirs(image_path, exist_ok=True)
                image.save(os.path.join(image_path, filename))
            new_recipe = Recipe(title=title, description=description, ingredients=ingredients, instructions=instructions, image=filename, user_id=current_user.id)
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

    @app.route('/delete/<int:recipe_id>')
    @login_required
    def delete_recipe(recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        if recipe.author != current_user:
            abort(403)
        db.session.delete(recipe)
        db.session.commit()
        flash('Рецептата е изтрита!')
        return redirect(url_for('index'))

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
        return render_template('profile.html', user=user, recipes=recipes)

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
