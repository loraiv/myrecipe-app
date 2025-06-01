import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';

interface Category {
  id: number;
  name: string;
  description?: string;
}

interface RecipeFormData {
  title: string;
  description: string;
  ingredients: string;
  instructions: string;
  category_ids: number[];
  user_id?: number;
  author?: string;
}

const RecipeForm: React.FC = () => {
  const [formData, setFormData] = useState<RecipeFormData>({
    title: '',
    description: '',
    ingredients: '',
    instructions: '',
    category_ids: []
  });

  const [categories, setCategories] = useState<Category[]>([]);
  const [isOwner, setIsOwner] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditing = !!id && window.location.pathname.includes('/edit');
  const isViewing = !!id && !window.location.pathname.includes('/edit');

  useEffect(() => {
    console.log('Component mounted, fetching categories...');
    fetchCategories();
    if (id) {
      fetchRecipe();
    }
  }, [id]);

  const fetchCategories = async () => {
    try {
      console.log('Making request to fetch categories...');
      const response = await fetch('http://localhost:5000/categories');
      if (response.ok) {
        const data = await response.json();
        console.log('Fetched categories from backend:', data);
        if (Array.isArray(data)) {
          setCategories(data);
        } else {
          console.error('Categories data is not an array:', data);
        }
      } else {
        console.error('Failed to fetch categories:', response.status);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchRecipe = async () => {
    setIsLoading(true);
    try {
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;

      const response = await fetch(`http://localhost:5000/recipes/${id}`, {
        headers: {
          'Authorization': `Bearer ${user?.token}`
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Fetched recipe data:', data);
        setFormData({
          title: data.title || '',
          description: data.description || '',
          ingredients: data.ingredients || '',
          instructions: data.instructions || '',
          category_ids: data.categories ? data.categories.map((c: Category) => c.id) : [],
          user_id: data.user_id,
          author: data.author
        });
        setIsOwner(user?.id === data.user_id);
      } else if (response.status === 404) {
        console.error('Recipe not found');
        navigate('/recipes');
      } else {
        console.error('Error fetching recipe:', response.status);
      }
    } catch (error) {
      console.error('Error fetching recipe:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      alert('Please log in to create or edit recipes');
      navigate('/login');
      return;
    }

    const user = JSON.parse(userStr);

    try {
      const url = isEditing
        ? `http://localhost:5000/recipes/${id}`
        : 'http://localhost:5000/recipes';
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        navigate('/recipes');
      } else if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('user');
        navigate('/login');
      } else {
        alert('Error saving recipe');
      }
    } catch (error) {
      console.error('Error saving recipe:', error);
      alert('Error saving recipe');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name === 'category_ids' && e.target instanceof HTMLSelectElement) {
      const selectedOptions = Array.from(e.target.selectedOptions, option => parseInt(option.value));
      console.log('Selected category IDs:', selectedOptions);
      setFormData(prev => ({
        ...prev,
        category_ids: selectedOptions
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  // Show read-only view for viewing mode
  if (isViewing) {
    return (
      <div className="recipe-form">
        <h2>{formData.title}</h2>
        <div className="recipe-content">
          <p className="author">
            <strong>By: </strong>
            <Link to={`/users/${formData.user_id}`} className="author-link">
              {formData.author}
            </Link>
          </p>
          
          <p><strong>Description:</strong></p>
          <p>{formData.description}</p>
          
          <p><strong>Categories:</strong></p>
          <div className="categories">
            {categories
              .filter(category => formData.category_ids.includes(category.id))
              .map(category => (
                <span key={category.id} className="category-tag">
                  {category.name}
                </span>
              ))}
          </div>
          
          <p><strong>Ingredients:</strong></p>
          <pre>{formData.ingredients}</pre>
          
          <p><strong>Instructions:</strong></p>
          <pre>{formData.instructions}</pre>
        </div>
        <div className="form-actions">
          <Link to="/recipes" className="back-btn">Back to Recipes</Link>
          {isOwner && (
            <Link to={`/recipes/${id}/edit`} className="edit-recipe-btn">
              Edit Recipe
            </Link>
          )}
        </div>
      </div>
    );
  }

  // Show editable form for create/edit mode
  return (
    <div className="recipe-form">
      <h2>{isEditing ? 'Edit Recipe' : 'Create Recipe'}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Title:</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description:</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="category_ids">Categories:</label>
          <div className="category-selection">
            <select
              id="category_ids"
              name="category_ids"
              multiple
              value={formData.category_ids.map(String)}
              onChange={handleChange}
              className="category-select"
              style={{ minHeight: '150px' }}
            >
              {categories && categories.length > 0 ? (
                categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))
              ) : (
                <option value="" disabled>No categories available</option>
              )}
            </select>
            <small>Hold Ctrl (Windows) or Command (Mac) to select multiple categories</small>
            
            <div className="selected-categories">
              <p><strong>Selected categories:</strong></p>
              <div className="categories">
                {categories
                  .filter(category => formData.category_ids.includes(category.id))
                  .map(category => (
                    <span key={category.id} className="category-tag">
                      {category.name}
                    </span>
                  ))}
              </div>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="ingredients">Ingredients:</label>
          <textarea
            id="ingredients"
            name="ingredients"
            value={formData.ingredients}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="instructions">Instructions:</label>
          <textarea
            id="instructions"
            name="instructions"
            value={formData.instructions}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-actions">
          <button type="submit" className="submit-btn">
            {isEditing ? 'Update Recipe' : 'Create Recipe'}
          </button>
          <Link to="/recipes" className="back-btn">Cancel</Link>
        </div>
      </form>
    </div>
  );
};

export default RecipeForm; 