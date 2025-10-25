import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../App';

const SocialFeatures = () => {
  const [activeTab, setActiveTab] = useState('feed');
  const [posts, setPosts] = useState([]);
  const [challenges, setChallenges] = useState([]);
  const [friends, setFriends] = useState([]);
  const [newPost, setNewPost] = useState({ content: '', image: null, meal: null });
  const [showCreatePost, setShowCreatePost] = useState(false);
  const { user, dailyStats } = useAppContext();

  useEffect(() => {
    loadSocialData();
  }, []);

  const loadSocialData = async () => {
    // Mock data for demonstration
    setPosts([
      {
        id: 1,
        user: { name: 'Sarah Johnson', avatar: '👩‍🦰' },
        content: 'Just made this amazing quinoa bowl! 🥗 Feeling great about my healthy choices today.',
        image: '/api/placeholder/meal1.jpg',
        meal: { name: 'Quinoa Power Bowl', calories: 420 },
        likes: 15,
        comments: 3,
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
        liked: false
      },
      {
        id: 2,
        user: { name: 'Mike Chen', avatar: '👨‍💼' },
        content: 'Week 3 of my fitness journey! Down 5 pounds and feeling stronger every day 💪',
        likes: 28,
        comments: 7,
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
        liked: true
      },
      {
        id: 3,
        user: { name: 'Emma Davis', avatar: '👩‍🎓' },
        content: 'Meal prep Sunday! These overnight oats are going to make my mornings so much easier 🌅',
        image: '/api/placeholder/meal2.jpg',
        meal: { name: 'Overnight Oats', calories: 280 },
        likes: 12,
        comments: 2,
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        liked: false
      }
    ]);

    setChallenges([
      {
        id: 1,
        title: '30-Day Veggie Challenge',
        description: 'Eat 5 servings of vegetables every day for 30 days',
        participants: 156,
        daysLeft: 12,
        progress: 18,
        joined: true
      },
      {
        id: 2,
        title: 'Hydration Hero',
        description: 'Drink 8 glasses of water daily for 2 weeks',
        participants: 89,
        daysLeft: 5,
        progress: 9,
        joined: false
      },
      {
        id: 3,
        title: 'Protein Power Week',
        description: 'Meet your protein goals every day this week',
        participants: 234,
        daysLeft: 3,
        progress: 4,
        joined: true
      }
    ]);

    setFriends([
      { id: 1, name: 'Alex Rivera', avatar: '👨‍🎨', status: 'online', streak: 15 },
      { id: 2, name: 'Lisa Park', avatar: '👩‍💻', status: 'offline', streak: 8 },
      { id: 3, name: 'David Kim', avatar: '👨‍🔬', status: 'online', streak: 22 }
    ]);
  };

  const createPost = async () => {
    if (!newPost.content.trim()) return;

    const post = {
      id: Date.now(),
      user: { name: user.name, avatar: '👤' },
      content: newPost.content,
      image: newPost.image,
      meal: newPost.meal,
      likes: 0,
      comments: 0,
      timestamp: new Date(),
      liked: false
    };

    setPosts([post, ...posts]);
    setNewPost({ content: '', image: null, meal: null });
    setShowCreatePost(false);
  };

  const toggleLike = (postId) => {
    setPosts(posts.map(post => 
      post.id === postId 
        ? { 
            ...post, 
            liked: !post.liked, 
            likes: post.liked ? post.likes - 1 : post.likes + 1 
          }
        : post
    ));
  };

  const joinChallenge = (challengeId) => {
    setChallenges(challenges.map(challenge =>
      challenge.id === challengeId
        ? { ...challenge, joined: !challenge.joined }
        : challenge
    ));
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return 'Just now';
  };

  return (
    <div className="social-features">
      <div className="social-header">
        <h2>👥 Social Hub</h2>
        <div className="social-tabs">
          {['feed', 'challenges', 'friends'].map(tab => (
            <button
              key={tab}
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'feed' && '📰 Feed'}
              {tab === 'challenges' && '🏆 Challenges'}
              {tab === 'friends' && '👥 Friends'}
            </button>
          ))}
        </div>
      </div>

      <AnimatePresence mode="wait">
        {/* Feed Tab */}
        {activeTab === 'feed' && (
          <motion.div
            key="feed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="feed-tab"
          >
            {/* Create Post */}
            <div className="create-post-section">
              <button
                className="create-post-btn"
                onClick={() => setShowCreatePost(true)}
              >
                ✍️ Share your progress...
              </button>
            </div>

            {/* Posts Feed */}
            <div className="posts-feed">
              {posts.map((post, index) => (
                <motion.div
                  key={post.id}
                  className="post-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="post-header">
                    <div className="user-info">
                      <div className="user-avatar">{post.user.avatar}</div>
                      <div className="user-details">
                        <h4>{post.user.name}</h4>
                        <span className="post-time">{formatTimeAgo(post.timestamp)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="post-content">
                    <p>{post.content}</p>
                    {post.image && (
                      <div className="post-image">
                        <img src={post.image} alt="Post" />
                      </div>
                    )}
                    {post.meal && (
                      <div className="post-meal">
                        <div className="meal-info">
                          <span className="meal-name">🍽️ {post.meal.name}</span>
                          <span className="meal-calories">{post.meal.calories} cal</span>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="post-actions">
                    <button
                      className={`action-btn like ${post.liked ? 'liked' : ''}`}
                      onClick={() => toggleLike(post.id)}
                    >
                      {post.liked ? '❤️' : '🤍'} {post.likes}
                    </button>
                    <button className="action-btn comment">
                      💬 {post.comments}
                    </button>
                    <button className="action-btn share">
                      📤 Share
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Challenges Tab */}
        {activeTab === 'challenges' && (
          <motion.div
            key="challenges"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="challenges-tab"
          >
            <div className="challenges-header">
              <h3>🏆 Active Challenges</h3>
              <p>Join challenges to stay motivated and compete with friends!</p>
            </div>

            <div className="challenges-grid">
              {challenges.map((challenge, index) => (
                <motion.div
                  key={challenge.id}
                  className={`challenge-card ${challenge.joined ? 'joined' : ''}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="challenge-header">
                    <h4>{challenge.title}</h4>
                    <div className="challenge-meta">
                      <span className="participants">👥 {challenge.participants}</span>
                      <span className="days-left">⏰ {challenge.daysLeft} days left</span>
                    </div>
                  </div>

                  <p className="challenge-description">{challenge.description}</p>

                  {challenge.joined && (
                    <div className="challenge-progress">
                      <div className="progress-header">
                        <span>Progress: {challenge.progress}/{challenge.progress + challenge.daysLeft} days</span>
                        <span>{Math.round((challenge.progress / (challenge.progress + challenge.daysLeft)) * 100)}%</span>
                      </div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ width: `${(challenge.progress / (challenge.progress + challenge.daysLeft)) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}

                  <div className="challenge-actions">
                    <button
                      className={`join-btn ${challenge.joined ? 'joined' : ''}`}
                      onClick={() => joinChallenge(challenge.id)}
                    >
                      {challenge.joined ? '✅ Joined' : '🚀 Join Challenge'}
                    </button>
                    {challenge.joined && (
                      <button className="update-progress-btn">
                        📊 Update Progress
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Create Challenge */}
            <div className="create-challenge-section">
              <button className="create-challenge-btn">
                ➕ Create New Challenge
              </button>
            </div>
          </motion.div>
        )}

        {/* Friends Tab */}
        {activeTab === 'friends' && (
          <motion.div
            key="friends"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="friends-tab"
          >
            <div className="friends-header">
              <h3>👥 Your Friends</h3>
              <button className="add-friends-btn">
                ➕ Add Friends
              </button>
            </div>

            <div className="friends-list">
              {friends.map((friend, index) => (
                <motion.div
                  key={friend.id}
                  className="friend-card"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="friend-info">
                    <div className="friend-avatar">{friend.avatar}</div>
                    <div className="friend-details">
                      <h4>{friend.name}</h4>
                      <div className="friend-status">
                        <span className={`status-dot ${friend.status}`}></span>
                        <span>{friend.status}</span>
                      </div>
                    </div>
                  </div>

                  <div className="friend-stats">
                    <div className="stat">
                      <span className="stat-value">{friend.streak}</span>
                      <span className="stat-label">day streak</span>
                    </div>
                  </div>

                  <div className="friend-actions">
                    <button className="message-btn">💬</button>
                    <button className="challenge-btn">⚔️</button>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Leaderboard */}
            <div className="leaderboard-section">
              <h3>🏆 Weekly Leaderboard</h3>
              <div className="leaderboard">
                {friends
                  .sort((a, b) => b.streak - a.streak)
                  .map((friend, index) => (
                    <div key={friend.id} className="leaderboard-item">
                      <span className="rank">#{index + 1}</span>
                      <span className="name">{friend.name}</span>
                      <span className="score">{friend.streak} days</span>
                    </div>
                  ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Create Post Modal */}
      <AnimatePresence>
        {showCreatePost && (
          <motion.div
            className="create-post-modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowCreatePost(false)}
          >
            <motion.div
              className="create-post-modal"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <h3>✍️ Create Post</h3>
                <button 
                  className="close-modal"
                  onClick={() => setShowCreatePost(false)}
                >
                  ✕
                </button>
              </div>

              <div className="modal-content">
                <textarea
                  className="post-input"
                  placeholder="Share your progress, achievements, or motivation..."
                  value={newPost.content}
                  onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                  rows={4}
                />

                <div className="post-options">
                  <button className="option-btn">
                    📷 Add Photo
                  </button>
                  <button className="option-btn">
                    🍽️ Add Meal
                  </button>
                  <button className="option-btn">
                    📊 Add Progress
                  </button>
                </div>
              </div>

              <div className="modal-actions">
                <button 
                  className="cancel-btn"
                  onClick={() => setShowCreatePost(false)}
                >
                  Cancel
                </button>
                <button 
                  className="post-btn"
                  onClick={createPost}
                  disabled={!newPost.content.trim()}
                >
                  📤 Post
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SocialFeatures;