import React, { useState, useEffect } from 'react';

const SettingsModal = ({ isOpen, onClose, onSave }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [instagramLoggedIn, setInstagramLoggedIn] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSettings();
    }
  }, [isOpen]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await fetch('http://localhost:8000/api/settings');
      if (res.ok) {
        const data = await res.json();
        setUsername(data.instagram_username || '');
        setInstagramLoggedIn(data.instagram_logged_in || false);
        // We do not fetch the actual password for security, we just indicate if it exists
        if (data.has_instagram_password) {
          setPassword('••••••••••••');
        }
        if (data.has_groq_key) {
          setApiKey('••••••••••••••••••••••••••••••••••••');
        }
      }
    } catch (err) {
      console.error("Error al obtener configuraciones:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatusMsg('Guardando configuración y validando...');
    
    // Si la contraseña o la api key son las de marcadores de posición, no las enviamos
    const payload = {
      instagram_username: username,
    };

    if (password !== '••••••••••••') {
      payload.instagram_password = password;
    }
    if (apiKey !== '••••••••••••••••••••••••••••••••••••') {
      payload.groq_api_key = apiKey;
    }

    try {
      const res = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setStatusMsg(data.instagram_status);
        if (data.instagram_status.includes('Logged In')) {
          setInstagramLoggedIn(true);
        } else {
          setInstagramLoggedIn(false);
        }
        onSave();
        setTimeout(() => {
          setStatusMsg('');
          onClose();
        }, 1500);
      } else {
        setStatusMsg('Error al guardar configuración.');
      }
    } catch (err) {
      console.error(err);
      setStatusMsg('Error de conexión con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>Configuraciones de API y Redes</h3>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Instagram Username</label>
              <input 
                type="text" 
                placeholder="ej: marketing_medico_user" 
                value={username} 
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Instagram Password</label>
              <input 
                type="password" 
                placeholder="Contraseña de Instagram" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)}
                onClick={() => password === '••••••••••••' && setPassword('')}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                {instagramLoggedIn ? 
                  "✅ Sesión iniciada correctamente en Instagram." : 
                  "ℹ️ Si se deja vacío, el sistema utilizará datos de tendencias simulados."}
              </p>
            </div>
            <div className="form-group" style={{ marginTop: '10px' }}>
              <label>Groq API Key</label>
              <input 
                type="password" 
                placeholder="gsk_..." 
                value={apiKey} 
                onChange={(e) => setApiKey(e.target.value)}
                onClick={() => apiKey === '••••••••••••••••••••••••••••••••••••' && setApiKey('')}
              />
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                Llave de API de Groq para habilitar el agente de marketing inteligente.
              </p>
            </div>

            {statusMsg && (
              <div style={{ 
                padding: '10px', 
                borderRadius: '8px', 
                backgroundColor: 'rgba(255,255,255,0.05)', 
                color: statusMsg.includes('Failed') || statusMsg.includes('Error') ? 'var(--accent-pink)' : 'var(--accent-primary)',
                fontSize: '0.85rem',
                textAlign: 'center'
              }}>
                {statusMsg}
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Guardando...' : 'Guardar y Validar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SettingsModal;
