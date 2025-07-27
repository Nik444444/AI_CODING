import React from 'react';
import './Button.css';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  onClick,
  ...props 
}) => {
  const className = `btn btn-${variant} btn-${size} ${disabled ? 'btn-disabled' : ''}`;
  
  return (
    <button 
      className={className}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
