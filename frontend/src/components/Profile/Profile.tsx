import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface Recipe {
  id: number;
  title: string;
  user_id: number;
}

interface User {
  id: number;
  username: string;
  email: string;
}

const Profile: React.FC = () => {
  const [userRecipes, setUserRecipes] = useState<Recipe[]>([]);
  const [userInfo, setUserInfo] = useState<User | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      navigate('/login');
      return;
    }

    const user = JSON.parse(userStr);
    setUserInfo({
      id: user.id,
      username: user.username,
      email: user.email
    });

    fetchUserRecipes(user.id, user.token);
  }, []);

  const fetchUserRecipes = async (userId: number, token: string) => {
    try {
      const response = await fetch(`http://localhost:5000/recipes?user_id=${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setUserRecipes(data);
      } else if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } catch (error) {
      console.error('Error fetching user recipes:', error);
    }
  };

  if (!userInfo) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="profile-container">
      <h2>My Profile</h2>
      <div className="profile-info">
        <p><strong>Username:</strong> {userInfo.username}</p>
        <p><strong>Email:</strong> {userInfo.email}</p>
      </div>

      <div className="my-recipes">
        <h3>My Recipes</h3>
        {userRecipes.length === 0 ? (
          <p>You haven't posted any recipes yet. <Link to="/recipes/new">Create one now!</Link></p>
        ) : (
          <ul className="recipe-list">
            {userRecipes.map(recipe => (
              <li key={recipe.id}>
                <Link to={`/recipes/${recipe.id}`}>{recipe.title}</Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Profile; 