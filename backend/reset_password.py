from app.database import get_db_connection
from werkzeug.security import generate_password_hash

def reset_password(username, new_password):
    conn = get_db_connection()
    try:
        # Generate new password hash
        password_hash = generate_password_hash(new_password)
        
        # Update the user's password
        cursor = conn.execute(
            'UPDATE users SET password_hash = ? WHERE username = ?',
            (password_hash, username)
        )
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Password successfully reset for user: {username}")
        else:
            print(f"User not found: {username}")
            
    except Exception as e:
        print(f"Error resetting password: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    username = input("Enter username: ")
    new_password = input("Enter new password: ")
    
    if len(new_password) < 6:
        print("Password must be at least 6 characters")
    else:
        reset_password(username, new_password) 