import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

interface RecipeFormData {
  title: string;
  description: string;
  ingredients: string;
  instructions: string;
}

const RecipeForm: React.FC = () => {
  const [formData, setFormData] = useState<RecipeFormData>({
    title: '',
    description: '',
    ingredients: '',
    instructions: '',
  });

  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id;

  useEffect(() => {
    if (isEditing) {
      fetchRecipe();
    }
  }, [id]);

  const fetchRecipe = async () => {
    try {
      const response = await fetch(`http://localhost:5000/recipes/${id}`);
      if (response.ok) {
        const data = await response.json();
        setFormData(data);
      }
    } catch (error) {
      console.error('Error fetching recipe:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const url = isEditing
        ? `http://localhost:5000/recipes/${id}`
        : 'http://localhost:5000/recipes';
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        navigate('/recipes');
      }
    } catch (error) {
      console.error('Error saving recipe:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="recipe-form">
      <h2>{isEditing ? 'Edit Recipe' : 'Create New Recipe'}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Title:</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Ingredients:</label>
          <textarea
            name="ingredients"
            value={formData.ingredients}
            onChange={handleChange}
            required
            placeholder="Enter ingredients, one per line"
          />
        </div>
        <div className="form-group">
          <label>Instructions:</label>
          <textarea
            name="instructions"
            value={formData.instructions}
            onChange={handleChange}
            required
            placeholder="Enter step-by-step instructions"
          />
        </div>
        <button type="submit">{isEditing ? 'Update Recipe' : 'Create Recipe'}</button>
      </form>
    </div>
  );
};

export default RecipeForm; 