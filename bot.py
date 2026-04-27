import requests

# 1. Pega aquí los datos que obtuviste en Telegram
TOKEN = "8691766056:AAFtYdd5mo7lTz-eBJ_-UPCnpYu1AaAI5F4"
CHAT_ID = "5988002299"

def enviar_alerta_telegram(mensaje):
    """
    Esta función toma un texto y lo dispara directamente a tu celular
    usando la API oficial de Telegram.
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Preparamos los datos (parse_mode en Markdown permite usar negritas y cursivas)
    datos = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    # Disparamos el mensaje
    respuesta = requests.post(url, data=datos)
    
    if respuesta.status_code == 200:
        print("✅ ¡Mensaje enviado exitosamente a tu celular!")
    else:
        print("❌ Error al enviar el mensaje:", respuesta.text)

# 2. Creamos un mensaje de prueba con formato (simulando los partidos)
mensaje_prueba = """
🏆 *PARTIDOS DE HOY - TOP 5 LIGAS* 🏆

🏴󠁧󠁢󠁥󠁮󠁧󠁿 *Premier League:*
⚽ Arsenal vs Chelsea (14:00)
⚽ Man City vs Liverpool (16:30)

🇪🇸 *La Liga:*
⚽ Real Madrid vs Barcelona (16:00)

🇮🇹 *Serie A:*
⚽ Juventus vs Milan (13:45)

🤖 _Comunicación con Python establecida con éxito._
"""

# 3. Ejecutamos la función
enviar_alerta_telegram(mensaje_prueba)