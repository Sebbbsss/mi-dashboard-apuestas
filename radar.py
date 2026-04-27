import requests

# 1. TUS CREDENCIALES (Pon las tuyas aquí)
TOKEN = "8691766056:AAFtYdd5mo7lTz-eBJ_-UPCnpYu1AaAI5F4"
CHAT_ID = "5988002299"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    datos = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=datos)

def escanear_partidos():
    # 2. El diccionario con los códigos secretos de ESPN para las 5 grandes ligas
    ligas = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "eng.1",
        "🇪🇸 La Liga": "esp.1",
        "🇮🇹 Serie A": "ita.1",
        "🇩🇪 Bundesliga": "ger.1",
        "🇫🇷 Ligue 1": "fra.1"
    }
    
    mensaje_final = "🤖 *RADAR DE APUESTAS ACTIVADO* 🤖\n_Partidos programados para hoy:_\n\n"
    hay_partidos = False
    
    # 3. El bot visita la puerta trasera de ESPN para cada liga
    for nombre_liga, codigo in ligas.items():
        url_espn = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{codigo}/scoreboard"
        
        try:
            respuesta = requests.get(url_espn).json() # Extraemos la data pura (JSON)
            eventos = respuesta.get("events", [])
            
            if eventos:
                mensaje_final += f"🏆 *{nombre_liga}*\n"
                for evento in eventos:
                    # Extraemos el nombre del partido
                    nombre = evento["name"]
                    # Extraemos la hora (o el estado si ya se está jugando)
                    estado = evento["status"]["type"]["shortDetail"]
                    
                    mensaje_final += f"⚽ {nombre} _({estado})_\n"
                mensaje_final += "\n"
                hay_partidos = True
                
        except Exception as e:
            print(f"Error escaneando {nombre_liga}: {e}")

    # Si no hay fútbol hoy, que el bot nos lo diga
    if not hay_partidos:
        mensaje_final += "Hoy no hay partidos en las 5 grandes ligas. Día de descanso para la banca. 😴"
        
    return mensaje_final

# --- EJECUCIÓN DEL PROGRAMA ---
print("📡 Conectando con los satélites de ESPN...")
mensaje_partidos = escanear_partidos()

print("📱 Enviando el reporte a tu celular...")
enviar_telegram(mensaje_partidos)

print("✅ ¡Alerta entregada con éxito!")