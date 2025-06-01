from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Recipe, Category, db
from datetime import datetime

recipes = Blueprint('recipes', __name__)

@recipes.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description
    } for category in categories])

@recipes.route('/categories', methods=['POST'])
@login_required
def create_category():
    data = request.get_json()
    category = Category(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(category)
    db.session.commit()
    return jsonify({
        'message': 'Category created successfully',
        'category': {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }
    }), 201

@recipes.route('/recipes', methods=['GET'])
def get_recipes():
    user_id = request.args.get('user_id')
    
    try:
        query = Recipe.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        recipes_list = query.all()
            
        return jsonify([{
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'created_at': recipe.created_at,
            'updated_at': recipe.updated_at,
            'user_id': recipe.user_id,
            'author': recipe.author.username,
            'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
        } for recipe in recipes_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipes.route('/recipes', methods=['POST'])
@login_required
def create_recipe():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'description', 'ingredients', 'instructions')):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        recipe = Recipe(
            title=data['title'],
            description=data['description'],
            ingredients=data['ingredients'],
            instructions=data['instructions'],
            user_id=current_user.id
        )
        
        # Handle categories if provided
        if 'categories' in data and isinstance(data['categories'], list):
            categories = Category.query.filter(Category.id.in_(data['categories'])).all()
            recipe.categories = categories
        
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify({
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'created_at': recipe.created_at,
            'updated_at': recipe.updated_at,
            'user_id': recipe.user_id,
            'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes.route('/recipes/<int:recipe_id>', methods=['PUT'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
        
    if recipe.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    try:
        # Update the recipe
        recipe.title = data.get('title', recipe.title)
        recipe.description = data.get('description', recipe.description)
        recipe.ingredients = data.get('ingredients', recipe.ingredients)
        recipe.instructions = data.get('instructions', recipe.instructions)
        recipe.updated_at = datetime.utcnow()
        
        # Update categories if provided
        if 'category_ids' in data:
            categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
            recipe.categories = categories
        
        db.session.commit()
        
        return jsonify({
            'message': 'Recipe updated successfully',
            'recipe': {
                'id': recipe.id,
                'title': recipe.title,
                'description': recipe.description,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'created_at': recipe.created_at,
                'updated_at': recipe.updated_at,
                'user_id': recipe.user_id,
                'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
        
    if recipe.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({'message': 'Recipe deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
        'updated_at': recipe.updated_at,
        'user_id': recipe.user_id,
        'author': recipe.author.username,
        'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
    }) 