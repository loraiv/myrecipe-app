import React from 'react';
import { useParams } from 'react-router-dom';
import CommentSection from '../Comments/CommentSection';
import './Recipe.css';

interface Recipe {
  id: number;
  title: string;
  description: string;
  image_url?: string;
  author: {
    id: number;
    username: string;
  };
  average_rating: number;
  created_at: string;
}

const Recipe: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [recipe, setRecipe] = React.useState<Recipe | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/recipes/${id}`);
        if (response.ok) {
          const data = await response.json();
          setRecipe(data);
        }
      } catch (error) {
        console.error('Failed to fetch recipe:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecipe();
  }, [id]);

  if (isLoading) {
    return <div className="loading">Loading recipe...</div>;
  }

  if (!recipe) {
    return <div className="error">Recipe not found</div>;
  }

  return (
    <div className="recipe-detail">
      <h2>{recipe.title}</h2>
      
      <div className="recipe-meta">
        <span className="author">By: {recipe.author.username}</span>
        <span className="date">
          Posted on: {new Date(recipe.created_at).toLocaleDateString()}
        </span>
        {recipe.average_rating > 0 && (
          <span className="average-rating">
            Average Rating: {recipe.average_rating.toFixed(1)} ★
          </span>
        )}
      </div>

      {recipe.image_url && (
        <div className="recipe-image">
          <img src={recipe.image_url} alt={recipe.title} />
        </div>
      )}

      <div className="recipe-description">
        {recipe.description}
      </div>

      <CommentSection recipeId={recipe.id} />
    </div>
  );
};

export default Recipe; 