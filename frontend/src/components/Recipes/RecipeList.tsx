import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface Category {
  id: number;
  name: string;
}

interface Recipe {
  id: number;
  title: string;
  description: string;
  author: string;
  user_id: number;
  categories: Category[];
}

const RecipeList: React.FC = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [currentUserId, setCurrentUserId] = useState<number | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Get current user from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      setCurrentUserId(user.id);
    }
  }, []);

  const fetchRecipes = async () => {
    try {
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;

      const response = await fetch('http://localhost:5000/recipes', {
        headers: {
          'Authorization': `Bearer ${user?.token}`
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setRecipes(data);
      } else if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } catch (error) {
      console.error('Error fetching recipes:', error);
    }
  };

  useEffect(() => {
    fetchRecipes();
  }, []);

  const handleDelete = async (recipeId: number) => {
    if (!window.confirm('Are you sure you want to delete this recipe?')) {
      return;
    }

    try {
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;

      const response = await fetch(`http://localhost:5000/recipes/${recipeId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${user?.token}`
        },
        credentials: 'include'
      });

      if (response.ok) {
        fetchRecipes(); // Refresh the list after deletion
      } else if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('user');
        navigate('/login');
      } else if (response.status === 403) {
        alert('You do not have permission to delete this recipe');
      } else {
        alert('Failed to delete recipe');
      }
    } catch (error) {
      console.error('Error deleting recipe:', error);
      alert('An error occurred while deleting the recipe');
    }
  };

  return (
    <div className="recipe-list">
      <h2>Recipes</h2>
      <Link to="/recipes/new" className="create-recipe-btn">Create New Recipe</Link>
      <div className="recipe-grid">
        {recipes.map((recipe) => (
          <div key={recipe.id} className="recipe-card">
            <h3>{recipe.title}</h3>
            <p>{recipe.description}</p>
            <p className="author">By: {recipe.author}</p>
            <div className="categories">
              {recipe.categories.map(category => (
                <span key={category.id} className="category-tag">
                  {category.name}
                </span>
              ))}
            </div>
            <div className="recipe-actions">
              <Link to={`/recipes/${recipe.id}`} className="view-recipe-btn">
                View Recipe
              </Link>
              {currentUserId === recipe.user_id && (
                <>
                  <Link to={`/recipes/${recipe.id}/edit`} className="edit-recipe-btn">
                    Edit
                  </Link>
                  <button 
                    onClick={() => handleDelete(recipe.id)}
                    className="delete-recipe-btn"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecipeList; 