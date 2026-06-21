import React from 'react';

const Loader = ({ message }) => {
  return (
    <div className="loader-container">
      <div className="loader-spinner"></div>
      <p className="loader-text">{message || "Analizando el mercado médico..."}</p>
    </div>
  );
};

export default Loader;
