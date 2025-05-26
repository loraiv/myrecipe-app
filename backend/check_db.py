from app.database import get_db_connection

def check_users():
    conn = get_db_connection()
    try:
        users = conn.execute('SELECT id, username, email, password_hash FROM users').fetchall()
        print("\nUsers in database:")
        for user in users:
            print(f"ID: {user['id']}, Username: {user['username']}, Email: {user['email']}")
            print(f"Password hash: {user['password_hash'][:20]}...")  # Only show start of hash for security
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("Checking database contents...")
    check_users() 