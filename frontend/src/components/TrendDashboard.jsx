import React, { useState } from 'react';

const parseMarkdown = (text) => {
  if (!text) return { __html: "" };
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/\n/g, '<br />');
  html = html.replace(/(<li>.*?<\/li>)+/gs, (match) => `<ul>${match}</ul>`);
  
  return { __html: html };
};

const processChartsData = (posts) => {
  if (!posts || posts.length === 0) return null;

  // 1. Engagement Data
  const engagementData = posts.map(post => ({
    username: post.username,
    likes: post.like_count,
    comments: post.comment_count
  }));

  // 2. Hashtags Data
  const hashtagCounts = {};
  posts.forEach(post => {
    const hashtags = post.caption.match(/#\w+/g) || [];
    hashtags.forEach(tag => {
      const cleaned = tag.toLowerCase();
      hashtagCounts[cleaned] = (hashtagCounts[cleaned] || 0) + 1;
    });
  });
  const topHashtags = Object.entries(hashtagCounts)
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  // 3. Communication Tone Data
  let techCount = 0;
  let eduCount = 0;
  let commCount = 0;

  posts.forEach(post => {
    const caption = post.caption.toLowerCase();
    let isTech = /tecnolog|médic|radiolog|ingenier|manten|digital|sonda|equipo|mri|ecógra/.test(caption);
    let isEdu = /paciente|salud|cuidado|vida|bienestar|prevenc|doctor|sintoma/.test(caption);
    let isComm = /cotiz|demo|precio|descuent|vend|compr|adquir|comerc|oferta/.test(caption);

    if (!isTech && !isEdu && !isComm) {
      if (post.like_count > 400) isTech = true;
      else isEdu = true;
    }

    if (isTech) techCount++;
    if (isEdu) eduCount++;
    if (isComm) commCount++;
  });

  const total = techCount + eduCount + commCount || 1;
  const toneData = [
    { name: 'Técnico/Corporativo', count: techCount, percentage: Math.round((techCount / total) * 100) },
    { name: 'Educativo/Paciente', count: eduCount, percentage: Math.round((eduCount / total) * 100) },
    { name: 'Comercial/Ventas', count: commCount, percentage: Math.round((commCount / total) * 100) }
  ];

  return { engagementData, topHashtags, toneData };
};

const TrendChartsView = ({ posts }) => {
  const data = processChartsData(posts);
  if (!data) return <p style={{ color: 'var(--text-muted)' }}>No hay datos suficientes para graficar.</p>;

  const { engagementData, topHashtags, toneData } = data;
  const maxLikes = Math.max(...engagementData.map(d => d.likes)) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 1. Bar Chart for Engagement */}
      <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-color)' }}>
        <h4 style={{ fontSize: '0.9rem', color: 'var(--text-light)', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📈 Engagement Comparativo (Likes)</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Interacciones por post</span>
        </h4>
        <div style={{ display: 'flex', height: '180px', alignItems: 'flex-end', justifyContent: 'space-between', padding: '10px 10px 0 10px', gap: '16px', borderBottom: '1px solid var(--border-color)' }}>
          {engagementData.map((d, index) => {
            const heightPct = (d.likes / maxLikes) * 100;
            return (
              <div key={index} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, height: '100%', justifyContent: 'flex-end', position: 'relative' }} className="chart-bar-container">
                <div className="chart-tooltip" style={{
                  position: 'absolute',
                  bottom: `${heightPct + 5}%`,
                  background: 'rgba(0,0,0,0.85)',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '0.7rem',
                  whiteSpace: 'nowrap',
                  pointerEvents: 'none',
                  opacity: 0,
                  transition: 'opacity 0.2s',
                  boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
                  zIndex: 2
                }}>
                  {d.likes.toLocaleString()} Likes
                </div>
                <div style={{
                  width: '100%',
                  height: `${heightPct}%`,
                  background: 'linear-gradient(180deg, var(--accent-green) 0%, var(--accent-primary) 100%)',
                  borderRadius: '4px 4px 0 0',
                  minHeight: '4px',
                  cursor: 'pointer',
                  transition: 'height 0.8s ease-in-out'
                }} />
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '8px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', width: '100%', textAlign: 'center' }}>
                  @{d.username}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Communication Tone Distribution */}
      <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-color)' }}>
        <h4 style={{ fontSize: '0.9rem', color: 'var(--text-light)', marginBottom: '16px' }}>🎭 Distribución del Tono de Comunicación</h4>
        <div style={{ display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden', marginBottom: '16px', background: 'rgba(255,255,255,0.05)' }}>
          {toneData.map((t, index) => {
            const colors = ['var(--accent-primary)', 'var(--accent-green)', 'var(--accent-pink)'];
            if (t.percentage === 0) return null;
            return (
              <div 
                key={index} 
                style={{ 
                  width: `${t.percentage}%`, 
                  backgroundColor: colors[index], 
                  height: '100%', 
                  transition: 'width 0.8s ease-in-out' 
                }} 
                title={`${t.name}: ${t.percentage}%`}
              />
            );
          })}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {toneData.map((t, index) => {
            const colors = ['var(--accent-primary)', 'var(--accent-green)', 'var(--accent-pink)'];
            return (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: colors[index] }} />
                  <span style={{ color: 'var(--text-main)' }}>{t.name}</span>
                </div>
                <span style={{ color: 'var(--text-muted)', fontWeight: '600' }}>{t.percentage}% ({t.count})</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. Top Hashtags */}
      <div style={{ background: 'var(--bg-card)', padding: '16px', borderRadius: 'var(--border-radius-md)', border: '1px solid var(--border-color)' }}>
        <h4 style={{ fontSize: '0.9rem', color: 'var(--text-light)', marginBottom: '16px' }}>🏷️ Hashtags Más Populares</h4>
        {topHashtags.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {topHashtags.map((h, index) => {
              const maxCount = Math.max(...topHashtags.map(item => item.count)) || 1;
              const widthPct = (h.count / maxCount) * 100;
              return (
                <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span style={{ color: 'var(--accent-primary)', fontWeight: '500' }}>{h.tag}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{h.count} {h.count === 1 ? 'mención' : 'menciones'}</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${widthPct}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-green) 100%)',
                      borderRadius: '3px',
                      transition: 'width 0.8s ease-in-out'
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No se detectaron hashtags en las publicaciones.</p>
        )}
      </div>
    </div>
  );
};

const TrendDashboard = ({ posts, report, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('report'); // 'report', 'charts', or 'posts'

  if (!isOpen) return null;

  return (
    <div className="dashboard-panel">
      <div className="dashboard-header">
        <h3>
          <span>📊</span> Resumen y Publicaciones
        </h3>
        <button className="close-panel-btn" onClick={onClose}>&times;</button>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
          onClick={() => setActiveTab('report')}
        >
          Estrategia / Reporte
        </button>
        <button 
          className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
          onClick={() => setActiveTab('charts')}
        >
          Gráficas de Tendencia
        </button>
        <button 
          className={`tab-btn ${activeTab === 'posts' ? 'active' : ''}`}
          onClick={() => setActiveTab('posts')}
        >
          Instagram Posts ({posts?.length || 0})
        </button>
      </div>

      <div className="dashboard-content">
        {!posts && !report ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', textAlign: 'center', gap: '12px' }}>
            <span style={{ fontSize: '2.5rem' }}>🔍</span>
            <p>Realiza una búsqueda de tendencia para ver el análisis aquí.</p>
          </div>
        ) : (
          <>
            {activeTab === 'report' && (
              <div className="marketing-report-container" dangerouslySetInnerHTML={parseMarkdown(report)} />
            )}

            {activeTab === 'charts' && (
              <TrendChartsView posts={posts} />
            )}

            {activeTab === 'posts' && (
              <div className="posts-grid">
                {posts && posts.length > 0 ? (
                  posts.map((post, idx) => (
                    <div key={idx} className="post-card">
                       <div className="post-user">
                         <img 
                           className="post-avatar" 
                           src={post.profile_pic || "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=50"} 
                           alt={post.username} 
                         />
                         <div className="post-user-info">
                           <h5>@{post.username}</h5>
                           <span>{post.full_name}</span>
                         </div>
                       </div>
                       
                       {post.image_url && (
                         <img className="post-image" src={post.image_url} alt="Medical equipment post" />
                       )}
                       
                       <div className="post-actions">
                         <div className="post-action-item">
                           <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                             <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                           </svg>
                           <span>{post.like_count.toLocaleString()}</span>
                         </div>
                         <div className="post-action-item comments">
                           <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                             <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                           </svg>
                           <span>{post.comment_count.toLocaleString()}</span>
                         </div>
                       </div>

                       <div className="post-caption">
                         {post.caption}
                       </div>

                       <div className="post-source">
                         <span className={`source-badge ${post.is_real ? 'real' : 'mock'}`}>
                           {post.is_real ? 'Real Instagram' : 'Simulado'}
                         </span>
                         <a 
                           className="view-link" 
                           href={post.post_url} 
                           target="_blank" 
                           rel="noopener noreferrer"
                         >
                           Ver original ↗
                         </a>
                       </div>
                    </div>
                  ))
                ) : (
                  <p style={{ color: 'var(--text-muted)' }}>No se encontraron publicaciones.</p>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default TrendDashboard;
