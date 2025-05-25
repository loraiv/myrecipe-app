from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from .auth import auth as auth_blueprint
    from .recipes import recipes as recipes_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(recipes_blueprint)
    
    with app.app_context():
        # Import models here to avoid circular imports
        from .models import User, Recipe
        # Create all database tables
        db.drop_all()  # Drop existing tables
        db.create_all()  # Create new tables
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    return app
