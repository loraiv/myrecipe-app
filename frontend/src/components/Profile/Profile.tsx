import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

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
  const [isCurrentUser, setIsCurrentUser] = useState(true);
  const navigate = useNavigate();
  const { userId } = useParams();

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      navigate('/login');
      return;
    }

    const currentUser = JSON.parse(userStr);
    
    // If userId is provided in URL, fetch that user's info, otherwise show current user's profile
    const targetUserId = userId || currentUser.id;
    setIsCurrentUser(!userId || parseInt(userId) === currentUser.id);

    // Fetch user info
    fetchUserInfo(targetUserId, currentUser.token);
    // Fetch user recipes
    fetchUserRecipes(targetUserId, currentUser.token);
  }, [userId]);

  const fetchUserInfo = async (targetUserId: string | number, token: string) => {
    try {
      const response = await fetch(`http://localhost:5000/users/${targetUserId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setUserInfo({
          id: data.id,
          username: data.username,
          email: isCurrentUser ? data.email : undefined // Only show email for current user
        });
      } else if (response.status === 401) {
        alert('Your session has expired. Please log in again.');
        localStorage.removeItem('user');
        navigate('/login');
      }
    } catch (error) {
      console.error('Error fetching user info:', error);
    }
  };

  const fetchUserRecipes = async (userId: string | number, token: string) => {
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
      <h2>{isCurrentUser ? 'My Profile' : `${userInfo.username}'s Profile`}</h2>
      <div className="profile-info">
        <p><strong>Username:</strong> {userInfo.username}</p>
        {isCurrentUser && userInfo.email && (
          <p><strong>Email:</strong> {userInfo.email}</p>
        )}
      </div>

      <div className="my-recipes">
        <h3>{isCurrentUser ? 'My Recipes' : `${userInfo.username}'s Recipes`}</h3>
        {userRecipes.length === 0 ? (
          <p>
            {isCurrentUser ? (
              <>No recipes yet. <Link to="/recipes/new">Create one now!</Link></>
            ) : (
              'No recipes yet.'
            )}
          </p>
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