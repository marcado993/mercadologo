import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scraper import InstagramScraper
from agent import MarketingAgent
import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InstaMed Trends API", version="1.0.0")

# Permitir CORS para desarrollo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir al host del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales para los servicios
scraper = InstagramScraper()
agent = MarketingAgent()

# Modelos Pydantic para peticiones
class SearchRequest(BaseModel):
    query: str
    count: Optional[int] = 6

class AnalyzeRequest(BaseModel):
    query: str
    posts: List[Dict[str, Any]]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]
    context: str

class SettingsRequest(BaseModel):
    instagram_username: Optional[str] = ""
    instagram_password: Optional[str] = ""
    groq_api_key: Optional[str] = ""
    gemini_api_key: Optional[str] = ""

class ConversationRequest(BaseModel):
    id: str
    query: str
    posts: List[Dict[str, Any]]
    report: str
    messages: List[Dict[str, Any]]

# Funciones de utilidad para cargar/guardar configuración desde SQLite
def load_config():
    global scraper, agent
    try:
        username = db.get_setting("instagram_username", "")
        password = db.get_setting("instagram_password", "")
        
        # Cargar key de Groq, con fallback a Gemini
        groq_key = db.get_setting("groq_api_key", "")
        if not groq_key:
            groq_key = db.get_setting("gemini_api_key", "")
            
        # Fallback inicial a variables de entorno si la DB está vacía
        if not username and not password and not groq_key:
            username = os.getenv("INSTAGRAM_USERNAME", "")
            password = os.getenv("INSTAGRAM_PASSWORD", "")
            groq_key = os.getenv("GROQ_API_KEY", os.getenv("GEMINI_API_KEY", ""))
            
            # Guardar en base de datos para la posteridad
            if username: db.set_setting("instagram_username", username)
            if password: db.set_setting("instagram_password", password)
            if groq_key: db.set_setting("groq_api_key", groq_key)
            
        # Inicializar los servicios con los valores cargados
        scraper = InstagramScraper(username=username, password=password)
        agent = MarketingAgent(api_key=groq_key)
        logger.info("Configuración cargada desde SQLite correctamente.")
    except Exception as e:
        logger.error(f"Error al cargar configuración de SQLite: {e}")
        scraper = InstagramScraper()
        agent = MarketingAgent()

def save_config(config_data: dict):
    try:
        for k, v in config_data.items():
            db.set_setting(k, v)
        logger.info("Configuración guardada en SQLite.")
    except Exception as e:
        logger.error(f"Error al guardar configuración en SQLite: {e}")

# Inicializar configuración y base de datos al arrancar la app
@app.on_event("startup")
async def startup_event():
    db.init_db()
    load_config()

# Endpoints API
@app.get("/")
def read_root():
    return {"status": "online", "message": "InstaMed Trends API is running"}

@app.post("/api/search")
def search_trends(request: SearchRequest):
    """Busca posts reales de Instagram o simulados sobre la tendencia médica."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="La consulta de búsqueda no puede estar vacía")
    
    try:
        posts = scraper.search_instagram(request.query, count=request.count)
        return {
            "query": request.query,
            "posts": posts,
            "using_mock": not scraper.is_logged_in
        }
    except Exception as e:
        logger.error(f"Error en /api/search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
def analyze_trends(request: AnalyzeRequest):
    """Genera el reporte de marketing utilizando el agente LLM."""
    try:
        report = agent.analyze_trends(request.query, request.posts)
        return {
            "query": request.query,
            "report": report
        }
    except Exception as e:
        logger.error(f"Error en /api/analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat_agent(request: ChatRequest):
    """Endpoint interactivo para conversar con el agente de marketing."""
    try:
        # Convertir mensajes pydantic a diccionario
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        reply = agent.generate_chat_response(history_dicts, request.context)
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Error en /api/chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/settings")
def get_settings():
    """Retorna el estado actual de las configuraciones."""
    username = db.get_setting("instagram_username", os.getenv("INSTAGRAM_USERNAME", ""))
    password = db.get_setting("instagram_password", os.getenv("INSTAGRAM_PASSWORD", ""))
    groq_key = db.get_setting("groq_api_key", os.getenv("GROQ_API_KEY", ""))
    gemini_key = db.get_setting("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
    
    active_key = groq_key or gemini_key

    return {
        "instagram_username": username,
        "has_instagram_password": bool(password),
        "has_groq_key": bool(active_key),
        "has_gemini_key": bool(active_key),
        "instagram_logged_in": scraper.is_logged_in
    }

@app.post("/api/settings")
def update_settings(request: SettingsRequest):
    """Actualiza las configuraciones en memoria y las guarda en la base de datos SQLite."""
    global scraper, agent
    
    # Cargar valores actuales para no sobrescribir con campos vacíos
    current_username = db.get_setting("instagram_username", "")
    current_password = db.get_setting("instagram_password", "")
    current_groq_key = db.get_setting("groq_api_key", "")
    current_gemini_key = db.get_setting("gemini_api_key", "")

    username = request.instagram_username if request.instagram_username is not None else current_username
    password = request.instagram_password if request.instagram_password is not None else current_password
    
    groq_key = request.groq_api_key if request.groq_api_key is not None else current_groq_key
    gemini_key = request.gemini_api_key if request.gemini_api_key is not None else current_gemini_key

    if request.groq_api_key:
        groq_key = request.groq_api_key
    elif request.gemini_api_key:
        groq_key = request.gemini_api_key

    # Actualizar configuración persistente
    new_config = {
        "instagram_username": username,
        "instagram_password": password,
        "groq_api_key": groq_key,
        "gemini_api_key": gemini_key
    }
    save_config(new_config)

    # Re-instanciar los servicios con las nuevas credenciales
    scraper = InstagramScraper(username=username, password=password)
    agent = MarketingAgent(api_key=groq_key or gemini_key)

    instagram_status = "Not Logged In"
    if username and password:
        logger.info("Intentando iniciar sesión en Instagram con las nuevas credenciales...")
        logged_in = scraper.login()
        instagram_status = "Logged In" if logged_in else "Login Failed (Using Mock Fallback)"
    else:
        instagram_status = "Using Mock Mode (No credentials)"

    return {
        "success": True,
        "message": "Configuración actualizada con éxito.",
        "instagram_status": instagram_status,
        "has_groq_key": bool(groq_key or gemini_key),
        "has_gemini_key": bool(groq_key or gemini_key)
    }

# --- Endpoints de Historial persistidos en SQLite ---

@app.get("/api/history")
def get_history():
    """Obtiene todo el historial de conversaciones guardado en SQLite."""
    try:
        conversations = db.list_conversations()
        return conversations
    except Exception as e:
        logger.error(f"Error en GET /api/history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{conversation_id}")
def get_conversation_by_id(conversation_id: str):
    """Obtiene una conversación específica por su ID."""
    try:
        conv = db.get_conversation(conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        return conv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en GET /api/history/{conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/history")
def save_conversation_endpoint(request: ConversationRequest):
    """Guarda o actualiza una conversación en la base de datos."""
    try:
        db.save_conversation(
            conversation_id=request.id,
            query=request.query,
            posts=request.posts,
            report=request.report,
            messages=request.messages
        )
        return {"success": True, "message": "Conversación guardada con éxito."}
    except Exception as e:
        logger.error(f"Error en POST /api/history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{conversation_id}")
def delete_conversation_by_id(conversation_id: str):
    """Elimina una conversación específica de la base de datos."""
    try:
        db.delete_conversation(conversation_id)
        return {"success": True, "message": "Conversación eliminada con éxito."}
    except Exception as e:
        logger.error(f"Error en DELETE /api/history/{conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
