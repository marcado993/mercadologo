# backend/agent/brain.py
import os
import logging
from typing import List, Dict, Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart

from .prompts import get_trend_analysis_prompt, get_agent_system_prompt
from .knowledge import format_posts_text, generate_mock_report, generate_mock_chat_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketingAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.client_configured = False
        self.agent = None
        
        if self.api_key:
            try:
                # Pydantic AI uses GROQ_API_KEY env var for Groq models (groq:llama-3.3-70b-versatile)
                os.environ["GROQ_API_KEY"] = self.api_key
                
                # Create the agent instance with the Groq model
                self.agent = Agent('groq:llama-3.3-70b-versatile', deps_type=str)
                
                # Define dynamic system prompt based on search context (deps)
                @self.agent.system_prompt
                def get_system_prompt(ctx: RunContext[str]) -> str:
                    return get_agent_system_prompt(ctx.deps)
                
                self.client_configured = True
                logger.info("Groq API (via Pydantic AI) configurada exitosamente.")
            except Exception as e:
                logger.error(f"Error al configurar Groq API (via Pydantic AI): {e}")

    def analyze_trends(self, query: str, posts: List[Dict[str, Any]]) -> str:
        """
        Analiza las publicaciones de Instagram y genera un reporte de marketing completo.
        Si la API Key no está configurada, genera un reporte simulado de alta calidad.
        """
        # Formatear posts de Instagram usando el módulo de conocimiento
        posts_text = format_posts_text(posts)
        
        # Generar prompt de análisis usando el módulo de prompts
        prompt = get_trend_analysis_prompt(query, posts_text)
        
        if self.client_configured and self.agent:
            try:
                logger.info("Generando reporte de marketing usando Pydantic AI...")
                result = self.agent.run_sync(prompt, deps="")
                return result.data
            except Exception as e:
                logger.error(f"Error al llamar a la API de Groq (Pydantic AI): {e}. Usando reporte simulado.")
                return generate_mock_report(query, posts)
        else:
            logger.info("Groq API no configurada o agente no inicializado. Generando reporte simulado de alta calidad.")
            return generate_mock_report(query, posts)

    def generate_chat_response(self, conversation_history: List[Dict[str, str]], last_search_context: str) -> str:
        """
        Maneja la conversación de seguimiento con el agente de marketing.
        Permite al usuario hacer preguntas sobre el reporte o refinar copys de marketing.
        """
        if not conversation_history:
            return "No hay historial de conversación."

        if self.client_configured and self.agent:
            try:
                # Convertir historial (excepto el último mensaje) al formato de Pydantic AI
                pydantic_history: List[ModelMessage] = []
                for msg in conversation_history[:-1]:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "user":
                        pydantic_history.append(ModelRequest(parts=[UserPromptPart(content=content)]))
                    elif role in ("agent", "model", "assistant"):
                        pydantic_history.append(ModelResponse(parts=[TextPart(content=content)]))

                # El último mensaje es la consulta actual
                last_msg = conversation_history[-1]
                prompt = last_msg["content"]

                logger.info(f"Generando respuesta de chat usando Pydantic AI para prompt: '{prompt[:40]}...'")
                
                result = self.agent.run_sync(
                    prompt,
                    deps=last_search_context,
                    message_history=pydantic_history
                )
                return result.data
            except Exception as e:
                logger.error(f"Error en chat de Groq (Pydantic AI): {e}")
                return generate_mock_chat_response(conversation_history, last_search_context)
        else:
            return generate_mock_chat_response(conversation_history, last_search_context)
