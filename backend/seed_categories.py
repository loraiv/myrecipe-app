from app import create_app, db
from app.models import Category

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

    app = create_app()
    with app.app_context():
        for category_data in categories:
            # Check if category already exists
            existing = Category.query.filter_by(name=category_data['name']).first()
            if not existing:
                category = Category(**category_data)
                db.session.add(category)
        
        db.session.commit()
        print("Categories seeded successfully!")

if __name__ == '__main__':
    seed_categories() 