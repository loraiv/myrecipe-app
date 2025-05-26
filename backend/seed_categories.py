from app.database import get_db_connection

def seed_categories():
    categories = [
        {'name': 'Breakfast', 'description': 'Morning meals and brunch recipes'},
        {'name': 'Lunch', 'description': 'Midday meals and light dishes'},
        {'name': 'Dinner', 'description': 'Evening meals and main courses'},
        {'name': 'Dessert', 'description': 'Sweet treats and desserts'},
        {'name': 'Vegetarian', 'description': 'Meat-free recipes'},
        {'name': 'Vegan', 'description': 'Plant-based recipes without animal products'},
        {'name': 'Gluten-Free', 'description': 'Recipes without gluten'},
        {'name': 'Quick & Easy', 'description': 'Recipes that take 30 minutes or less'},
        {'name': 'Healthy', 'description': 'Nutritious and balanced meals'},
        {'name': 'Snacks', 'description': 'Light bites and appetizers'}
    ]

    conn = get_db_connection()
    for category in categories:
        try:
            conn.execute(
                'INSERT INTO categories (name, description) VALUES (?, ?)',
                (category['name'], category['description'])
            )
        except:
            # Skip if category already exists
            pass
    
    conn.commit()
    conn.close()
    print("Categories seeded successfully!")

if __name__ == '__main__':
    seed_categories() 