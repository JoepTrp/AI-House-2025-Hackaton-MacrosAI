import React, { createContext, useState, useContext } from 'react';

// Create Context
const UserContext = createContext();

// Hook for easy access
export const useUser = () => useContext(UserContext);

// Provider
export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({username:"User One"});

  const login = (email, password) => {
    //TODO: CALL API HERE 
    if (email && password) {
      setUser({ email });
    }
  };

  const register = (email, password) => {
    //TODO: CALL API HERE
    if (email && password) {
      setUser({ email });
    }
  };

  const logout = () => setUser(null);

  return (
    <UserContext.Provider value={{ user, login, register, logout }}>
      {children}
    </UserContext.Provider>
  );
};
