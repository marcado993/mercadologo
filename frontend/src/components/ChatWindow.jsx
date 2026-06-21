import React, { useState, useRef, useEffect } from 'react';
import logo from '../assets/instamed_logo.png';

const parseMarkdown = (text) => {
  if (!text) return { __html: "" };
  
  // Basic HTML escape first
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Format headers
  html = html.replace(/^### (.*$)/gim, '<h4>$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^# (.*$)/gim, '<h2>$1</h2>');
  
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Lists (simple conversion of lines starting with - or *)
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  
  // Replace line breaks with br
  html = html.replace(/\n/g, '<br />');

  // Group adjacent <li> tags into <ul> tags
  html = html.replace(/(<li>.*?<\/li>)+/gs, (match) => `<ul>${match}</ul>`);

  return { __html: html };
};

const ChatWindow = ({ 
  messages, 
  onSendMessage, 
  isLoading, 
  currentQuery,
  onToggleDashboard,
  isDashboardOpen,
  onOpenSettings,
  hasReport
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const suggestions = [
    {
      title: "Ecógrafos con IA 🩺",
      desc: "Analizar la portabilidad extrema y soporte clínico en ecógrafos.",
      query: "quiero buscar las tendencias de las maquinas médicas en ecógrafos y ver qué opina el sector"
    },
    {
      title: "Resonancia Magnética 3T 🧠",
      desc: "Revisar la experiencia de escaneo rápido y reducción de ruido.",
      query: "quiero buscar las tendencias de las maquinas médicas en resonancia magnética y ver la experiencia del paciente"
    },
    {
      title: "Radiografía Digital Directa 🦴",
      desc: "Tendencias en protección radiológica y flujo de emergencias.",
      query: "quiero buscar las tendencias de las maquinas médicas en rayos x digital y radiología portátil"
    },
    {
      title: "Monitores y Desfibriladores 🫀",
      desc: "Explorar DEA inteligentes y telemetría de cardiología.",
      query: "quiero buscar las tendencias de las maquinas médicas en desfibriladores externos automáticos y ecg"
    }
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput('');
  };

  const handleSuggestionClick = (query) => {
    if (isLoading) return;
    onSendMessage(query);
  };

  return (
    <div className="chat-section">
      <div className="chat-header">
        <div className="chat-header-info">
          <img src={logo} alt="InstaMed Logo" style={{ width: '28px', height: '28px', borderRadius: '50%', objectFit: 'cover', border: '1px solid rgba(255, 255, 255, 0.1)' }} />
          <h2>InstaMed 1.5 Flash ✦</h2>
          <p>
            <span className="pulse-dot"></span>
            {currentQuery ? `Búsqueda activa: "${currentQuery.length > 20 ? currentQuery.substring(0, 20) + '...' : currentQuery}"` : "Listo"}
          </p>
        </div>
        <div className="header-actions">
          {hasReport && (
            <button 
              className="header-btn"
              onClick={onToggleDashboard}
            >
              {isDashboardOpen ? "Ocultar Dashboard" : "Ver Dashboard"}
            </button>
          )}
          <button className="header-btn" onClick={onOpenSettings}>
            ⚙️ Ajustes
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <img src={logo} alt="InstaMed Logo" style={{ width: '72px', height: '72px', borderRadius: '18px', objectFit: 'cover', marginBottom: '8px', boxShadow: 'var(--shadow-glow)' }} />
            <h1>¿En qué puedo ayudarte hoy?</h1>
            <p>
              Explora tendencias de equipamiento médico y elabora campañas estratégicas al instante. 
              Escribe una consulta o haz clic en alguna sugerencia para comenzar.
            </p>
            <div className="suggestions-grid">
              {suggestions.map((s, idx) => (
                <div 
                  key={idx} 
                  className="suggestion-card"
                  onClick={() => handleSuggestionClick(s.query)}
                >
                  <h4>{s.title}</h4>
                  <p>{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role === 'user' ? 'user' : 'agent'}`}>
              <div className="avatar">
                {msg.role === 'user' ? '👤' : '🩺'}
              </div>
              <div 
                className="message-bubble"
                dangerouslySetInnerHTML={parseMarkdown(msg.content)}
              />
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="message-row agent">
            <div className="avatar">🩺</div>
            <div className="message-bubble">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <form onSubmit={handleSubmit} style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
          <div className="input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Pregúntale al agente de marketing médico..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="send-btn" 
              disabled={!input.trim() || isLoading}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="19" x2="12" y2="5"></line>
                <polyline points="5 12 12 5 19 12"></polyline>
              </svg>
            </button>
          </div>
        </form>
        <p className="input-disclaimer">
          InstaMed Agent puede cometer errores. Considera verificar la información comercial y médica importante.
        </p>
      </div>
    </div>
  );
};

export default ChatWindow;
