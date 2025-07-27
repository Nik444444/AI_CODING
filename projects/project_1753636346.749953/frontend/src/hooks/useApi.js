import { useState, useEffect } from 'react';
import { api } from '../services/api';

// Хук для загрузки списка items
export const useItems = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await api.getItems();
      setItems(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createItem = async (itemData) => {
    try {
      const response = await api.createItem(itemData);
      setItems(prev => [...prev, response.data]);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const deleteItem = async (id) => {
    try {
      await api.deleteItem(id);
      setItems(prev => prev.filter(item => item.id !== id));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  return {
    items,
    loading,
    error,
    fetchItems,
    createItem,
    deleteItem
  };
};

// Хук для health check
export const useHealthCheck = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await api.healthCheck();
        setHealth(response.data);
      } catch (err) {
        setHealth({ status: 'error', message: err.message });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  return { health, loading };
};
