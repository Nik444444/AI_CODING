import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator = ({ agentName = "AI Ассистент" }) => {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex max-w-4xl">
        <div className="flex-shrink-0 mr-4">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center shadow-lg">
            <Bot className="w-5 h-5 text-white animate-pulse" />
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-700 rounded-2xl px-6 py-4 shadow-lg">
          <div className="flex items-center space-x-3">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
              <div 
                className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" 
                style={{animationDelay: '0.1s'}}
              ></div>
              <div 
                className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" 
                style={{animationDelay: '0.2s'}}
              ></div>
            </div>
            <span className="text-gray-400 text-sm font-medium">
              {agentName} печатает...
            </span>
          </div>
          
          {/* Subtle pulsing background effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-blue-500/5 rounded-2xl animate-pulse"></div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;