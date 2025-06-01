import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import RecipeList from './components/Recipes/RecipeList';
import RecipeForm from './components/Recipes/RecipeForm';
import Profile from './components/Profile/Profile';
import './App.css';

const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('user'));

  useEffect(() => {
    // Update authentication state when localStorage changes
    const handleStorageChange = () => {
      setIsAuthenticated(!!localStorage.getItem('user'));
    };

    // Add event listener for storage changes
    window.addEventListener('storage', handleStorageChange);

    // Add event listener for custom auth event
    window.addEventListener('auth-change', handleStorageChange);

    // Check auth state on mount
    handleStorageChange();

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-change', handleStorageChange);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    window.location.href = '/login';
  };

  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">Recipe App</div>
          <div className="nav-links">
            {isAuthenticated ? (
              <>
                <Link to="/recipes">Recipes</Link>
                <Link to="/recipes/new">Create Recipe</Link>
                <Link to="/profile">My Profile</Link>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login">Login</Link>
                <Link to="/register">Register</Link>
              </>
            )}
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <Navigate to="/recipes" replace />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route 
              path="/login" 
              element={
                isAuthenticated ? (
                  <Navigate to="/recipes" replace />
                ) : (
                  <Login setIsAuthenticated={setIsAuthenticated} />
                )
              } 
            />
            <Route 
              path="/register" 
              element={
                isAuthenticated ? (
                  <Navigate to="/recipes" replace />
                ) : (
                  <Register />
                )
              } 
            />
            <Route
              path="/recipes"
              element={
                isAuthenticated ? <RecipeList /> : <Navigate to="/login" replace />
              }
            />
            <Route
              path="/recipes/new"
              element={
                isAuthenticated ? <RecipeForm /> : <Navigate to="/login" replace />
              }
            />
            <Route
              path="/recipes/:id"
              element={
                isAuthenticated ? <RecipeForm /> : <Navigate to="/login" replace />
              }
            />
            <Route
              path="/recipes/:id/edit"
              element={
                isAuthenticated ? <RecipeForm /> : <Navigate to="/login" replace />
              }
            />
            <Route
              path="/profile"
              element={
                isAuthenticated ? <Profile /> : <Navigate to="/login" replace />
              }
            />
            <Route
              path="/users/:userId"
              element={
                isAuthenticated ? <Profile /> : <Navigate to="/login" replace />
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
