from flask import Blueprint, request, jsonify
from .models import Recipe
from . import db

main = Blueprint('main', __name__)

@main.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([{
        'id': r.id,
        'title': r.title,
        'author': r.author
    } for r in recipes])

@main.route('/recipes', methods=['POST'])
def create_recipe():
    data = request.json
    new_recipe = Recipe(
        title=data['title'],
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        author=data['author']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({'message': 'Recipe created'}), 201
