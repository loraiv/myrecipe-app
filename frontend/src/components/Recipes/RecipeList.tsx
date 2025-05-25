import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

interface Recipe {
  id: number;
  title: string;
  description: string;
  author: string;
}

const RecipeList: React.FC = () => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  useEffect(() => {
    const fetchRecipes = async () => {
      try {
        const response = await fetch('http://localhost:5000/recipes');
        if (response.ok) {
          const data = await response.json();
          setRecipes(data);
        }
      } catch (error) {
        console.error('Error fetching recipes:', error);
      }
    };

    fetchRecipes();
  }, []);

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
            <Link to={`/recipes/${recipe.id}`} className="view-recipe-btn">
              View Recipe
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecipeList; 