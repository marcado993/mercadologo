# InstaMed Agent (Mercadólogo) 📊🩺

InstaMed Agent es una aplicación web moderna y premium diseñada para el sector salud y de dispositivos médicos. Permite buscar tendencias comerciales directamente de publicaciones reales o simuladas de Instagram, y utiliza un agente inteligente de **Groq** (`llama-3.3-70b-versatile` a través de Pydantic AI) para generar análisis de mercado detallados, perfiles de comprador (buyer personas), propuestas de copies de email y redes sociales, así como gráficas interactivas del engagement de las publicaciones.

---

## 🛠️ Requisitos Previos

- **Docker** y **Docker Compose** (si deseas ejecutarlo en contenedores).
- **Python 3.10+** (si deseas correr el backend localmente).
- **Node.js 18+** y **npm** (si deseas correr el frontend localmente).

---

## 🐋 Ejecución con Docker (Recomendado) 🚀

La forma más rápida de levantar toda la arquitectura (Backend y Frontend) de forma aislada es utilizando **Docker Compose**.

1. **Clonar el Repositorio:**
   ```bash
   git clone https://github.com/marcado993/mercadologo.git
   cd mercadologo
   ```

2. **Configurar Variables de Entorno (Opcional):**
   Crea o edita el archivo de configuración en `backend/.env` (puedes tomar como base `backend/.env.template`). Si no deseas usar variables de entorno fijas, puedes configurar tus claves directamente en la interfaz gráfica web en la sección de **Ajustes**.
   ```env
   GROQ_API_KEY=gsk_tu_clave_de_groq_aqui
   INSTAGRAM_USERNAME=tu_usuario_de_instagram (opcional)
   INSTAGRAM_PASSWORD=tu_contraseña_de_instagram (opcional)
   ```

3. **Construir y Levantar los Contenedores:**
   Ejecuta el siguiente comando en la raíz del proyecto:
   ```bash
   docker compose up -d --build
   ```

4. **Acceder a la Aplicación:**
   - **Frontend (Interfaz Web):** Abre en tu navegador [http://localhost](http://localhost) (Puerto 80).
   - **Backend (API FastAPI):** Disponible en [http://localhost:8000](http://localhost:8000).
   - **Documentación de la API (Swagger):** Disponible en [http://localhost:8000/docs](http://localhost:8000/docs).

5. **Detener Contenedores:**
   ```bash
   docker compose down
   ```

---

## 💻 Ejecución en Entorno Local (Desarrollo)

Si prefieres correr los servicios de manera nativa en tu máquina para propósitos de desarrollo rápido:

### 1. Levantar el Backend (FastAPI)

1. Ve a la carpeta `backend`:
   ```bash
   cd backend
   ```
2. Crea un entorno virtual e instálalo:
   - **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     pip install -r requirements.txt
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -r requirements.txt
     ```
3. Configura tus credenciales en el archivo `.env` (usa `.env.template` como referencia).
4. Corre el servidor FastAPI en modo reload:
   ```bash
   python app.py
   ```
   El backend estará corriendo en `http://localhost:8000`.

### 2. Levantar el Frontend (React + Vite)

1. En una nueva terminal, ve a la carpeta `frontend`:
   ```bash
   cd frontend
   ```
2. Instala las dependencias:
   ```bash
   npm install
   ```
3. Corre el servidor de desarrollo:
   ```bash
   npm run dev
   ```
4. Abre tu navegador en la dirección que indique la consola (generalmente [http://localhost:5173](http://localhost:5173)).

---

## 🎨 Características Destacadas

- **Agente de Marketing en Salud:** Análisis avanzado de copys y comportamiento de compra médico con IA generativa (modelo `llama-3.3-70b-versatile` de Groq).
- **Dashboard Integrado:** Visualiza publicaciones scrapeadas y estadísticas del engagement de Instagram.
- **Gráficas Interactivas de Tendencia:** Reporte visual que calcula el engagement de forma comparativa, analiza el tono de la comunicación del mercado y extrae los hashtags más utilizados de manera dinámica.
- **Persistencia en SQLite:** Guarda todo tu historial de búsquedas y configuraciones de forma local y segura.
