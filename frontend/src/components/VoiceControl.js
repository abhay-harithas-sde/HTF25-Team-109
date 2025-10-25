import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const VoiceControl = ({ onCommand }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState(null);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if speech recognition is supported
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };

      recognitionInstance.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        setTranscript(finalTranscript || interimTranscript);

        if (finalTranscript) {
          processVoiceCommand(finalTranscript.toLowerCase());
        }
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      setRecognition(recognitionInstance);
      setIsSupported(true);
    } else {
      setIsSupported(false);
    }
  }, []);

  const processVoiceCommand = (command) => {
    console.log('Voice command:', command);
    
    // Process different voice commands
    if (command.includes('scan food') || command.includes('take photo') || command.includes('camera')) {
      onCommand('scan food');
    } else if (command.includes('add food') || command.includes('manual entry')) {
      onCommand('add food');
    } else if (command.includes('show history') || command.includes('meal history')) {
      onCommand('show history');
    } else if (command.includes('analytics') || command.includes('show analytics')) {
      onCommand('analytics');
    } else if (command.includes('goals') || command.includes('show goals')) {
      onCommand('goals');
    } else if (command.includes('dashboard') || command.includes('home')) {
      onCommand('dashboard');
    } else if (command.includes('help') || command.includes('what can you do')) {
      showVoiceHelp();
    }
  };

  const showVoiceHelp = () => {
    const helpMessage = `
      Voice commands you can use:
      • "Scan food" - Open camera to scan food
      • "Add food" - Open manual food entry
      • "Show history" - View meal history
      • "Analytics" - View nutrition analytics
      • "Goals" - Open goals settings
      • "Dashboard" - Go to main dashboard
    `;
    alert(helpMessage);
  };

  const startListening = () => {
    if (recognition && !isListening) {
      recognition.start();
    }
  };

  const stopListening = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  if (!isSupported) {
    return null; // Don't render if not supported
  }

  return (
    <div className="voice-control">
      <motion.button
        className={`voice-button ${isListening ? 'listening' : ''}`}
        onClick={isListening ? stopListening : startListening}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        animate={isListening ? { 
          scale: [1, 1.1, 1],
          boxShadow: [
            "0 0 0 0 rgba(239, 68, 68, 0.4)",
            "0 0 0 10px rgba(239, 68, 68, 0)",
            "0 0 0 0 rgba(239, 68, 68, 0.4)"
          ]
        } : {}}
        transition={{ 
          scale: { duration: 0.8, repeat: Infinity },
          boxShadow: { duration: 1.5, repeat: Infinity }
        }}
      >
        {isListening ? '🔴' : '🎤'}
      </motion.button>

      <AnimatePresence>
        {isListening && (
          <motion.div
            className="voice-feedback"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className="listening-indicator">
              <div className="sound-wave">
                <div className="wave"></div>
                <div className="wave"></div>
                <div className="wave"></div>
                <div className="wave"></div>
              </div>
              <p>Listening...</p>
            </div>
            
            {transcript && (
              <div className="transcript">
                <p>"{transcript}"</p>
              </div>
            )}
            
            <div className="voice-commands-hint">
              <p>Try saying: "Scan food", "Add food", "Show history"</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default VoiceControl;