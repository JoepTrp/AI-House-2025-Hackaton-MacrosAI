import React, { createContext, useState, useContext } from 'react';

// Create Context
const UserContext = createContext();

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

  const register = (email, password, username, { gender, age, weight, activityLevel, goal } ) => {
    //TODO: CALL API HERE
    if (email && password) {
      // keep user null intentionally
      setUser(username);
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
