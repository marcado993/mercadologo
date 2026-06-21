# backend/db.py
import os
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "instamed.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    logger.info(f"Inicializando base de datos SQLite en: {DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de Ajustes (configuraciones)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Tabla de Conversaciones (historial y reportes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            query TEXT,
            posts TEXT,      -- Guardado como JSON string
            report TEXT,
            messages TEXT,   -- Guardado como JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# --- Funciones para Ajustes (Settings) ---

def get_setting(key: str, default: str = "") -> str:
    """Obtiene un ajuste de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["value"]
    return default

def set_setting(key: str, value: str):
    """Guarda o actualiza un ajuste en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# --- Funciones para Conversaciones (Conversations) ---

def list_conversations() -> List[Dict[str, Any]]:
    """Obtiene todas las conversaciones guardadas, ordenadas por fecha de creación desc."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, posts, report, messages, created_at FROM conversations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        try:
            posts = json.loads(row["posts"]) if row["posts"] else []
        except Exception:
            posts = []
            
        try:
            messages = json.loads(row["messages"]) if row["messages"] else []
        except Exception:
            messages = []
            
        conversations.append({
            "id": row["id"],
            "query": row["query"],
            "posts": posts,
            "report": row["report"],
            "messages": messages,
            "created_at": row["created_at"]
        })
    return conversations

def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene una conversación específica por su ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, query, posts, report, messages, created_at FROM conversations WHERE id = ?", (conversation_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    try:
        posts = json.loads(row["posts"]) if row["posts"] else []
    except Exception:
        posts = []
        
    try:
        messages = json.loads(row["messages"]) if row["messages"] else []
    except Exception:
        messages = []
        
    return {
        "id": row["id"],
        "query": row["query"],
        "posts": posts,
        "report": row["report"],
        "messages": messages,
        "created_at": row["created_at"]
    }

def save_conversation(conversation_id: str, query: str, posts: List[Dict[str, Any]], report: str, messages: List[Dict[str, Any]]):
    """Guarda o actualiza una conversación en la base de datos."""
    posts_str = json.dumps(posts, ensure_ascii=False)
    messages_str = json.dumps(messages, ensure_ascii=False)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO conversations (id, query, posts, report, messages)
        VALUES (?, ?, ?, ?, ?)
    """, (conversation_id, query, posts_str, report, messages_str))
    conn.commit()
    conn.close()

def delete_conversation(conversation_id: str):
    """Elimina una conversación específica de la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()
