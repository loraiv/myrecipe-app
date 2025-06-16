import pytest
from app import app, db, User, Recipe, Comment
from flask import json

@pytest.fixture(scope="function")
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            user = User(username='commenter', email='commenter@example.com')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()
            recipe = Recipe(title='Recipe', description='desc', ingredients='ing', instructions='inst', cooking_time=10, user_id=user.id)
            db.session.add(recipe)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_comment(client):
    with app.app_context():
        user = User.query.first()
        recipe = Recipe.query.first()
        comment = Comment(content='Nice!', rating=5, user_id=user.id, recipe_id=recipe.id)
        db.session.add(comment)
        db.session.commit()
        found = Comment.query.filter_by(content='Nice!').first()
        assert found is not None
        assert found.rating == 5
        assert found.recipe_id == recipe.id

def test_recipe_comments_relationship(client):
    with app.app_context():
        user = User.query.first()
        recipe = Recipe.query.first()
        comment1 = Comment(content='Good', rating=4, user_id=user.id, recipe_id=recipe.id)
        comment2 = Comment(content='Great', rating=5, user_id=user.id, recipe_id=recipe.id)
        db.session.add_all([comment1, comment2])
        db.session.commit()
        recipe = Recipe.query.first()
        assert len(recipe.comments) == 2 