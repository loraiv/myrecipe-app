from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Recipe, Category, db

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
@login_required
def get_recipes():
    user_id = request.args.get('user_id', type=int)
    if user_id:
        recipes = Recipe.query.filter_by(user_id=user_id).all()
    else:
        recipes = Recipe.query.all()
    
    return jsonify([{
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'user_id': recipe.user_id,
        'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
    } for recipe in recipes])

@recipes.route('/recipes', methods=['POST'])
@login_required
def create_recipe():
    data = request.get_json()
    
    # Create the recipe
    recipe = Recipe(
        title=data['title'],
        description=data['description'],
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        user_id=current_user.id
    )
    
    # Add categories if provided
    if 'category_ids' in data:
        categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
        recipe.categories.extend(categories)
    
    db.session.add(recipe)
    db.session.commit()
    
    return jsonify({
        'message': 'Recipe created successfully',
        'recipe': {
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
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
    
    # Update categories if provided
    if 'category_ids' in data:
        recipe.categories = []
        categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
        recipe.categories.extend(categories)
    
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
        'author': recipe.author.username,
        'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
    }) 