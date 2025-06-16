from app import app, db
from app import User
import os

def check_tables():
    """Check if all required tables exist and have the correct structure."""
    try:
        # Check users table
        users = User.query.all()
        print(f"Users table exists with {len(users)} records")
        
        # Check recipes table
        recipes = db.session.execute("SELECT * FROM recipes").fetchall()
        print(f"Recipes table exists with {len(recipes)} records")
        
        # Check comments table
        comments = db.session.execute("SELECT * FROM comments").fetchall()
        print(f"Comments table exists with {len(comments)} records")
        
        # Check favorites table
        favorites = db.session.execute("SELECT * FROM favorites").fetchall()
        print(f"Favorites table exists with {len(favorites)} records")
        
    except Exception as e:
        print(f"Error checking tables: {str(e)}")

def init_database():
    """Initialize the database with required tables."""
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        print("Dropped all existing tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create test user
        test_user = User(
            username='test',
            email='test@example.com'
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        
        # Commit changes
        db.session.commit()
        print("Created default users (admin and test)")

if __name__ == '__main__':
    # Remove existing database if it exists
    db_path = os.path.join(os.path.dirname(__file__), 'recipes.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")
    
    print("Initializing database...")
    init_database()
    
    print("\nChecking tables...")
    check_tables() 