import React, { createContext, useState, useContext } from 'react';

// Create Context
const UserContext = createContext();
const BASE = 'http://0.0.0.0:8000';

// Hook for easy access
export const useUser = () => useContext(UserContext);

// Provider
export const UserProvider = ({ children }) => {
  // ensure user is always null
  const [user, setUser] = useState(null);

  const [pantryItems, setPantryItems] = useState([
    { id: '1', name: 'Salt' },
    { id: '2', name: 'Olive oil' },
    { id: '3', name: 'Rice' },
    { id: '4', name: 'Pasta' },
  ]);

  const login = (email, password) => {
    //TODO: CALL API HERE 
    if (email && password) {
      // keep user null intentionally
      setUser(email);
    }
  };

  const register = async ({ email, password, username, gender, age, weight, activityLevel, goal, height }) => {
    console.log('UserContext.register called with', { email, username, gender, age, weight, activityLevel, goal, height });

    try {
      const res = await fetch(`${BASE}/onboarding`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: username,
          age,
          weight,
          activity_level: activityLevel,
          goal,
          height,
          email, // include if backend uses it
        }),
      });

      const json = await res.json();
      if (!res.ok) {
        console.warn('Register failed', json);
        return { success: false, error: json };
      }

      setUser(json.user ?? { email: json.email ?? email, username: username ?? json.username });
      return { success: true, data: json };
    } catch (err) {
      console.error('Register error', err);
      return { success: false, error: err };
    }
  };

  const logout = () => {
    setUser(null);
    setPantryItems([]);
    
  }

  const addPantryItem = (item) => setPantryItems((prev) => [...prev, item]);
  const removePantryItem = (id) => setPantryItems((prev) => prev.filter((i) => i.id !== id));
  const updatePantryItem = (id, updates) =>
    setPantryItems((prev) => prev.map((i) => (i.id === id ? { ...i, ...updates } : i)));
  const clearPantry = () => setPantryItems([]);

  return (
    <UserContext.Provider value={{ user, login, register, logout, 
        pantryItems,
        setPantryItems,
        addPantryItem,
        removePantryItem,
        updatePantryItem,
        clearPantry, }}>
      {children}
    </UserContext.Provider>
  );
};
