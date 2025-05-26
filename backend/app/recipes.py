from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Recipe, Category
from .database import get_db_connection

recipes = Blueprint('recipes', __name__)

@recipes.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.get_all()
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
    category.save()
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
        if user_id:
            recipes = Recipe.get_by_user_id(user_id)
        else:
            recipes = Recipe.get_all()
            
        # Get all usernames in one query for efficiency
        conn = get_db_connection()
        user_map = {}
        users = conn.execute('SELECT id, username FROM users').fetchall()
        for user in users:
            user_map[user['id']] = user['username']
        conn.close()
            
        return jsonify([{
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'created_at': recipe.created_at,
            'updated_at': recipe.updated_at,
            'user_id': recipe.user_id,
            'author': user_map.get(recipe.user_id, 'Unknown'),
            'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
        } for recipe in recipes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipes.route('/recipes', methods=['POST'])
@login_required
def create_recipe():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'description', 'ingredients', 'instructions')):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO recipes (title, description, ingredients, instructions, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['title'], data['description'], data['ingredients'], 
              data['instructions'], current_user.id))
        
        recipe_id = cursor.lastrowid
        
        # Handle categories if provided
        if 'categories' in data and isinstance(data['categories'], list):
            for category_id in data['categories']:
                cursor.execute('''
                    INSERT INTO recipe_categories (recipe_id, category_id)
                    VALUES (?, ?)
                ''', (recipe_id, category_id))
        
        conn.commit()
        
        # Get the created recipe
        recipe = Recipe.get(recipe_id)
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
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@recipes.route('/recipes/<int:recipe_id>', methods=['PUT'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.get(recipe_id)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404
        
    if recipe.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    conn = get_db_connection()
    try:
        # Update the recipe
        conn.execute('''
            UPDATE recipes 
            SET title = ?, description = ?, ingredients = ?, instructions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('title', recipe.title),
            data.get('description', recipe.description),
            data.get('ingredients', recipe.ingredients),
            data.get('instructions', recipe.instructions),
            recipe_id
        ))
        
        # Update categories if provided
        if 'category_ids' in data:
            # Remove existing categories
            conn.execute('DELETE FROM recipe_categories WHERE recipe_id = ?', (recipe_id,))
            
            # Add new categories
            for category_id in data['category_ids']:
                conn.execute('''
                    INSERT INTO recipe_categories (recipe_id, category_id)
                    VALUES (?, ?)
                ''', (recipe_id, category_id))
        
        conn.commit()
        
        # Get updated recipe
        updated_recipe = Recipe.get(recipe_id)
        return jsonify({
            'message': 'Recipe updated successfully',
            'recipe': {
                'id': updated_recipe.id,
                'title': updated_recipe.title,
                'description': updated_recipe.description,
                'ingredients': updated_recipe.ingredients,
                'instructions': updated_recipe.instructions,
                'created_at': updated_recipe.created_at,
                'updated_at': updated_recipe.updated_at,
                'user_id': updated_recipe.user_id,
                'categories': [{'id': c.id, 'name': c.name} for c in updated_recipe.categories]
            }
        })
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@recipes.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.get(recipe_id)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404
        
    if recipe.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db_connection()
    try:
        # Delete recipe categories first
        conn.execute('DELETE FROM recipe_categories WHERE recipe_id = ?', (recipe_id,))
        # Delete the recipe
        conn.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
        conn.commit()
        return jsonify({'message': 'Recipe deleted successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@recipes.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.get(recipe_id)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404
        
    # Get the username of the recipe author
    conn = get_db_connection()
    user = conn.execute('SELECT username FROM users WHERE id = ?', (recipe.user_id,)).fetchone()
    conn.close()
    
    return jsonify({
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'created_at': recipe.created_at,
        'updated_at': recipe.updated_at,
        'user_id': recipe.user_id,
        'author': user['username'] if user else 'Unknown',
        'categories': [{'id': c.id, 'name': c.name} for c in recipe.categories]
    }) 