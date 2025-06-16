import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SearchBar.css';

interface SearchResult {
  id: number;
  title?: string;
  description?: string;
  username?: string;
  email?: string;
  image_url?: string;
}

const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'recipes' | 'users'>('recipes');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.length < 2) return;

    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/search/${searchType}?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setResults(data);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    if (searchType === 'recipes') {
      navigate(`/recipes/${result.id}`);
    } else {
      navigate(`/users/${result.id}`);
    }
    setQuery('');
    setResults([]);
  };

  return (
    <div className="search-container">
      <form onSubmit={handleSearch} className="search-input-container">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Search ${searchType}...`}
          className="search-input"
          minLength={2}
        />
        <select
          value={searchType}
          onChange={(e) => setSearchType(e.target.value as 'recipes' | 'users')}
          className="search-type-select"
        >
          <option value="recipes">Recipes</option>
          <option value="users">Users</option>
        </select>
        <button type="submit" className="search-button">Search</button>
      </form>
      
      {isLoading && <div className="search-loading">Loading...</div>}
      
      {results.length > 0 && (
        <div className="search-results">
          {results.map((result) => (
            <div
              key={result.id}
              className="search-result-item"
              onClick={() => handleResultClick(result)}
            >
              {searchType === 'recipes' ? (
                <>
                  {result.image_url && (
                    <img src={result.image_url} alt={result.title} className="result-image" />
                  )}
                  <div className="result-content">
                    <div className="result-title">{result.title}</div>
                    <div className="result-description">{result.description}</div>
                  </div>
                </>
              ) : (
                <>
                  <div className="result-title">{result.username}</div>
                  <div className="result-description">{result.email}</div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
      
      {results.length === 0 && query.length >= 2 && !isLoading && (
        <div className="no-results">No results found for "{query}"</div>
      )}
    </div>
  );
};

export default SearchBar; 