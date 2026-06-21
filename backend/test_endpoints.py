import requests
import json
import sys

# Forzar codificación utf-8 para la salida en consola si es posible
if sys.stdout.encoding != 'utf-8':
    try:
        # Reconfigurar stdout para usar utf-8
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Codificar a ascii reemplazando caracteres desconocidos si falla la salida utf-8
        print(text.encode(sys.stdout.encoding or 'ascii', errors='replace').decode(sys.stdout.encoding or 'ascii'))

def test_api():
    safe_print("=== PROBANDO ENDPOINT: /api/search ===")
    payload_search = {
        "query": "quiero buscar las tendencias de las maquinas médicas en ecógrafos",
        "count": 3
    }
    try:
        r = requests.post("http://localhost:8000/api/search", json=payload_search)
        safe_print(f"Status Code: {r.status_code}")
        data = r.json()
        safe_print(f"Búsqueda: {data.get('query')}")
        safe_print(f"Usando simulación: {data.get('using_mock')}")
        posts = data.get('posts', [])
        safe_print(f"Número de posts devueltos: {len(posts)}")
        for i, post in enumerate(posts):
            safe_print(f"  Post {i+1} por @{post['username']}: {post['caption'][:60]}... ({post['like_count']} likes)")
        
        safe_print("\n=== PROBANDO ENDPOINT: /api/analyze ===")
        payload_analyze = {
            "query": data.get('query'),
            "posts": posts
        }
        r_analyze = requests.post("http://localhost:8000/api/analyze", json=payload_analyze)
        safe_print(f"Status Code: {r_analyze.status_code}")
        analyze_data = r_analyze.json()
        report = analyze_data.get('report', '')
        safe_print(f"Reporte generado con éxito (Longitud: {len(report)} caracteres)")
        safe_print("\nPrimeras líneas del reporte:")
        safe_print("\n".join(report.split("\n")[:10]))
        
        safe_print("\n=== PROBANDO ENDPOINT: /api/chat ===")
        payload_chat = {
            "history": [
                {"role": "user", "content": "¿Cómo enfocarías una campaña para LinkedIn?"}
            ],
            "context": report
        }
        r_chat = requests.post("http://localhost:8000/api/chat", json=payload_chat)
        safe_print(f"Status Code: {r_chat.status_code}")
        chat_data = r_chat.json()
        safe_print(f"Respuesta del agente:\n{chat_data.get('reply')[:200]}...")
        
        safe_print("\n[OK] TODOS LOS ENDPOINTS FUNCIONAN CORRECTAMENTE!")
    except Exception as e:
        safe_print(f"[ERROR] Error al conectar o procesar API: {e}")

if __name__ == "__main__":
    test_api()
