import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import TrendDashboard from './components/TrendDashboard';
import SettingsModal from './components/SettingsModal';
import Loader from './components/Loader';
import logo from './assets/instamed_logo.png';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [posts, setPosts] = useState(null);
  const [report, setReport] = useState(null);
  const [currentQuery, setCurrentQuery] = useState('');
  const [history, setHistory] = useState([]);
  const [activeHistoryId, setActiveHistoryId] = useState(null);
  
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState('');
  
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState({ instagram: false, groq: false });

  // Cargar estado inicial y configuraciones al montar
  useEffect(() => {
    checkApiStatus();
    loadHistoryFromDb();
  }, []);

  const checkApiStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/settings');
      if (res.ok) {
        const data = await res.json();
        setApiStatus({
          instagram: data.instagram_logged_in,
          groq: data.has_groq_key
        });
      }
    } catch (err) {
      console.error("Error al conectar con la API:", err);
    }
  };

  const loadHistoryFromDb = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/history');
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Error al cargar historial desde SQLite:", err);
    }
  };

  const saveConversationToDb = async (item) => {
    try {
      await fetch('http://localhost:8000/api/history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item)
      });
    } catch (err) {
      console.error("Error al guardar conversación en SQLite:", err);
    }
  };

  const handleDeleteHistory = async (e, id) => {
    e.stopPropagation(); // Evita que se seleccione la conversación al hacer clic en eliminar
    try {
      const res = await fetch(`http://localhost:8000/api/history/${id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        const updatedHistory = history.filter(item => item.id !== id);
        setHistory(updatedHistory);
        if (activeHistoryId === id) {
          handleNewChat();
        }
      }
    } catch (err) {
      console.error("Error al eliminar conversación de SQLite:", err);
    }
  };

  // Helper para verificar si es una consulta de busqueda
  const isSearchQuery = (text) => {
    const t = text.toLowerCase();
    return (
      t.includes("buscar las tendencias") || 
      t.includes("buscar tendencias") || 
      t.includes("analizar tendencias") || 
      t.includes("tendencias de")
    );
  };

  const handleSendMessage = async (text) => {
    // 1. Agregar mensaje de usuario al chat
    const newUserMessage = { role: 'user', content: text };
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    setIsLoading(true);

    if (isSearchQuery(text)) {
      // Flujo de Búsqueda e Instagram Scraping
      setLoadingMsg('Scrapeando publicaciones en Instagram...');
      setCurrentQuery(text);
      
      try {
        // A. Buscar en Instagram
        const searchRes = await fetch('http://localhost:8000/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: text, count: 6 })
        });
        
        if (!searchRes.ok) throw new Error('Error en la búsqueda de Instagram');
        const searchData = await searchRes.json();
        setPosts(searchData.posts);
        
        // B. Analizar con el agente
        setLoadingMsg('Generando análisis estratégico de marketing...');
        const analyzeRes = await fetch('http://localhost:8000/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: text, posts: searchData.posts })
        });

        if (!analyzeRes.ok) throw new Error('Error en el análisis de marketing');
        const analyzeData = await analyzeRes.json();
        setReport(analyzeData.report);

        // C. Agregar respuesta del agente
        const agentReply = {
          role: 'agent',
          content: `### ¡Búsqueda completada! 🎉\n\nHe recopilado publicaciones de Instagram relacionadas con tu consulta y he generado un reporte de marketing completo.\n\nPuedes ver las publicaciones y la estrategia comercial detallada en el **Dashboard de Tendencias** que acabo de abrir en el panel derecho.\n\n¿Tienes alguna pregunta sobre la campaña o quieres redactar un copy de ventas específico?`
        };
        
        const finalMessages = [...updatedMessages, agentReply];
        setMessages(finalMessages);
        setDashboardOpen(true);

        // D. Guardar en la base de datos SQLite
        const historyId = Date.now().toString();
        const newHistoryItem = {
          id: historyId,
          query: text,
          posts: searchData.posts,
          report: analyzeData.report,
          messages: finalMessages
        };
        
        const newHistory = [newHistoryItem, ...history];
        setHistory(newHistory);
        await saveConversationToDb(newHistoryItem);
        setActiveHistoryId(historyId);

      } catch (err) {
        console.error(err);
        setMessages([...updatedMessages, {
          role: 'agent',
          content: `❌ Hubo un error procesando tu consulta de búsqueda: ${err.message}. Por favor verifica que el backend de FastAPI esté encendido.`
        }]);
      } finally {
        setIsLoading(false);
        setLoadingMsg('');
      }

    } else {
      // Flujo de chat conversacional estándar
      setLoadingMsg('Consultando al agente de marketing...');
      
      try {
        const chatRes = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            history: updatedMessages,
            context: report || "No hay un reporte activo todavía."
          })
        });

        if (!chatRes.ok) throw new Error('Error en la respuesta del chat');
        const chatData = await chatRes.json();

        const agentReply = { role: 'agent', content: chatData.reply };
        const finalMessages = [...updatedMessages, agentReply];
        setMessages(finalMessages);

        // Actualizar los mensajes del item activo en SQLite
        if (activeHistoryId) {
          const activeItem = history.find(item => item.id === activeHistoryId);
          if (activeItem) {
            const updatedItem = { ...activeItem, messages: finalMessages };
            const updatedHistory = history.map(item => {
              if (item.id === activeHistoryId) {
                return updatedItem;
              }
              return item;
            });
            setHistory(updatedHistory);
            await saveConversationToDb(updatedItem);
          }
        }

      } catch (err) {
        console.error(err);
        setMessages([...updatedMessages, {
          role: 'agent',
          content: `❌ No se pudo conectar con el agente: ${err.message}`
        }]);
      } finally {
        setIsLoading(false);
        setLoadingMsg('');
      }
    }
  };

  const handleSelectHistory = (item) => {
    setActiveHistoryId(item.id);
    setCurrentQuery(item.query);
    setPosts(item.posts);
    setReport(item.report);
    setMessages(item.messages);
    setDashboardOpen(true);
  };

  const handleNewChat = () => {
    setActiveHistoryId(null);
    setCurrentQuery('');
    setPosts(null);
    setReport(null);
    setMessages([]);
    setDashboardOpen(false);
  };

  return (
    <div className="app-container">
      {/* Sidebar Izquierdo */}
      <div className="sidebar">
        <div className="sidebar-header">
          <img src={logo} alt="InstaMed Logo" style={{ width: '32px', height: '32px', borderRadius: '50%', objectFit: 'cover' }} />
          <div className="logo-text">InstaMed Agent</div>
        </div>

        <div className="sidebar-content">
          <button className="new-chat-btn" onClick={handleNewChat}>
            Nueva Búsqueda <span>+</span>
          </button>
          
          <div className="history-section">
            <div className="history-title">Búsquedas Recientes</div>
            {history.map((item) => (
              <div 
                key={item.id}
                className={`history-item ${activeHistoryId === item.id ? 'active' : ''}`}
                onClick={() => handleSelectHistory(item)}
                title={item.query}
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}
              >
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1 }}>
                  📝 {item.query.length > 20 ? item.query.substring(0, 20) + '...' : item.query}
                </span>
                <button 
                  onClick={(e) => handleDeleteHistory(e, item.id)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.8rem', padding: '2px 4px', marginLeft: '6px' }}
                  className="delete-history-btn"
                  title="Eliminar conversación"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="sidebar-footer">
          <div style={{ padding: '0 8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Instagram: <span style={{ color: apiStatus.instagram ? 'var(--accent-primary)' : 'var(--accent-pink)' }}>
              {apiStatus.instagram ? 'Conectado' : 'Modo Simulado'}
            </span>
          </div>
          <div style={{ padding: '0 8px', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Groq IA: <span style={{ color: apiStatus.groq ? 'var(--accent-primary)' : 'var(--accent-pink)' }}>
              {apiStatus.groq ? 'Configurado' : 'Modo Simulado'}
            </span>
          </div>
          
          <button className="footer-btn" onClick={() => setSettingsOpen(true)}>
            <span>⚙️</span> Ajustes / Credenciales
          </button>
        </div>
      </div>

      {/* Area Central de Chat */}
      <ChatWindow 
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading && !loadingMsg.includes('Scrapeando') && !loadingMsg.includes('generativo')}
        currentQuery={currentQuery}
        onToggleDashboard={() => setDashboardOpen(!dashboardOpen)}
        isDashboardOpen={dashboardOpen}
        onOpenSettings={() => setSettingsOpen(true)}
        hasReport={!!report}
      />

      {/* Dashboard Derecho (Tendencias e Instagram Posts) */}
      <TrendDashboard 
        posts={posts}
        report={report}
        isOpen={dashboardOpen}
        onClose={() => setDashboardOpen(false)}
      />

      {/* Modal de Configuración */}
      <SettingsModal 
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSave={() => {
          checkApiStatus();
        }}
      />

      {/* Loader Overlay para procesos pesados de Scraping/Análisis */}
      {isLoading && loadingMsg && (
        <div className="modal-overlay" style={{ zIndex: 105 }}>
          <div className="modal-content" style={{ border: 'none', background: 'transparent', boxShadow: 'none' }}>
            <Loader message={loadingMsg} />
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
