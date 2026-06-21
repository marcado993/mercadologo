# backend/agent/knowledge.py
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def format_posts_text(posts: List[Dict[str, Any]]) -> str:
    """
    Formatea las publicaciones de Instagram en texto estructurado para el prompt.
    """
    posts_text = ""
    for i, post in enumerate(posts):
        posts_text += f"\n--- Publicación {i+1} ---\n"
        posts_text += f"Usuario: @{post['username']}\n"
        posts_text += f"Engagement: {post['like_count']} Likes, {post['comment_count']} Comentarios\n"
        posts_text += f"Texto: {post['caption']}\n"
    return posts_text

def generate_mock_report(query: str, posts: List[Dict[str, Any]]) -> str:
    """Genera un reporte markdown de marketing preestablecido sumamente realista en español."""
    q = query.lower()
    equipment = "equipamiento médico inteligente"
    
    if "ultrasonido" in q or "ecograf" in q:
        equipment = "Ecógrafos Portátiles y Sistemas de Ultrasonido con IA"
        details = """
*   **Portabilidad Extrema (Point-of-Care Ultrasound - POCUS):** Los transductores inalámbricos que se conectan al smartphone o tableta están dominando la conversación. Facilitan diagnósticos rápidos en emergencias.
*   **Integración de Inteligencia Artificial:** Herramientas que pre-calculan fracciones de eyección o detectan bordes orgánicos automáticamente para reducir el error de medición del operador.
*   **Sondas Multicrecimiento:** Sondas que combinan funciones lineales, convexas y sectoriales en un solo dispositivo físico.
"""
        personas = """
*   **Persona 1: Dra. Mónica Ruiz (Ginecóloga y Dueña de Clínica Privada)**
    *   *Dolor:* Desea aumentar la rotación de pacientes sin perder precisión y ofrecer ecografías 5D/HD Live como diferencial comercial.
    *   *Solución:* Equipamiento con renderizado rápido y automatización de mediciones fetales.
*   **Persona 2: Ing. Manuel Soria (Director de Compras de Grupo Hospitalario)**
    *   *Dolor:* Presupuestos ajustados y necesidad de equipos duraderos con alto retorno de inversión.
    *   *Solución:* Sondas multifunción todo-en-uno que reducen la inversión en múltiples transductores individuales.
"""
        campaign = """
*   **Concepto:** "El Diagnóstico del Mañana en la Palma de tu Mano"
*   **Mensaje Clave:** Empoderar a los especialistas de la salud con imágenes de resolución hospitalaria en un formato ultra-portátil potenciado por IA.
*   **Propuesta de Copy para Email B2B:**
    *   **Asunto:** ¿Su clínica está perdiendo pacientes por lentitud en el diagnóstico? 🩺
    *   **Cuerpo:** Estimado/a Dr./Dra., en el mercado actual del cuidado de la salud, la rapidez diagnóstica define la preferencia de los pacientes. Le presentamos nuestro nuevo sistema de ultrasonido portátil. Agende una demostración virtual gratuita hoy mismo haciendo clic aquí.
"""
    elif "resonancia" in q or "mri" in q:
        equipment = "Resonadores Magnéticos de Alto Campo (3T) y Experiencia del Paciente"
        details = """
*   **Experiencia del Paciente (Claustrofobia y Ruido):** Se habla mucho de sistemas de reducción de ruido acústico (Silent MRI) y túneles más anchos (70cm open bore) con pantallas multimedia integradas.
*   **Velocidad de Escaneo Acelerada:** Algoritmos de reconstrucción de imágenes por aprendizaje profundo que reducen el tiempo del examen a la mitad (Deep Learning Reconstruction).
*   **Sistemas de Bajo Helio:** Equipos modernos que casi no consumen helio líquido para enfriar los imanes, bajando dramáticamente los costos operativos e instalación.
"""
        personas = """
*   **Persona 1: Dr. Carlos Espinoza (Jefe de Radiología)**
    *   *Dolor:* Cuellos de botella en la sala de espera y quejas frecuentes de pacientes claustrofóbicos que cancelan estudios.
    *   *Solución:* Escaneos rápidos y ambiente de confort mejorado.
*   **Persona 2: Lic. Laura Fernández (Administradora del Centro de Diagnóstico)**
    *   *Dolor:* Costos altísimos de mantenimiento y recarga de helio en resonadores antiguos.
    *   *Solución:* Tecnología "zero-boil-off" y alta rotación diaria de turnos.
"""
        campaign = """
*   **Concepto:** "Silencio, Confort y Claridad Absoluta"
*   **Mensaje Clave:** Romper el paradigma de que las resonancias son exámenes ruidosos y aterradores, garantizando la máxima resolución diagnóstica.
*   **Propuesta de Copy para Email B2B:**
    *   **Asunto:** Reduzca un 35% el ausentismo en sus estudios de Resonancia Magnética 🧠
    *   **Cuerpo:** Estimado Director, los exámenes cancelados por claustrofobia representan miles de dólares en pérdidas mensuales. Nuestro nuevo resonador magnético 3T de gran diámetro y tecnología de reducción de ruido resuelve este problema de raíz. Hablemos de financiamiento flexible.
"""
    else:
        equipment = "Equipos Médicos de Radiología Digital y Emergencias"
        details = """
*   **Baja Dosificación de Radiación:** La principal preocupación en posts de salud es la bioseguridad. Equipos de dosis ultra-baja son tendencia comercial.
*   **Conectividad Inalámbrica (PACS/DICOM):** Envío instantáneo de placas radiográficas directamente a los servidores del hospital para lectura remota.
*   **Monitoreo Remoto e IoT:** Dispositivos médicos que notifican de forma preventiva cuándo requieren mantenimiento, evitando paros imprevistos.
"""
        personas = """
*   **Persona 1: Dr. Sergio Lozano (Director Médico de Hospital)**
    *   *Dolor:* Tiempo de espera en emergencias por revelado e informes físicos.
    *   *Solución:* Sistemas digitales que muestran el resultado en pantalla en 3 segundos.
*   **Persona 2: Ing. Sofía Ruiz (Jefa de Ingeniería Clínica)**
    *   *Dolor:* Cumplir con regulaciones de bioseguridad y control estricto de dosis de radiación.
    *   *Solución:* Reportes de dosis automáticos integrados en el equipo.
"""
        campaign = """
*   **Concepto:** "Máxima Precisión, Mínima Exposición"
*   **Mensaje Clave:** Transición digital para clínicas que quieren proteger a sus pacientes y acelerar la atención de urgencia.
*   **Propuesta de Copy para Email B2B:**
    *   **Asunto:** La era del revelado químico ha terminado. Digitalice su sala de Rayos X ⚡
    *   **Cuerpo:** Estimado/a colega, agilice el flujo de su clínica. Nuestros digitalizadores directos reducen el tiempo de espera a solo segundos por paciente. Ahorre costos, espacio y proteja el ambiente. Solicite cotización con descuento corporativo.
"""

    report = f"""# 📈 Reporte de Tendencias y Campaña: {equipment}

## 1. Resumen Ejecutivo y Diagnóstico de la Tendencia
Hemos analizado las publicaciones más populares sobre la búsqueda **"{query}"** en canales del sector salud, ingeniería clínica y marketing de dispositivos. Se observa una clara tendencia hacia la **digitalización integrada**, la **reducción de tiempos de examen** y la **humanización de la atención médica**.

El mercado actual valora la autonomía del equipo y las integraciones con Inteligencia Artificial. Las marcas que comunican estos avances técnicos traduciéndolos a beneficios para el paciente (ej. menos dolor, menos radiación, menos tiempo en máquina) logran un engagement superior.

### Factores Clave de Tendencia:
{details}

---

## 2. Análisis de la Competencia y Engagement en Instagram
*   **Tono de la Comunicación:** Predomina un estilo educativo y de "detrás de escena". Los profesionales de la salud valoran ver el equipo real operando en una clínica en lugar de renders corporativos planos.
*   **Formatos Ganadores:** Carruseles que explican "Antes vs. Después" de adoptar la tecnología, y videos cortos (Reels) mostrando la interfaz táctil o la pantalla de resultados del equipo.
*   **Métricas de Engagement:** Los posts con testimonios directos de médicos que ya usan los equipos registran un **30% más de comentarios** solicitando información comercial y precios.
*   **Hashtags Estratégicos:** `#medtech #equiposmedicos #tecnologiamedica #hospitales #distribuidor #clinicas #diagnostico #doctorlife`

---

## 3. Perfil del Comprador (Buyer Personas)
{personas}

---

## 4. Estrategia de Campaña de Marketing Sugerida
{campaign}

---
*(Nota: Este reporte se generó utilizando el motor simulado avanzado de InstaMed Agent, ya que no se detectó una API key válida de Groq activa en los parámetros. Configura tu API key para obtener análisis en tiempo real de los posts reales.)*
"""
    return report

def generate_mock_chat_response(conversation_history: List[Dict[str, str]], last_search_context: str) -> str:
    """Genera respuestas simuladas de seguimiento para el chat basándose en el historial de la conversación."""
    last_user_message = conversation_history[-1]["content"].lower()
    
    if "email" in last_user_message or "correo" in last_user_message:
        return """Aquí tienes una alternativa de **Email de Ventas B2B** enfocado en un tono más técnico y con mayor énfasis en el retorno de inversión (ROI), ideal para presentárselo a Directores Financieros o Gerentes de Hospitales:

### Asunto: Optimice el ROI de su área de imagenología médica 📈

**Cuerpo:**
Estimado/a [Nombre del Administrador],

En la gestión hospitalaria, cada minuto de inactividad de un equipo médico representa una fuga de recursos. 

Nuestro nuevo sistema no solo reduce el tiempo de examen en un **40%**, lo que le permite atender hasta a **8 pacientes adicionales por jornada**, sino que reduce los costos de mantenimiento preventivo en un **20%** gracias a su sistema de auto-diagnóstico IoT.

Hemos preparado una calculadora financiera en Excel donde podrá estimar el tiempo de amortización del equipo según el volumen actual de su clínica.

¿Le interesaría una llamada de 10 minutos esta semana para hacer el cálculo personalizado?

Atentamente,
**[Tu Nombre]**
Director de Cuentas Médicas
"""
    elif "redes" in last_user_message or "instagram" in last_user_message or "reels" in last_user_message:
        return """Excelente pregunta. Para potenciar el contenido en **Instagram / LinkedIn**, aquí tienes un guion estructurado para un **Reel de 30 segundos** enfocado en médicos y dueños de clínicas:

### Guion de Reel: "El mito del diagnóstico lento"

*   **0-3 seg (Gancho Visual):** Muestra a un doctor frustrado mirando un monitor antiguo, o una sala de espera llena.
    *   *Texto en pantalla:* "¿Pacientes cansados de esperar?"
    *   *Voz en off:* "El tiempo de tus pacientes vale oro, pero el tuyo también."
*   **3-15 seg (El Contraste):** Transición rápida y brillante a un plano detalle del nuevo equipo médico. Una mano presiona un botón y la imagen médica aparece instantáneamente en alta definición.
    *   *Voz en off:* "Con el procesamiento automático por IA, obtienes mediciones automáticas precisas en menos de 5 segundos. Sin rodeos."
*   **15-25 seg (Demostración de beneficio):** Muestra la portabilidad del equipo o su pantalla táctil interactiva. El médico sonríe.
    *   *Voz en off:* "Portátil, higiénico y listo para compartir directo a la nube. Moderniza tu consulta hoy."
*   **25-30 seg (Llamado a la acción):** Pantalla final con tu logotipo y datos de contacto.
    *   *Texto en pantalla:* "Escribe 'DEMO' en los comentarios para enviarte los detalles."
    *   *Voz en off:* "Escribe DEMO en este video y recibe una cotización especial."
"""
    elif "precio" in last_user_message or "costo" in last_user_message:
        return """Cuando tratamos el tema de **precios** en marketing B2B para equipos médicos, la estrategia recomendada es **nunca publicar el precio de lista directamente en las redes sociales**. En su lugar, utilízalo como un gancho de conversión (Lead Magnet).

### Estrategia de Precios en Campañas:
1.  **En Redes Sociales:** Genera curiosidad sobre los planes de financiamiento (ej. "Equípate hoy y empieza a pagar en 90 días" o "Planes de renting desde $XXX/mes"). Esto atrae leads calificados sin asustar a los prospectos de menor presupuesto.
2.  **Llamado a la Acción:** Invita al usuario a recibir una cotización a la medida: *"El costo varía según los transductores y la garantía extendida que requieras. Déjanos tus datos para estructurar una oferta especial para tu clínica."*
3.  **Enfoque de Ventas:** Convierte la objeción del precio alto en una conversación sobre el costo por paciente (ej. *"Este ecógrafo se paga solo con realizar 3 ecografías al día"*).
"""
    else:
        return """Entendido. Como asesor de marketing médico, te sugiero que nos enfoquemos en los siguientes pasos para tu campaña:
1. **Definir el Canal Principal**: ¿Estaremos captando leads a través de Instagram Ads (ideal para médicos independientes y pequeñas clínicas) o por campañas de LinkedIn B2B / Correo Directo (ideal para directores y gerentes de hospitales)?
2. **Material de Apoyo**: Podemos redactar un folleto técnico (Ficha de Producto) o un script detallado para que tus ejecutivos de ventas lo usen al llamar a los prospectos interesados.

¿Qué parte de la estrategia te gustaría que redactemos o detallemos a continuación?"""
