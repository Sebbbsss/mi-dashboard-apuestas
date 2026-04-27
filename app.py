import streamlit as st
import pandas as pd
from scipy.stats import poisson

# --- FUNCIONES AUXILIARES ---
def cuota_justa(probabilidad):
    return round(100 / probabilidad, 2) if probabilidad > 0 else 0

def evaluar_valor(probabilidad, cuota_casa):
    # Solo evalúa si el usuario ingresó una cuota mayor a 1.0
    if cuota_casa > 1.0:
        ev = ((probabilidad / 100) * cuota_casa) - 1
        if ev > 0:
            st.success(f"✅ VALOR: +{round(ev*100, 2)}%")
        else:
            st.error(f"❌ Sin valor: {round(ev*100, 2)}%")

# 1. TÍTULO Y DISEÑO DE LA PÁGINA
st.set_page_config(page_title="Dashboard Profesional de Apuestas", layout="wide")
st.title("🏆 Dashboard Maestro: Value Betting & Stats")
st.markdown("Sube tus bases de datos, elige los equipos e ingresa las cuotas de tu casa de apuestas.")

# 2. CARGADOR DE ARCHIVOS
archivos_subidos = st.file_uploader("📂 Sube tus bases de datos (Ej: E0.csv, SP1.csv, ARG.csv)", type=["csv"], accept_multiple_files=True)

if archivos_subidos:
    lista_tablas = [pd.read_csv(archivo) for archivo in archivos_subidos]
    datos_premier = pd.concat(lista_tablas, ignore_index=True)
    
    # --- EL TRADUCTOR UNIVERSAL ---
    # Traduce columnas de otras ligas para que el código las entienda
    traducciones = {
        'Home': 'HomeTeam',
        'Away': 'AwayTeam',
        'HG': 'FTHG',  
        'AG': 'FTAG'   
    }
    datos_premier.rename(columns=traducciones, inplace=True)
    
    # Preparamos las tarjetas si es que existen en esta liga
    if 'HY' in datos_premier.columns and 'AY' in datos_premier.columns:
        datos_premier['Total_Yellows'] = datos_premier['HY'] + datos_premier['AY']
        
    # Verificamos que la traducción funcionó y existe 'HomeTeam'
    if 'HomeTeam' not in datos_premier.columns:
        st.error("🚨 ERROR: El archivo subido tiene nombres de columnas desconocidos. Abre el CSV en Excel y verifica cómo se llaman las columnas de equipo local y visitante.")
        st.stop() # Detiene la ejecución aquí para que no colapse la app
        
    st.success(f"✅ ¡Bases de datos cargadas! {len(datos_premier)} partidos listos.")
    
    # 3. MENÚS DESPLEGABLES INTELIGENTES
    lista_equipos = sorted(datos_premier['HomeTeam'].dropna().unique())
    lista_arbitros = sorted(datos_premier['Referee'].dropna().unique()) if 'Referee' in datos_premier.columns else []
    opciones_arbitros = ["Ninguno"] + list(lista_arbitros)

    col1, col2, col3 = st.columns(3)
    with col1:
        local = st.selectbox("🏠 Equipo Local", lista_equipos)
    with col2:
        visitante = st.selectbox("✈️ Equipo Visitante", lista_equipos)
    with col3:
        arbitro = st.selectbox("⚽ Árbitro (Opcional)", opciones_arbitros)

    # 4. EL MOTOR EN TIEMPO REAL
    if local != visitante:
        st.divider()
        st.subheader(f"📊 Análisis en Vivo: {local.upper()} vs {visitante.upper()}")
        
        # --- MATEMÁTICA DE GOLES (Siempre disponible en todas las ligas) ---
        prom_local = datos_premier[datos_premier['HomeTeam'] == local]['FTHG'].mean()
        prom_vis = datos_premier[datos_premier['AwayTeam'] == visitante]['FTAG'].mean()
        
        prob_1, prob_X, prob_2 = 0, 0, 0
        prob_u15, prob_u25, prob_u35 = 0, 0, 0
        
        for gl in range(10):
            for gv in range(10):
                prob_m = poisson.pmf(gl, prom_local) * poisson.pmf(gv, prom_vis)
                tot = gl + gv
                
                # 1X2
                if gl > gv: prob_1 += prob_m
                elif gl == gv: prob_X += prob_m
                else: prob_2 += prob_m
                
                # Under (Los goles totales son menores a la línea)
                if tot < 1.5: prob_u15 += prob_m
                if tot < 2.5: prob_u25 += prob_m
                if tot < 3.5: prob_u35 += prob_m
                    
        # Conversión a porcentajes
        prob_1, prob_X, prob_2 = prob_1 * 100, prob_X * 100, prob_2 * 100
        prob_u15, prob_u25, prob_u35 = prob_u15 * 100, prob_u25 * 100, prob_u35 * 100
        
        # Los Over son simplemente el 100% menos el Under
        prob_o15, prob_o25, prob_o35 = 100 - prob_u15, 100 - prob_u25, 100 - prob_u35
        
        # Ambos Marcan (Probabilidad de que NO sea cero, multiplicada por ambos)
        prob_anota_local = (1 - poisson.pmf(0, prom_local)) * 100
        prob_anota_vis = (1 - poisson.pmf(0, prom_vis)) * 100
        prob_btts = (prob_anota_local / 100) * (prob_anota_vis / 100) * 100

        # --- INTERFAZ OVER/UNDER ---
        st.markdown("### 📈 Mercado de Total de Goles (Over/Under)")
        ou1, ou2, ou3 = st.columns(3)
        
        with ou1:
            st.markdown("#### Línea 1.5 (Favorita)")
            st.metric("Más de 1.5 Goles", f"{round(prob_o15, 1)}%", f"Cuota Justa: {cuota_justa(prob_o15)}")
            c_o15 = st.number_input("Tu Cuota (+1.5):", min_value=1.0, value=1.0, step=0.05, key="o15")
            evaluar_valor(prob_o15, c_o15)
            
            st.metric("Menos de 1.5", f"{round(prob_u15, 1)}%", f"Cuota Justa: {cuota_justa(prob_u15)}")
            c_u15 = st.number_input("Tu Cuota (-1.5):", min_value=1.0, value=1.0, step=0.05, key="u15")
            evaluar_valor(prob_u15, c_u15)
            
        with ou2:
            st.markdown("#### Línea 2.5")
            st.metric("Más de 2.5 Goles", f"{round(prob_o25, 1)}%", f"Cuota Justa: {cuota_justa(prob_o25)}")
            c_o25 = st.number_input("Tu Cuota (+2.5):", min_value=1.0, value=1.0, step=0.05, key="o25")
            evaluar_valor(prob_o25, c_o25)
            
            st.metric("Menos de 2.5", f"{round(prob_u25, 1)}%", f"Cuota Justa: {cuota_justa(prob_u25)}")
            c_u25 = st.number_input("Tu Cuota (-2.5):", min_value=1.0, value=1.0, step=0.05, key="u25")
            evaluar_valor(prob_u25, c_u25)
            
        with ou3:
            st.markdown("#### Línea 3.5")
            st.metric("Más de 3.5 Goles", f"{round(prob_o35, 1)}%", f"Cuota Justa: {cuota_justa(prob_o35)}")
            c_o35 = st.number_input("Tu Cuota (+3.5):", min_value=1.0, value=1.0, step=0.05, key="o35")
            evaluar_valor(prob_o35, c_o35)
            
            st.metric("Menos de 3.5", f"{round(prob_u35, 1)}%", f"Cuota Justa: {cuota_justa(prob_u35)}")
            c_u35 = st.number_input("Tu Cuota (-3.5):", min_value=1.0, value=1.0, step=0.05, key="u35")
            evaluar_valor(prob_u35, c_u35)

        st.divider()

        # --- INTERFAZ 1X2 Y AMBOS MARCAN ---
        col_1x2, col_am = st.columns(2)
        with col_1x2:
            st.markdown("### ⚽ Mercado 1X2")
            g1, g2, g3 = st.columns(3)
            with g1:
                st.metric(f"Gana {local}", f"{round(prob_1, 1)}%", f"Cuota: {cuota_justa(prob_1)}")
                c_1 = st.number_input("Cuota Local:", min_value=1.0, value=1.0, step=0.05, key="c1")
                evaluar_valor(prob_1, c_1)
            with g2:
                st.metric("Empate", f"{round(prob_X, 1)}%", f"Cuota: {cuota_justa(prob_X)}")
                c_x = st.number_input("Cuota Empate:", min_value=1.0, value=1.0, step=0.05, key="cx")
                evaluar_valor(prob_X, c_x)
            with g3:
                st.metric(f"Gana {visitante}", f"{round(prob_2, 1)}%", f"Cuota: {cuota_justa(prob_2)}")
                c_2 = st.number_input("Cuota Visita:", min_value=1.0, value=1.0, step=0.05, key="c2")
                evaluar_valor(prob_2, c_2)

        with col_am:
            st.markdown("### 🎯 Ambos Equipos Marcan")
            am1, am2 = st.columns(2)
            with am1:
                st.metric("Sí (BTTS)", f"{round(prob_btts, 1)}%", f"Cuota: {cuota_justa(prob_btts)}")
                c_btts = st.number_input("Cuota BTTS Sí:", min_value=1.0, value=1.0, step=0.05, key="btts")
                evaluar_valor(prob_btts, c_btts)
            with am2:
                prob_no_btts = 100 - prob_btts
                st.metric("No (BTTS)", f"{round(prob_no_btts, 1)}%", f"Cuota: {cuota_justa(prob_no_btts)}")
                c_no_btts = st.number_input("Cuota BTTS No:", min_value=1.0, value=1.0, step=0.05, key="nobtts")
                evaluar_valor(prob_no_btts, c_no_btts)

        st.divider()

        # --- SECCIÓN BLINDADA DE ESTADÍSTICAS PURAS ---
        st.markdown("### 🛠️ Proyecciones Estadísticas Extra")
        
        exp_col1, exp_col2 = st.columns(2)
        
        with exp_col1:
            with st.expander("🚩 Corners Esperados"):
                # ESCUDO: Verificamos si existen las columnas de corners
                if 'HC' in datos_premier.columns and 'AC' in datos_premier.columns:
                    ataque_local_c = datos_premier[datos_premier['HomeTeam'] == local]['HC'].mean()
                    defensa_vis_c = datos_premier[datos_premier['AwayTeam'] == visitante]['HC'].mean()
                    esp_local_c = (ataque_local_c + defensa_vis_c) / 2
                    
                    ataque_vis_c = datos_premier[datos_premier['AwayTeam'] == visitante]['AC'].mean()
                    defensa_local_c = datos_premier[datos_premier['HomeTeam'] == local]['AC'].mean()
                    esp_vis_c = (ataque_vis_c + defensa_local_c) / 2
                    
                    st.write(f"**Total Proyectado:** {round(esp_local_c + esp_vis_c, 2)} corners")
                    st.write(f"A favor de {local}: {round(esp_local_c, 2)}")
                    st.write(f"A favor de {visitante}: {round(esp_vis_c, 2)}")
                else:
                    st.info("⚠️ Datos de corners no disponibles en esta liga.")
                    
        with exp_col2:
            with st.expander("🟨 Tarjetas Esperadas"):
                # ESCUDO: Verificamos tarjetas
                if 'HY' in datos_premier.columns and 'AY' in datos_premier.columns:
                    tarjetas_local = datos_premier[datos_premier['HomeTeam'] == local]['HY'].mean()
                    tarjetas_vis = datos_premier[datos_premier['AwayTeam'] == visitante]['AY'].mean()
                    esp_equipos_t = tarjetas_local + tarjetas_vis
                    
                    if arbitro != "Ninguno":
                        prom_arb = datos_premier[datos_premier['Referee'] == arbitro]['Total_Yellows'].mean()
                        total_t = (esp_equipos_t + prom_arb) / 2
                        st.write(f"**Total Ajustado (Árbitro {arbitro}):** {round(total_t, 2)} tarjetas")
                    else:
                        st.write(f"**Total Base Equipos:** {round(esp_equipos_t, 2)} tarjetas")
                else:
                    st.info("⚠️ Datos de tarjetas no disponibles en esta liga.")

        exp_col3, exp_col4 = st.columns(2)
        
        with exp_col3:
            with st.expander("🥅 Tiros al Arco"):
                # ESCUDO: Verificamos tiros al arco
                if 'HST' in datos_premier.columns and 'AST' in datos_premier.columns:
                    ataque_local_t = datos_premier[datos_premier['HomeTeam'] == local]['HST'].mean()
                    defensa_vis_t = datos_premier[datos_premier['AwayTeam'] == visitante]['HST'].mean()
                    esp_local_t = (ataque_local_t + defensa_vis_t) / 2
                    
                    ataque_vis_t = datos_premier[datos_premier['AwayTeam'] == visitante]['AST'].mean()
                    defensa_local_t = datos_premier[datos_premier['HomeTeam'] == local]['AST'].mean()
                    esp_vis_t = (ataque_vis_t + defensa_local_t) / 2
                    
                    st.write(f"**Total del Partido:** {round(esp_local_t + esp_vis_t, 2)} tiros al arco")
                    st.write(f"De {local}: {round(esp_local_t, 2)}")
                    st.write(f"De {visitante}: {round(esp_vis_t, 2)}")
                else:
                    st.info("⚠️ Datos de tiros no disponibles en esta liga.")

        with exp_col4:
            with st.expander("🛑 Faltas Cometidas"):
                # ESCUDO: Verificamos faltas
                if 'HF' in datos_premier.columns and 'AF' in datos_premier.columns:
                    agres_local = datos_premier[datos_premier['HomeTeam'] == local]['HF'].mean()
                    recibe_vis = datos_premier[datos_premier['AwayTeam'] == visitante]['HF'].mean()
                    esp_local_f = (agres_local + recibe_vis) / 2
                    
                    agres_vis = datos_premier[datos_premier['AwayTeam'] == visitante]['AF'].mean()
                    recibe_local = datos_premier[datos_premier['HomeTeam'] == local]['AF'].mean()
                    esp_vis_f = (agres_vis + recibe_local) / 2
                    
                    st.write(f"**Total del Partido:** {round(esp_local_f + esp_vis_f, 2)} faltas")
                    st.write(f"Cometidas por {local}: {round(esp_local_f, 2)}")
                    st.write(f"Cometidas por {visitante}: {round(esp_vis_f, 2)}")
                else:
                    st.info("⚠️ Datos de faltas no disponibles en esta liga.")
                    
    elif local == visitante:
        st.warning("⚠️ Selecciona dos equipos distintos.")