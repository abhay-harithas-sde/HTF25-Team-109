import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppContext } from '../App';

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hi! I'm your AI nutrition assistant. I can help you with meal planning, nutrition advice, and food analysis. What would you like to know?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, dailyStats, aiInsights } = useAppContext();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response (in real app, this would call your AI API)
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage, { user, dailyStats, aiInsights });
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const generateAIResponse = (message, context) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('calorie') || lowerMessage.includes('calories')) {
      return `Based on your current intake of ${Math.round(context.dailyStats.calories)} calories today, you're ${context.dailyStats.calories < 2000 ? 'below' : 'at'} your daily goal. ${context.dailyStats.calories < 2000 ? 'Consider adding a healthy snack!' : 'Great job staying on track!'}`;
    }
    
    if (lowerMessage.includes('protein')) {
      return `You've consumed ${Math.round(context.dailyStats.protein)}g of protein today. For optimal muscle maintenance, aim for 0.8-1g per kg of body weight. Consider adding lean meats, eggs, or legumes to your meals.`;
    }
    
    if (lowerMessage.includes('meal') || lowerMessage.includes('food')) {
      return `I can help you plan nutritious meals! Based on your preferences, I'd recommend focusing on whole foods, lean proteins, and plenty of vegetables. Would you like specific meal suggestions for breakfast, lunch, or dinner?`;
    }
    
    if (lowerMessage.includes('weight') || lowerMessage.includes('lose') || lowerMessage.includes('gain')) {
      return `For healthy weight management, focus on creating a moderate calorie deficit/surplus (300-500 calories) combined with regular exercise. Track your progress consistently and be patient with the process!`;
    }
    
    if (lowerMessage.includes('water') || lowerMessage.includes('hydration')) {
      return `Staying hydrated is crucial for metabolism and appetite control. Aim for 8-10 glasses of water daily, more if you're active. Try adding lemon or cucumber for flavor!`;
    }
    
    if (lowerMessage.includes('exercise') || lowerMessage.includes('workout')) {
      return `Combining nutrition tracking with regular exercise amplifies your results! Aim for 150 minutes of moderate activity weekly, plus 2-3 strength training sessions. Don't forget to fuel your workouts properly!`;
    }
    
    // Default responses
    const defaultResponses = [
      "That's a great question! Nutrition is very individual. Based on your current data, I'd recommend focusing on balanced meals with adequate protein and vegetables.",
      "I'm here to help with your nutrition journey! Feel free to ask about meal planning, calorie goals, or specific foods you're curious about.",
      "Every small step counts in your health journey. Keep tracking your meals and stay consistent with your goals!",
      "Remember, sustainable changes are better than drastic ones. Focus on adding nutritious foods rather than restricting everything."
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const quickQuestions = [
    "How many calories should I eat?",
    "What's a healthy breakfast?",
    "How much protein do I need?",
    "Tips for meal prep?",
    "Best snacks for energy?",
    "How to stay hydrated?"
  ];

  return (
    <>
      {/* Floating AI Button */}
      <motion.button
        className="ai-assistant-button"
        onClick={() => setIsOpen(true)}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        animate={{ 
          boxShadow: isOpen ? "0 0 0 0 rgba(102, 126, 234, 0)" : "0 0 0 10px rgba(102, 126, 234, 0.3)"
        }}
        transition={{ 
          boxShadow: { duration: 1.5, repeat: Infinity }
        }}
      >
        🤖
      </motion.button>

      {/* AI Chat Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="ai-assistant-modal"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              className="ai-chat-container"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Chat Header */}
              <div className="chat-header">
                <div className="ai-avatar">🤖</div>
                <div className="ai-info">
                  <h3>AI Nutrition Assistant</h3>
                  <span className="ai-status">Online • Ready to help</span>
                </div>
                <button 
                  className="close-chat"
                  onClick={() => setIsOpen(false)}
                >
                  ✕
                </button>
              </div>

              {/* Chat Messages */}
              <div className="chat-messages">
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    className={`message ${message.type}`}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="message-content">
                      {message.content}
                    </div>
                    <div className="message-time">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </div>
                  </motion.div>
                ))}
                
                {isTyping && (
                  <motion.div
                    className="message assistant typing"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Quick Questions */}
              {messages.length === 1 && (
                <div className="quick-questions">
                  <p>Quick questions you can ask:</p>
                  <div className="question-chips">
                    {quickQuestions.map((question, index) => (
                      <button
                        key={index}
                        className="question-chip"
                        onClick={() => {
                          setInputMessage(question);
                          handleSendMessage();
                        }}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat Input */}
              <div className="chat-input-container">
                <input
                  type="text"
                  className="chat-input"
                  placeholder="Ask me anything about nutrition..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  disabled={isTyping}
                />
                <button
                  className="send-button"
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                >
                  📤
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default AIAssistant;