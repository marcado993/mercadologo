import os
import json
import random
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    PleaseWaitFewMinutes,
    ChallengeRequired,
    FeedbackRequired,
    ClientError
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSION_FILE = Path(__file__).parent / "session.json"

# Unsplash image URLs of medical equipment and hospital scenes for professional looks
MEDICAL_IMAGES = {
    "ultrasound": [
        "https://images.unsplash.com/photo-1579684389782-64d84b5e905d?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=800&auto=format&fit=crop&q=80"
    ],
    "mri": [
        "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1530026405186-ed1ea0ac7a63?w=800&auto=format&fit=crop&q=80"
    ],
    "radiography": [
        "https://images.unsplash.com/photo-1551076805-e1869033e561?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&auto=format&fit=crop&q=80"
    ],
    "cardio": [
        "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1603398938378-e54eab446dde?w=800&auto=format&fit=crop&q=80"
    ],
    "general": [
        "https://images.unsplash.com/photo-1584515901367-f1c2a1cf553f?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1527613426441-4da17471b66d?w=800&auto=format&fit=crop&q=80"
    ]
}

class InstagramScraper:
    def __init__(self, username=None, password=None):
        self.cl = Client()
        self.username = username
        self.password = password
        self.is_logged_in = False
        # Configurar retardos automáticos entre peticiones
        self.cl.delay_range = [2, 7]
        
    def login(self) -> bool:
        if not self.username or not self.password:
            logger.info("No se proporcionaron credenciales de Instagram. Usando modo simulado.")
            return False
            
        try:
            # 1. Configurar retardos aleatorios entre peticiones en instagrapi
            self.cl.delay_range = [2, 7]
            
            # 2. Intentar cargar sesión guardada para evitar baneos
            if SESSION_FILE.exists():
                try:
                    logger.info("Cargando sesión guardada de Instagram...")
                    self.cl.load_settings(SESSION_FILE)
                    
                    # Intentar iniciar sesión usando la sesión persistida
                    self.cl.login(self.username, self.password)
                    
                    # Realizar una llamada de prueba ligera para verificar si la sesión sigue siendo válida
                    logger.info("Verificando validez de la sesión cargada con una llamada ligera...")
                    self.cl.get_timeline_feed()
                    
                    self.is_logged_in = True
                    logger.info("Inicio de sesión exitoso con sesión persistida y válida.")
                    return True
                except LoginRequired:
                    logger.warning("La sesión persistida ha expirado (LoginRequired). Re-iniciando sesión limpia...")
                    # Re-instanciar el cliente para limpiar cualquier estado
                    self.cl = Client()
                    self.cl.delay_range = [3, 8]
                except Exception as e:
                    logger.warning(f"No se pudo usar la sesión persistida: {e}. Re-iniciando sesión limpia...")
                    self.cl = Client()
                    self.cl.delay_range = [3, 8]
            
            # 3. Login limpio con usuario y contraseña
            logger.info(f"Iniciando sesión limpia en Instagram con usuario: {self.username}...")
            # Añadir un pequeño retardo antes de iniciar sesión por seguridad
            time.sleep(random.uniform(2, 5))
            self.cl.login(self.username, self.password)
            self.is_logged_in = True
            
            # Guardar la nueva sesión
            self.cl.dump_settings(SESSION_FILE)
            logger.info("Inicio de sesión limpia exitoso y sesión guardada en disco.")
            return True
        except (PleaseWaitFewMinutes, FeedbackRequired) as e:
            logger.error(f"Bloqueo temporal o rate limit de Instagram durante el inicio de sesión: {e}")
            self.is_logged_in = False
            return False
        except ChallengeRequired as e:
            logger.error(f"Verificación requerida (Desafío/2FA/Checkpoint) por Instagram: {e}")
            self.is_logged_in = False
            return False
        except Exception as e:
            logger.error(f"Error inesperado al iniciar sesión en Instagram: {e}")
            self.is_logged_in = False
            return False

    def search_instagram(self, query: str, count: int = 6) -> list:
        """
        Busca publicaciones en Instagram relacionadas con la consulta.
        Si las credenciales fallan o no están configuradas, recurre a datos simulados de alta calidad.
        """
        if not self.is_logged_in:
            # Intentamos iniciar sesión primero si tenemos credenciales
            if self.username and self.password:
                self.login()
                
        # Si logramos iniciar sesión, intentamos hacer scraping real
        if self.is_logged_in:
            try:
                # Extraemos un hashtag coherente a partir de la consulta
                hashtag = self._extract_hashtag(query)
                
                # Introducir retardo humano aleatorio antes de la consulta
                delay = random.uniform(3, 8)
                logger.info(f"Esperando {delay:.2f} segundos antes de hacer la búsqueda para evitar rate-limits...")
                time.sleep(delay)
                
                logger.info(f"Buscando posts reales para el hashtag: #{hashtag}")
                medias = self.cl.hashtag_medias_top(hashtag, amount=count)
                
                results = []
                for media in medias:
                    results.append({
                        "id": media.id,
                        "username": media.user.username,
                        "full_name": media.user.full_name,
                        "profile_pic": str(media.user.profile_pic_url) if media.user.profile_pic_url else "",
                        "caption": media.caption_text or "",
                        "like_count": media.like_count,
                        "comment_count": media.comment_count,
                        "created_at": media.taken_at.isoformat() if media.taken_at else datetime.now().isoformat(),
                        "image_url": str(media.thumbnail_url) if media.thumbnail_url else (str(media.resources[0].thumbnail_url) if media.resources else ""),
                        "post_url": f"https://www.instagram.com/p/{media.code}/",
                        "is_real": True
                    })
                return results
            except LoginRequired:
                logger.error("La sesión de Instagram ha expirado durante la búsqueda. Invalidando estado de sesión.")
                self.is_logged_in = False
                # Eliminar archivo de sesión si no sirve
                if SESSION_FILE.exists():
                    try:
                        SESSION_FILE.unlink()
                    except Exception:
                        pass
                return self.generate_mock_posts(query, count)
            except PleaseWaitFewMinutes as e:
                logger.warning(f"Instagram ha impuesto un rate limit temporal (PleaseWaitFewMinutes): {e}. Usando fallback simulado.")
                return self.generate_mock_posts(query, count)
            except ChallengeRequired as e:
                logger.warning(f"Desafío requerido por Instagram (ChallengeRequired): {e}. Usando fallback simulado.")
                self.is_logged_in = False
                return self.generate_mock_posts(query, count)
            except FeedbackRequired as e:
                logger.warning(f"Feedback requerido (acción bloqueada temporalmente) por Instagram: {e}. Usando fallback simulado.")
                return self.generate_mock_posts(query, count)
            except Exception as e:
                logger.error(f"Error durante el scraping real de Instagram: {e}. Usando fallback simulado.")
                # Fallback al modo mock si el scraping real falla (muy común por rate limits de IG)
                return self.generate_mock_posts(query, count)
        else:
            logger.info("Usando datos simulados enriquecidos para la consulta.")
            return self.generate_mock_posts(query, count)

    def _extract_hashtag(self, query: str) -> str:
        """Extrae el hashtag más relevante basado en palabras clave en la consulta."""
        q = query.lower()
        if "ultrasonido" in q or "ecograf" in q:
            return "ecografia"
        elif "resonancia" in q or "mri" in q:
            return "resonanciamagnetica"
        elif "rayos" in q or "radiograf" in q or "x-ray" in q:
            return "radiologia"
        elif "cardi" in q or "desfibrilador" in q or "electrocardiograma" in q:
            return "cardiologia"
        elif "odontolog" in q or "dental" in q:
            return "odontologia"
        else:
            return "equipomedico"

    def generate_mock_posts(self, query: str, count: int = 6) -> list:
        """Genera publicaciones simuladas realistas sobre tecnología médica en español."""
        q = query.lower()
        
        # Determinar el tipo de máquina médica de la consulta
        machine_type = "general"
        if "ultrasonido" in q or "ecograf" in q:
            machine_type = "ultrasound"
        elif "resonancia" in q or "mri" in q:
            machine_type = "mri"
        elif "rayos" in q or "radiograf" in q or "x-ray" in q:
            machine_type = "radiography"
        elif "cardi" in q or "desfibrilador" in q or "electrocardiograma" in q:
            machine_type = "cardio"

        # Creadores de contenido simulados
        accounts = [
            {"username": "medtech_latam", "full_name": "MedTech Latinoamérica", "profile_pic": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=100"},
            {"username": "radiologia_avanzada", "full_name": "Dra. Valeria Gómez | Radióloga", "profile_pic": "https://images.unsplash.com/photo-1594824813573-246434de83fb?w=100"},
            {"username": "equipos_medicos_pro", "full_name": "Suministros Médicos Profesionales", "profile_pic": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=100"},
            {"username": "cardiocare_clinic", "full_name": "CardioCare Centro Médico", "profile_pic": "https://images.unsplash.com/photo-1579684389782-64d84b5e905d?w=100"},
            {"username": "hospital_innovacion", "full_name": "Hospital del Futuro", "profile_pic": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=100"},
            {"username": "ingenieria_clinica_col", "full_name": "Ing. Carlos Mendoza", "profile_pic": "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=100"}
        ]

        # Catálogo de copys de marketing simulados por tipo de máquina
        captions_db = {
            "ultrasound": [
                "¡La revolución en diagnóstico por imagen! Presentamos el nuevo Ecógrafo Portátil con Inteligencia Artificial. Diagnósticos más rápidos, mayor nitidez y conectividad en la nube para compartir resultados en tiempo real. 🏥✨\n\n#ecografo #ultrasonido #medicina #tecnologia #salud #marketingmedico #medtech #clinic",
                "Hoy en nuestra clínica probamos la sonda transductora inalámbrica de última generación. Increíble cómo facilita el examen rápido a pie de cama del paciente. La portabilidad es la tendencia número 1 en 2026. 🩺💡\n\n#ultrasonido #ecografia #ginecologia #pediatria #innovacionmedica #salud #doctor",
                "¿Sabías que la IA en ecografía reduce el tiempo de escaneo en un 40%? La detección automática de anomalías está ayudando a los médicos a ser más precisos. Un gran paso para la medicina preventiva. 🤖📈\n\n#ecografo #inteligenciaartificial #radiologia #diagnostico #medicina #hospitales #tecnologia"
            ],
            "mri": [
                "Rediseñando la experiencia del paciente: Resonancia Magnética 3T de gran diámetro. Menos ruido, menos claustrofobia, y una velocidad de escaneo impresionante. ¡Los pacientes lo adoran! 🧠💪\n\n#resonancia #mri #radiologia #salud #bienestar #tecnologiamedica #hospital #diagnostico",
                "Instalación exitosa del nuevo resonador magnético inteligente en nuestro departamento de imagenología. Reducción de artefactos por movimiento gracias al software predictivo. Calidad de imagen superior para decisiones clínicas críticas. 🏥🔬\n\n#resonancia #mri #neurologia #radiologo #ingenieriamedica #equiposmedicos #oncologia",
                "Tendencias en salud: El auge de los resonadores magnéticos modulares de bajo helio. Más sostenibles con el medio ambiente y menores costos de mantenimiento. La ecología también llega a la alta tecnología médica. 🌿⚡\n\n#mri #sustentabilidad #medicinaverde #tecnologia #radiologia #clinica #marketinghospitalario"
            ],
            "radiography": [
                "La era digital llegó para quedarse. Descubre nuestro sistema de Radiografía Digital Directa de baja dosis. Protegemos al paciente reduciendo hasta un 50% la radiación sin perder resolución de imagen. 🦴🛡️\n\n#radiologia #rayosx #medicina #salud #proteccionradiologica #clinica #diagnostico #tecnologia",
                "Equipo de Rayos X portátil y robusto, ideal para emergencias y unidades de cuidados intensivos. Batería de larga duración y transmisión inalámbrica directa a la estación de trabajo médica. 🚑📡\n\n#rayosx #urgencias #uci #traumatologia #medtech #salud #hospitales #distribuidormedico",
                "Renovando el área de imagenología. ¿Por qué cambiar a radiología digital? Mayor flujo de pacientes, eliminación de químicos contaminantes de revelado y almacenamiento inmediato en el PACS. 💻🔋\n\n#radiografia #digital #saludambiental #pacs #medicina #innovacion #marketingmedico"
            ],
            "cardio": [
                "Segundos que salvan vidas: La importancia de contar con Desfibriladores Externos Automáticos (DEA) inteligentes y conectados en espacios públicos y corporativos. Fácil guía por voz e informes automáticos de estado. 🫀⚡\n\n#desfibrilador #cardio #dea #urgencias #reanimacion #salud #primerosauxilios #empresa",
                "Electrocardiógrafo digital de 12 canales con interpretación automática basada en machine learning. Portátil, intuitivo y con batería recargable. Analizando el ritmo cardíaco en segundos. 📈❤️\n\n#electrocardiograma #ecg #cardiologia #medico #saludcardiovascular #diagnostico #medtech",
                "Monitores multiparámetros con alertas inteligentes y conectividad Bluetooth para telemetría continua de pacientes cardíacos. La monitorización remota es el estándar de oro actual. 🏥📲\n\n#cardiologia #monitormedico #salud #uci #clinica #hospital #telemedicina #tecnologia"
            ],
            "general": [
                "La digitalización del equipamiento médico está transformando los hospitales de todo el mundo. Desde la IA en diagnóstico hasta la telemedicina integrada. ¿Tu clínica ya está lista para dar el salto? 🏥🚀\n\n#equipomedico #tecnologia #salud #hospital #telemedicina #marketingmedico #medicina #innovacion",
                "Las 3 tendencias clave en la compra de tecnología médica este año: 1) Inteligencia Artificial nativa, 2) Dispositivos portátiles/inalámbricos, 3) Sistemas eco-eficientes. 📊🌱\n\n#marketingmedico #tendencias #medtech #hospitales #clinicas #distribuidormedico #salud",
                "Hablamos sobre cómo la ergonomía de los nuevos equipos de quirófano reduce la fatiga de los cirujanos en cirugías de larga duración. La salud del personal médico también importa. 🩺✨\n\n#quirofano #cirujano #ergonomia #medicina #hospital #salud #tecnologiamedica #equipos"
            ]
        }

        # Generar los posts simulados aleatorios basados en la base de datos
        results = []
        selected_captions = captions_db.get(machine_type, captions_db["general"])
        selected_images = MEDICAL_IMAGES.get(machine_type, MEDICAL_IMAGES["general"])

        for i in range(count):
            account = accounts[i % len(accounts)]
            caption = selected_captions[i % len(selected_captions)]
            # Reemplazar ciertos hashtags o palabras para hacerlos coincidir con la consulta si es específica
            if "ecograf" in q and machine_type == "general":
                caption = caption.replace("#equipomedico", "#ecografo")
            
            image_url = selected_images[i % len(selected_images)]
            likes = random.randint(120, 2500)
            comments = random.randint(10, 180)
            days_ago = random.randint(1, 15)
            created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
            post_id = f"mock_post_{machine_type}_{i}_{random.randint(1000, 9999)}"

            results.append({
                "id": post_id,
                "username": account["username"],
                "full_name": account["full_name"],
                "profile_pic": account["profile_pic"],
                "caption": caption,
                "like_count": likes,
                "comment_count": comments,
                "created_at": created_at,
                "image_url": image_url,
                "post_url": f"https://www.instagram.com/p/{post_id}/",
                "is_real": False
            })
        
        # Mezclar ligeramente para que no parezca estructurado de forma fija
        random.shuffle(results)
        return results
