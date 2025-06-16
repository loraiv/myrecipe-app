import React, { useState, useEffect } from 'react';
import './CommentSection.css';

interface Comment {
  id: number;
  user_id: number;
  username: string;
  content: string;
  rating: number;
  created_at: string;
}

interface CommentSectionProps {
  recipeId: number;
}

const CommentSection: React.FC<CommentSectionProps> = ({ recipeId }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchComments();
  }, [recipeId]);

  const fetchComments = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/recipes/${recipeId}/comments`);
      if (response.ok) {
        const data = await response.json();
        setComments(data);
      }
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || rating === 0) return;

    try {
      const response = await fetch(`http://localhost:5000/api/recipes/${recipeId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newComment.trim(),
          rating,
        }),
        credentials: 'include',
      });

      if (response.ok) {
        const newCommentData = await response.json();
        setComments([...comments, newCommentData]);
        setNewComment('');
        setRating(0);
      }
    } catch (error) {
      console.error('Failed to post comment:', error);
    }
  };

  const StarRating = ({ value, onRate, onHover }: { value: number; onRate?: (rating: number) => void; onHover?: (rating: number) => void }) => {
    return (
      <div className="star-rating">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`star ${star <= (hoveredRating || value) ? 'filled' : ''}`}
            onClick={() => onRate?.(star)}
            onMouseEnter={() => onHover?.(star)}
            onMouseLeave={() => onHover?.(0)}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="comment-section">
      <h3>Comments & Ratings</h3>
      
      <form onSubmit={handleSubmit} className="comment-form">
        <div className="rating-input">
          <label>Your Rating:</label>
          <StarRating
            value={rating}
            onRate={setRating}
            onHover={setHoveredRating}
          />
        </div>
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Share your thoughts about this recipe..."
          required
        />
        <button type="submit" disabled={!newComment.trim() || rating === 0}>
          Post Comment
        </button>
      </form>

      <div className="comments-list">
        {isLoading ? (
          <div className="loading">Loading comments...</div>
        ) : comments.length === 0 ? (
          <div className="no-comments">No comments yet. Be the first to comment!</div>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="comment">
              <div className="comment-header">
                <span className="comment-author">{comment.username}</span>
                <StarRating value={comment.rating} />
                <span className="comment-date">
                  {new Date(comment.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="comment-content">{comment.content}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CommentSection; 