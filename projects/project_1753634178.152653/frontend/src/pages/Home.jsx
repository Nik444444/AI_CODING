import React from 'react';
import Button from '../components/Button/Button';
import './Home.css';

const Home = () => {
  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Добро пожаловать в наше приложение
          </h1>
          <p className="hero-description">
            Современное веб-приложение, созданное с помощью React и передовых технологий.
          </p>
          <div className="hero-actions">
            <Button variant="primary" size="lg">
              Начать работу
            </Button>
            <Button variant="secondary" size="lg">
              Узнать больше
            </Button>
          </div>
        </div>
      </section>
      
      <section className="features">
        <div className="features-grid">
          <div className="feature-card">
            <h3>Современный дизайн</h3>
            <p>Красивый и интуитивно понятный интерфейс</p>
          </div>
          <div className="feature-card">
            <h3>Высокая производительность</h3>
            <p>Быстрая загрузка и отзывчивость</p>
          </div>
          <div className="feature-card">
            <h3>Адаптивность</h3>
            <p>Работает на всех устройствах</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
