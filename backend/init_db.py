from app.database import get_db_connection, init_db
from app import create_app, db
from app.models import User, Category
import os

def check_tables():
    conn = get_db_connection()
    try:
        # Check users table
        users = conn.execute("SELECT * FROM users").fetchall()
        print(f"Users table exists with {len(users)} records")
        
        # Check if tables exist
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('users', 'recipes', 'categories', 'recipe_categories')
        """).fetchall()
        print("Existing tables:", [table['name'] for table in tables])
        
    except Exception as e:
        print(f"Error checking tables: {str(e)}")
    finally:
        conn.close()

def init_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Create default categories
        default_categories = [
            'Основно ястие',
            'Десерт',
            'Салата',
            'Супа',
            'Вегетарианско',
            'Бързо',
            'Здравословно',
            'Международна кухня',
            'Dinner',
            'Lunch',
            'Breakfast',
            'Snack',
            'Appetizer',
            'Beverage'
        ]
        for name in default_categories:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name))
        db.session.commit()
        print("Default categories created!")

if __name__ == '__main__':
    db_path = os.path.join(os.path.dirname(__file__), 'recipes.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database at {db_path}")
    print("Initializing database...")
    init_database()
    
    print("\nChecking tables...")
    check_tables() 