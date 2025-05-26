from app.database import get_db_connection, init_db
from seed_categories import seed_categories

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

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Database initialized!")
    
    print("\nChecking tables...")
    check_tables()
    
    print("Seeding categories...")
    seed_categories()
    print("Categories seeded!") 