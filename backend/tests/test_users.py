import pytest
from app import app, db, User
from flask import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_user_password_hashing():
    user = User(username='user1', email='user1@example.com')
    user.set_password('secret')
    assert user.check_password('secret')
    assert not user.check_password('wrong')

def test_user_registration(client):
    with app.app_context():
        user = User(username='newuser', email='new@example.com')
        user.set_password('newpass')
        db.session.add(user)
        db.session.commit()
        found = User.query.filter_by(username='newuser').first()
        assert found is not None
        assert found.email == 'new@example.com'

def test_duplicate_user_registration(client):
    with app.app_context():
        user1 = User(username='dupe', email='dupe@example.com')
        user1.set_password('pass')
        db.session.add(user1)
        db.session.commit()
        user2 = User(username='dupe', email='dupe@example.com')
        user2.set_password('pass')
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit() 