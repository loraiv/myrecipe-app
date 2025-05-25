from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Recipe, db

recipes = Blueprint('recipes', __name__)

@recipes.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([{
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'created_at': recipe.created_at,
        'author': recipe.author.username
    } for recipe in recipes])

@recipes.route('/recipes', methods=['POST'])
@login_required
def create_recipe():
    data = request.get_json()
    recipe = Recipe(
        title=data['title'],
        description=data['description'],
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        user_id=current_user.id
    )
    
    db.session.add(recipe)
    db.session.commit()
    
    return jsonify({
        'message': 'Recipe created successfully',
        'recipe': {
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description
        }
    }), 201

@recipes.route('/recipes/<int:recipe_id>', methods=['PUT'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    if recipe.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    recipe.title = data.get('title', recipe.title)
    recipe.description = data.get('description', recipe.description)
    recipe.ingredients = data.get('ingredients', recipe.ingredients)
    recipe.instructions = data.get('instructions', recipe.instructions)
    
    db.session.commit()
    
    return jsonify({'message': 'Recipe updated successfully'})

@recipes.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    if recipe.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(recipe)
    db.session.commit()
    
    return jsonify({'message': 'Recipe deleted successfully'})

@recipes.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify({
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'created_at': recipe.created_at,
        'author': recipe.author.username
    }) 