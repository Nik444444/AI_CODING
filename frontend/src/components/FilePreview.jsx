import React, { useState } from 'react';
import { 
  FileText, 
  Image, 
  Code, 
  Download, 
  Eye, 
  EyeOff,
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

const FilePreview = ({ files = [], className = "" }) => {
  const [expandedFiles, setExpandedFiles] = useState({});
  const [copiedFiles, setCopiedFiles] = useState({});

  const toggleExpanded = (fileId) => {
    setExpandedFiles(prev => ({
      ...prev,
      [fileId]: !prev[fileId]
    }));
  };

  const copyContent = async (content, fileId) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFiles(prev => ({ ...prev, [fileId]: true }));
      setTimeout(() => {
        setCopiedFiles(prev => ({ ...prev, [fileId]: false }));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp'].includes(extension)) {
      return Image;
    } else if (['js', 'jsx', 'ts', 'tsx', 'py', 'html', 'css', 'json'].includes(extension)) {
      return Code;
    } else {
      return FileText;
    }
  };

  const getFileType = (fileName) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    const typeMap = {
      'js': 'JavaScript',
      'jsx': 'React Component',
      'ts': 'TypeScript',
      'tsx': 'React TypeScript',
      'py': 'Python',
      'html': 'HTML',
      'css': 'CSS',
      'json': 'JSON',
      'md': 'Markdown',
      'txt': 'Text',
      'png': 'PNG Image',
      'jpg': 'JPEG Image',
      'jpeg': 'JPEG Image',
      'gif': 'GIF Image',
      'svg': 'SVG Vector'
    };
    
    return typeMap[extension] || 'Файл';
  };

  const formatFileSize = (content) => {
    const bytes = new Blob([content || '']).size;
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  if (!files || files.length === 0) {
    return null;
  }

  return (
    <div className={`file-preview-container ${className}`}>
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
          <FileText className="w-4 h-4 mr-2" />
          Созданные файлы ({files.length})
        </h4>
        
        <div className="space-y-3">
          {files.map((file, index) => {
            const fileId = `file-${index}`;
            const isExpanded = expandedFiles[fileId];
            const IconComponent = getFileIcon(file.name || file.path || `file-${index}`);
            const fileName = file.name || file.path || `Файл ${index + 1}`;
            const fileContent = file.content || '';
            
            return (
              <Card key={fileId} className="bg-gray-900 border-gray-700">
                <CardContent className="p-4">
                  {/* File Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3 min-w-0 flex-1">
                      <div className="flex-shrink-0">
                        <IconComponent className="w-5 h-5 text-cyan-400" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-white truncate">{fileName}</p>
                        <p className="text-xs text-gray-400">
                          {getFileType(fileName)} • {formatFileSize(fileContent)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {fileContent && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyContent(fileContent, fileId)}
                          className="h-8 w-8 p-0"
                          title="Копировать содержимое"
                        >
                          {copiedFiles[fileId] ? (
                            <Check className="h-4 w-4 text-green-400" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                      
                      {fileContent && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleExpanded(fileId)}
                          className="h-8 w-8 p-0"
                          title={isExpanded ? "Скрыть содержимое" : "Показать содержимое"}
                        >
                          {isExpanded ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  {/* File Content Preview */}
                  {fileContent && isExpanded && (
                    <div className="mt-3">
                      <div className="bg-gray-950 rounded-lg p-4 border border-gray-700">
                        <pre className="text-sm text-gray-100 overflow-x-auto whitespace-pre-wrap">
                          <code>{fileContent}</code>
                        </pre>
                      </div>
                    </div>
                  )}
                  
                  {/* Quick Preview (first few lines) */}
                  {fileContent && !isExpanded && (
                    <div className="mt-3">
                      <div className="bg-gray-950 rounded-lg p-3 border border-gray-700">
                        <pre className="text-xs text-gray-400 overflow-hidden">
                          <code>
                            {fileContent.split('\n').slice(0, 3).join('\n')}
                            {fileContent.split('\n').length > 3 && '\n...'}
                          </code>
                        </pre>
                      </div>
                    </div>
                  )}
                  
                  {/* File Actions */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-700">
                    <span className="text-xs text-gray-500">
                      {fileContent.split('\n').length} строк
                    </span>
                    
                    <div className="flex items-center space-x-2">
                      {file.url && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(file.url, '_blank')}
                          className="h-7 text-xs"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          Открыть
                        </Button>
                      )}
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const blob = new Blob([fileContent], { type: 'text/plain' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = fileName;
                          document.body.appendChild(a);
                          a.click();
                          document.body.removeChild(a);
                          URL.revokeObjectURL(url);
                        }}
                        className="h-7 text-xs"
                      >
                        <Download className="w-3 h-3 mr-1" />
                        Скачать
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default FilePreview;