# Recipe App

A modern web application for sharing, searching, and managing cooking recipes. Users can register, add and edit their own recipes, upload images, comment and rate others' recipes, and mark favorites. The app features an admin panel, REST API, unit tests, and is ready for cloud deployment.

## Features
- User registration and login
- Profile picture upload
- Add, edit, and delete recipes with images
- Comment and rate recipes
- Mark recipes as favorites
- Search and filter recipes
- Admin panel for managing users, recipes, and comments
- REST API for recipes (CRUD)
- Unit tests for main components
- Cloud deployment ready (Railway, Docker, etc.)

## Technologies
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-CORS
- **Frontend:** Jinja2 templates, Bootstrap 5, HTML5, CSS3
- **Database:** SQLite (easy to switch to PostgreSQL/MySQL)
- **Testing:** pytest, pytest-flask
- **DevOps:** Railway, Procfile, Docker (optional), GitHub Actions (optional)


## Setup & Run Locally
1. Clone the repo and enter the backend directory:
   ```bash
   git clone <your-repo-url>
   cd recipe-app/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python init_db.py
   ```
5. Run the app:
   ```bash
   python app.py
   ```
6. Open [http://localhost:5000](http://localhost:5000) in your browser.

## REST API Examples
- **GET /api/recipes** — List all recipes
- **GET /api/recipes/<id>** — Get recipe details
- **POST /api/recipes** — Create a recipe (JSON)
- **PUT /api/recipes/<id>** — Update a recipe
- **DELETE /api/recipes/<id>** — Delete a recipe

Example POST body:
```json
{
  "title": "Omelette",
  "description": "Quick omelette",
  "ingredients": "Eggs\nCheese",
  "instructions": "Beat eggs. Cook with cheese.",
  "cooking_time": 10,
  "user_id": 1
}
```

## Testing
- Run all tests with:
  ```bash
  pytest
  ```
- Tests cover: user registration, password hashing, recipe CRUD, comments, API endpoints, and relationships.

## Deployment
- Ready for Railway, Heroku, Render, or PythonAnywhere.
- Includes `Procfile` and Dockerfile for easy deployment.
- Set environment variables (e.g., `SECRET_KEY`) in your cloud provider.

## Future Improvements
- User and comment REST API endpoints
- OAuth/Google/Facebook login
- Full CI/CD pipeline
- PostgreSQL for production
- Swagger/OpenAPI documentation
- Mobile app integration

## Credits
- Developed by [Your Name]
- Inspired by the open-source community

---
