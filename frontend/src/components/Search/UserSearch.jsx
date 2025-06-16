import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function UserSearch() {
  const [username, setUsername] = useState('');
  const [recipes, setRecipes] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  const handleSearch = async () => {
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setError('');
    setRecipes([]);
    setUserInfo(null);
    setLoading(true);

    try {
      const userStr = localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : null;

      if (!user?.token) {
        throw new Error('You must be logged in to search');
      }

      // Search for user and their recipes in one request
      const response = await fetch(`http://localhost:5000/search_user?username=${encodeURIComponent(username)}`, {
        headers: {
          'Authorization': `Bearer ${user.token}`
        },
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(response.status === 404 ? 'User not found' : 'Failed to search for user');
      }

      const data = await response.json();
      setUserInfo({ username: data.user });
      setRecipes(data.recipes);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="user-search-container">
      <h2>Search Users</h2>
      <div className="search-box">
        <input
          type="text"
          placeholder="Enter username to search..."
          value={username}
          onChange={e => setUsername(e.target.value)}
          onKeyPress={handleKeyPress}
          className="search-input"
        />
        <button 
          onClick={handleSearch} 
          disabled={loading}
          className="search-button"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {userInfo && (
        <div className="user-info">
          <h3>User Profile</h3>
          <div className="user-profile">
            <div className="user-details">
              <h4>{userInfo.username}</h4>
            </div>
          </div>
        </div>
      )}

      {recipes.length > 0 && (
        <div className="user-recipes">
          <h3>{userInfo.username}'s Recipes</h3>
          <div className="recipe-grid">
            {recipes.map(recipe => (
              <div key={recipe.id} className="recipe-card">
                <h4>{recipe.title}</h4>
                {recipe.description && (
                  <p className="recipe-description">{recipe.description}</p>
                )}
                <Link to={`/recipes/${recipe.id}`} className="view-recipe-btn">
                  View Recipe
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {userInfo && recipes.length === 0 && (
        <div className="no-recipes">
          <p>No recipes found for this user.</p>
        </div>
      )}
    </div>
  );
}

export default UserSearch;