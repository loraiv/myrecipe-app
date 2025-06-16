import pytest
from app import app, db, Recipe, User
from flask import json

@pytest.fixture(scope="function")
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test user
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def create_recipe(client, user_id):
    data = {
        'title': 'Test Recipe',
        'description': 'A test recipe',
        'ingredients': 'Eggs\nFlour',
        'instructions': 'Mix\nBake',
        'cooking_time': 30,
        'user_id': user_id
    }
    return client.post('/api/recipes', data=json.dumps(data), content_type='application/json')

def test_create_recipe(client):
    with app.app_context():
        user = User.query.first()
        rv = create_recipe(client, user.id)
        assert rv.status_code == 201
        data = rv.get_json()
        assert 'id' in data

def test_get_recipes(client):
    with app.app_context():
        user = User.query.first()
        create_recipe(client, user.id)
        rv = client.get('/api/recipes')
        assert rv.status_code == 200
        data = rv.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['title'] == 'Test Recipe'

def test_get_single_recipe(client):
    with app.app_context():
        user = User.query.first()
        resp = create_recipe(client, user.id)
        recipe_id = resp.get_json()['id']
        rv = client.get(f'/api/recipes/{recipe_id}')
        assert rv.status_code == 200
        data = rv.get_json()
        assert data['title'] == 'Test Recipe'

def test_update_recipe(client):
    with app.app_context():
        user = User.query.first()
        resp = create_recipe(client, user.id)
        recipe_id = resp.get_json()['id']
        update_data = {'title': 'Updated Recipe'}
        rv = client.put(f'/api/recipes/{recipe_id}', data=json.dumps(update_data), content_type='application/json')
        assert rv.status_code == 200
        rv = client.get(f'/api/recipes/{recipe_id}')
        data = rv.get_json()
        assert data['title'] == 'Updated Recipe'

def test_delete_recipe(client):
    with app.app_context():
        user = User.query.first()
        resp = create_recipe(client, user.id)
        recipe_id = resp.get_json()['id']
        rv = client.delete(f'/api/recipes/{recipe_id}')
        assert rv.status_code == 200
        rv = client.get(f'/api/recipes/{recipe_id}')
        assert rv.status_code == 404 