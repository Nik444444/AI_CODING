import React from 'react';
import { Copy, Check } from 'lucide-react';
import { Button } from './ui/button';

const MessageFormatter = ({ content, className = "" }) => {
  const [copiedStates, setCopiedStates] = React.useState({});

  const copyToClipboard = async (text, blockId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedStates(prev => ({ ...prev, [blockId]: true }));
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [blockId]: false }));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const formatMessage = (text) => {
    if (!text) return '';

    // Split text into parts based on code blocks
    const parts = [];
    let currentIndex = 0;
    
    // Regex to match code blocks (both ``` and single backticks)
    const codeBlockRegex = /```(\w+)?\n?([\s\S]*?)```|`([^`]+)`/g;
    let match;

    while ((match = codeBlockRegex.exec(text)) !== null) {
      // Add text before code block
      if (match.index > currentIndex) {
        const beforeText = text.slice(currentIndex, match.index);
        parts.push({
          type: 'text',
          content: beforeText
        });
      }

      if (match[0].startsWith('```')) {
        // Multi-line code block
        const language = match[1] || 'text';
        const code = match[2];
        parts.push({
          type: 'codeblock',
          language: language,
          content: code,
          id: `code-${parts.length}`
        });
      } else {
        // Inline code
        parts.push({
          type: 'inline-code',
          content: match[3]
        });
      }

      currentIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (currentIndex < text.length) {
      parts.push({
        type: 'text',
        content: text.slice(currentIndex)
      });
    }

    return parts;
  };

  const formatTextContent = (text) => {
    // Format basic markdown elements
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gm, '<h2 class="text-xl font-semibold mt-4 mb-2">$1</h2>')
      .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mt-4 mb-2">$1</h1>')
      .replace(/^- (.*$)/gm, '<li class="ml-4">• $1</li>')
      .replace(/^\d+\.\s(.*$)/gm, '<li class="ml-4">$1</li>')
      .replace(/\n/g, '<br>');
  };

  const parts = formatMessage(content);

  return (
    <div className={`message-content ${className}`}>
      {parts.map((part, index) => {
        switch (part.type) {
          case 'codeblock':
            return (
              <div key={index} className="relative my-4">
                <div className="flex items-center justify-between bg-gray-800 px-4 py-2 rounded-t-lg">
                  <span className="text-sm text-gray-300 font-mono">{part.language}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(part.content, part.id)}
                    className="h-6 w-6 p-0 hover:bg-gray-700"
                  >
                    {copiedStates[part.id] ? (
                      <Check className="h-3 w-3 text-green-400" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <pre className="bg-gray-900 p-4 rounded-b-lg overflow-x-auto">
                  <code className="text-gray-100 text-sm font-mono whitespace-pre">
                    {part.content}
                  </code>
                </pre>
              </div>
            );
          
          case 'inline-code':
            return (
              <code key={index} className="bg-gray-800 text-cyan-300 px-2 py-1 rounded text-sm font-mono">
                {part.content}
              </code>
            );
          
          case 'text':
            return (
              <div
                key={index}
                className="prose prose-invert max-w-none"
                dangerouslySetInnerHTML={{
                  __html: formatTextContent(part.content)
                }}
              />
            );
          
          default:
            return null;
        }
      })}
    </div>
  );
};

export default MessageFormatter;