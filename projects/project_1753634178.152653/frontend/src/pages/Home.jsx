import React, { useState } from 'react';
import { useItems, useHealthCheck } from '../hooks/useApi';
import Button from '../components/Button/Button';
import './Home.css';

const Home = () => {
  const { items, loading, error, createItem, deleteItem } = useItems();
  const { health } = useHealthCheck();
  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');

  const handleCreateItem = async (e) => {
    e.preventDefault();
    if (!newItemName.trim()) return;

    try {
      await createItem({
        name: newItemName,
        description: newItemDesc
      });
      setNewItemName('');
      setNewItemDesc('');
    } catch (err) {
      console.error('Ошибка создания:', err);
    }
  };

  return (
    <div className="home">
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Полнофункциональное приложение
          </h1>
          <p className="hero-description">
            Frontend + Backend интеграция работает! 
            {health && <span className="health-status">Статус: {health.status}</span>}
          </p>
        </div>
      </section>
      
      <section className="api-demo">
        <h2>Демо API</h2>
        
        <div className="create-item-form">
          <h3>Создать новый элемент</h3>
          <form onSubmit={handleCreateItem}>
            <input
              type="text"
              placeholder="Название"
              value={newItemName}
              onChange={(e) => setNewItemName(e.target.value)}
              className="input"
            />
            <input
              type="text"
              placeholder="Описание"
              value={newItemDesc}
              onChange={(e) => setNewItemDesc(e.target.value)}
              className="input"
            />
            <Button type="submit" variant="primary">
              Создать
            </Button>
          </form>
        </div>

        <div className="items-list">
          <h3>Список элементов</h3>
          {loading && <p>Загрузка...</p>}
          {error && <p className="error">Ошибка: {error}</p>}
          
          <div className="items-grid">
            {items.map((item) => (
              <div key={item.id} className="item-card">
                <h4>{item.name}</h4>
                <p>{item.description}</p>
                <p className="item-date">
                  Создано: {new Date(item.created_at).toLocaleDateString()}
                </p>
                <Button 
                  variant="error" 
                  size="sm"
                  onClick={() => deleteItem(item.id)}
                >
                  Удалить
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;

