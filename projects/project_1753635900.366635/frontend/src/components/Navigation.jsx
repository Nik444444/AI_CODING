import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import './Navigation.css';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          My App
        </Link>
        
        <div className={`nav-menu ${isOpen ? 'nav-menu-open' : ''}`}>
          <Link to="/" className="nav-link" onClick={() => setIsOpen(false)}>
            Главная
          </Link>
          <Link to="/about" className="nav-link" onClick={() => setIsOpen(false)}>
            О нас
          </Link>
        </div>
        
        <button 
          className="nav-toggle"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
