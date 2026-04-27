import requests
import pandas as pd
from scipy.stats import poisson
import difflib
import glob

# --- 1. TUS CREDENCIALES DE TELEGRAM ---
TOKEN = "8691766056:AAFtYdd5mo7lTz-eBJ_-UPCnpYu1AaAI5F4"
CHAT_ID = "5988002299"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    if len(mensaje) > 4000:
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje[:4000], "parse_mode": "Markdown"})
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje[4000:], "parse_mode": "Markdown"})
    else:
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})

# --- 2. CARGA DE BASE DE DATOS AUTOMÁTICA ---
print("Cargando bases de datos locales...")
archivos_csv = glob.glob("*.csv")

if not archivos_csv:
    print("❌ ERROR: No se encontraron archivos CSV.")
    exit()

lista_tablas = []
traducciones = {'Home': 'HomeTeam', 'Away': 'AwayTeam', 'HG': 'FTHG', 'AG': 'FTAG'}

for archivo in archivos_csv:
    temp_df = pd.read_csv(archivo)
    temp_df.rename(columns=traducciones, inplace=True)
    lista_tablas.append(temp_df)

df = pd.concat(lista_tablas, ignore_index=True)
lista_equipos_csv = df['HomeTeam'].dropna().unique().tolist()

def buscar_equipo(nombre_espn):
    coincidencias = difflib.get_close_matches(nombre_espn, lista_equipos_csv, n=1, cutoff=0.4)
    if coincidencias:
        return coincidencias[0]
    return None

# --- 3. RADAR + MOTOR MATEMÁTICO ---
ligas = {
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "eng.1",
    "🇪🇸 La Liga": "esp.1",
    "🇮🇹 Serie A": "ita.1",
    "🇩🇪 Bundesliga": "ger.1",
    "🇫🇷 Ligue 1": "fra.1"
}

mensaje_final = "🤖 *REPORTE DE PROBABILIDADES Y VALOR* 🤖\n\n"
hay_partidos = False

print("📡 Analizando partidos y calculando porcentajes...")

for nombre_liga, codigo in ligas.items():
    url_espn = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{codigo}/scoreboard"
    try:
        respuesta = requests.get(url_espn).json()
        eventos = respuesta.get("events", [])
        
        if eventos:
            mensaje_final += f"🏆 *{nombre_liga}*\n"
            mensaje_final += "➖" * 15 + "\n"
            
            for evento in eventos:
                equipo_local_espn = evento["competitions"][0]["competitors"][0]["team"]["name"]
                equipo_vis_espn = evento["competitions"][0]["competitors"][1]["team"]["name"]
                horario = evento["status"]["type"]["shortDetail"]
                
                local_csv = buscar_equipo(equipo_local_espn)
                vis_csv = buscar_equipo(equipo_vis_espn)
                
                mensaje_final += f"⚽ *{equipo_local_espn} vs {equipo_vis_espn}* _{horario}_\n"
                
                if local_csv and vis_csv and local_csv != vis_csv:
                    # -- MOTOR DE GOLES (POISSON) --
                    prom_local = df[df['HomeTeam'] == local_csv]['FTHG'].mean()
                    prom_vis = df[df['AwayTeam'] == vis_csv]['FTAG'].mean()
                    
                    if pd.isna(prom_local) or pd.isna(prom_vis):
                        mensaje_final += "⚠️ _Sin datos suficientes._\n\n"
                        continue
                        
                    prob_1, prob_X, prob_2, prob_o15, prob_o25 = 0, 0, 0, 0, 0
                    
                    for gl in range(10):
                        for gv in range(10):
                            prob = poisson.pmf(gl, prom_local) * poisson.pmf(gv, prom_vis)
                            if gl > gv: prob_1 += prob
                            elif gl == gv: prob_X += prob
                            else: prob_2 += prob
                            if (gl + gv) > 1.5: prob_o15 += prob
                            if (gl + gv) > 2.5: prob_o25 += prob
                    
                    # Probabilidades directas
                    p_btts = (1 - poisson.pmf(0, prom_local)) * (1 - poisson.pmf(0, prom_vis)) * 100
                    p_o15 = prob_o15 * 100
                    p_o25 = prob_o25 * 100
                    
                    # Convertimos a Cuotas Justas
                    c1 = round(1 / prob_1, 2) if prob_1 > 0 else 0
                    cx = round(1 / prob_X, 2) if prob_X > 0 else 0
                    c2 = round(1 / prob_2, 2) if prob_2 > 0 else 0
                    co15 = round(100 / p_o15, 2) if p_o15 > 0 else 0
                    co25 = round(100 / p_o25, 2) if p_o25 > 0 else 0
                    cbtts = round(100 / p_btts, 2) if p_btts > 0 else 0
                    
                    # -- MOTOR DE ESTADÍSTICAS EXTRA --
                    txt_extra = ""
                    if 'HC' in df.columns:
                        c_l = df[df['HomeTeam'] == local_csv]['HC'].mean()
                        c_v = df[df['AwayTeam'] == vis_csv]['AC'].mean()
                        txt_extra += f"🚩 Cor: {round(c_l + c_v, 1)} | "
                    if 'HST' in df.columns:
                        t_l = df[df['HomeTeam'] == local_csv]['HST'].mean()
                        t_v = df[df['AwayTeam'] == vis_csv]['AST'].mean()
                        txt_extra += f"🥅 Arco: {round(t_l + t_v, 1)}"

                    # Ensamblaje visual
                    mensaje_final += f"📈 *1X2:* 1({round(prob_1*100,1)}% - {c1}) | X({round(prob_X*100,1)}% - {cx}) | 2({round(prob_2*100,1)}% - {c2})\n"
                    mensaje_final += f"🎯 *Goles:* +1.5({round(p_o15,1)}% - {co15}) | +2.5({round(p_o25,1)}% - {co25}) | BTTS({round(p_btts,1)}% - {cbtts})\n"
                    if txt_extra:
                        mensaje_final += f"📊 *Stats:* {txt_extra}\n"
                    mensaje_final += "\n"
                    
                else:
                    mensaje_final += "⚠️ _Equipos no encontrados en CSV._\n\n"
                    
            hay_partidos = True
            
    except Exception as e:
        print(f"Error procesando {nombre_liga}: {e}")

if not hay_partidos:
    mensaje_final = "🤖 Sin partidos relevantes hoy."

enviar_telegram(mensaje_final)
print("✅ ¡Reporte completo enviado con éxito!")