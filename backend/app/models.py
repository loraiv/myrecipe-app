# app/models.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from .database import get_db_connection
import sqlite3

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if user is None:
                return None
            return User(user['id'], user['username'], user['email'], user['password_hash'])
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user is None:
                return None
            return User(user['id'], user['username'], user['email'], user['password_hash'])
        except sqlite3.OperationalError:
            return None
        finally:
            conn.close()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Recipe:
    def __init__(self, id, title, description, ingredients, instructions, created_at, updated_at, user_id, categories=None):
        self.id = id
        self.title = title
        self.description = description
        self.ingredients = ingredients
        self.instructions = instructions
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_id = user_id
        self.categories = categories if categories else []

    @staticmethod
    def get_all():
        conn = get_db_connection()
        recipes = conn.execute('SELECT * FROM recipes').fetchall()
        result = []
        for recipe in recipes:
            categories = get_recipe_categories(recipe['id'])
            result.append(Recipe(
                recipe['id'], recipe['title'], recipe['description'],
                recipe['ingredients'], recipe['instructions'],
                recipe['created_at'], recipe['updated_at'],
                recipe['user_id'], categories
            ))
        conn.close()
        return result

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_db_connection()
        recipes = conn.execute('SELECT * FROM recipes WHERE user_id = ?', (user_id,)).fetchall()
        result = []
        for recipe in recipes:
            categories = get_recipe_categories(recipe['id'])
            result.append(Recipe(
                recipe['id'], recipe['title'], recipe['description'],
                recipe['ingredients'], recipe['instructions'],
                recipe['created_at'], recipe['updated_at'],
                recipe['user_id'], categories
            ))
        conn.close()
        return result

    @staticmethod
    def get(recipe_id):
        conn = get_db_connection()
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        if recipe is None:
            conn.close()
            return None
        categories = get_recipe_categories(recipe['id'])
        conn.close()
        return Recipe(
            recipe['id'], recipe['title'], recipe['description'],
            recipe['ingredients'], recipe['instructions'],
            recipe['created_at'], recipe['updated_at'],
            recipe['user_id'], categories
        )

class Category:
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_all():
        conn = get_db_connection()
        categories = conn.execute('SELECT * FROM categories').fetchall()
        result = [Category(cat['id'], cat['name'], cat['description']) for cat in categories]
        conn.close()
        return result

def get_recipe_categories(recipe_id):
    conn = get_db_connection()
    categories = conn.execute('''
        SELECT c.* FROM categories c
        JOIN recipe_categories rc ON c.id = rc.category_id
        WHERE rc.recipe_id = ?
    ''', (recipe_id,)).fetchall()
    conn.close()
    return [Category(cat['id'], cat['name'], cat['description']) for cat in categories]
