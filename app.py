import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Sobolev", page_icon="⚽", layout="centered")

# ==========================================
# DICCIONARIO DE BANDERAS
# ==========================================
# Si falta un país en tu JSON, simplemente agrégalo aquí con su emoji
banderas = {
    "Ecuador": "🇪🇨", "Ghana": "🇬🇭", "Panamá": "🇵🇦", "Uzbekistán": "🇺🇿", 
    "Colombia": "🇨🇴", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croacia": "🇭🇷", "Portugal": "🇵🇹", 
    "RD Congo": "🇨🇩", "Austria": "🇦🇹", "Jordania": "🇯🇴", "Argentina": "🇦🇷", 
    "Argelia": "🇩🇿", "Irak": "🇮🇶", "Noruega": "🇳🇴", "Francia": "🇫🇷", 
    "Senegal": "🇸🇳", "Arabia Saudita": "🇸🇦", "Uruguay": "🇺🇾", "Irán": "🇮🇷", 
    "Nueva Zelanda": "🇳🇿", "España": "🇪🇸", "Cabo Verde": "🇨🇻", "Bélgica": "🇧🇪", 
    "Egipto": "🇪🇬", "Canadá": "🇨🇦", "Bosnia y Herzegovina": "🇧🇦", 
    "Corea del Sur": "🇰🇷", "República Checa": "🇨🇿", "México": "🇲🇽", 
    "Sudáfrica": "🇿🇦", "Brasil": "🇧🇷", "Alemania": "🇩🇪", "Italia": "🇮🇹",
    "Países Bajos": "🇳🇱", "Estados Unidos": "🇺🇸", "Japón": "🇯🇵", "Marruecos": "🇲🇦", "Suiza":"🇨🇭", "Catar":"🇶🇦",
    "Australia":"🇦🇺", "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Paraguay": "🇵🇾", "Turquía": "🇹🇷", "Costa de Marfil":"🇨🇮", "Curazao": "🇨🇼",
    "Suecia":"🇸🇪"
}

# ==========================================
# FUNCIONES DE LECTURA Y ESCRITURA JSON
# ==========================================
def cargar_datos(nombre_archivo, datos_por_defecto):
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return datos_por_defecto

def guardar_datos(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

usuarios = cargar_datos("usuarios.json", [])
partidos = cargar_datos("partidos.json", [])
pronosticos = cargar_datos("pronosticos.json", [])

df_usuarios = pd.DataFrame(usuarios)

# ==========================================
# CÁLCULO DE ESTADO DEL BANCO Y TASA DE CAMBIO
# ==========================================
if not df_usuarios.empty and "Banco" in df_usuarios["nombre"].values:
    datos_banco = df_usuarios[df_usuarios["nombre"] == "Banco"].iloc[0]
    dolares_reserva = float(datos_banco["dolares_depositados"])
    sobolevs_reserva = float(datos_banco["monedas"])
else:
    dolares_reserva = 0.0
    sobolevs_reserva = 0.0

tasa_base = 10.0
if sobolevs_reserva > 0 and dolares_reserva > 0:
    total_sobolevs_emitidos = df_usuarios[df_usuarios["nombre"] != "Banco"]["monedas"].sum() + sobolevs_reserva
    respaldo = dolares_reserva / total_sobolevs_emitidos if total_sobolevs_emitidos > 0 else 0
    tasa_actual = max(2.0, min(10.0, respaldo * 100))
else:
    tasa_actual = tasa_base

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.title("🏆 Mundial 2026")

# Visualización compacta
st.metric(label="💵 1 USD equivale a", value=f"{tasa_actual:.2f} Sobolevs")
st.markdown("---")

nombres_jugadores = [u["nombre"] for u in usuarios if u["nombre"] != "Banco"]

if nombres_jugadores:
    usuario_seleccionado = st.selectbox("👤 Identifícate:", nombres_jugadores)
    
    # Buscamos directamente en la lista de diccionarios original de Python
    datos_usuario_sel = next((u for u in usuarios if u["nombre"] == usuario_seleccionado), None)
    
    if datos_usuario_sel:
        # Extraemos el PIN como texto puro y limpiamos espacios accidentales
        pin_correcto = str(datos_usuario_sel.get("pin", "1234")).strip()
        
        # Entrada de contraseña
        pin_ingresado = st.text_input("🔑 Ingresa tu PIN de acceso:", type="password", key=f"pin_{usuario_seleccionado}").strip()
        
        # VALIDACIÓN: Comparación limpia de cadenas de texto
        if pin_ingresado == pin_correcto:
            usuario_actual = usuario_seleccionado
            saldo_usuario = datos_usuario_sel["monedas"]
            
            st.success(f"🔓 Acceso concedido a la sesión de {usuario_actual}")
            
            # --- SALDO SIEMPRE VISIBLE EN SIDEBAR ---
            st.sidebar.subheader("🏦 Tu Billetera")
            usuarios_frescos = cargar_datos("usuarios.json", [])
            saldo_fresco = next((u["monedas"] for u in usuarios_frescos if u["nombre"] == usuario_actual), 0)
            
            st.sidebar.metric("Sobolevs Disponibles", f"{saldo_fresco} 💰")
            st.sidebar.markdown("---")

          # Declaración dinámica de pestañas
            titulos_pestanas = ["🔐 Mi Perfil", "🛒 Tienda", "⚽ Apuestas", "📊 Posiciones", "📝 Resultados", "📜 Reglas", "📢 Edictos"]
            
            if usuario_actual == "Daniela":
                titulos_pestanas.append("⚙️ Control")
                
            pestanas = st.tabs(titulos_pestanas)
            
            # Asignamos
            tab_perfil = pestanas[0]
            tab_tienda = pestanas[1]
            tab_apuestas = pestanas[2]
            tab_posiciones = pestanas[3]
            tab_resultados = pestanas[4] # NUEVA PESTAÑA
            tab_reglas = pestanas[5]
            tab_edictos = pestanas[6]
            
            if usuario_actual == "Daniela":
                tab_control = pestanas[7]
            
            # --- PESTAÑA: RESULTADOS (Desglose Anónimo por partido finalizado) ---
            with tab_resultados:
                st.subheader("📝 Desglose de Resultados")
                st.write("*(Revisa de forma anónima los marcadores apostados y su nivel de acierto en los partidos finalizados)*")
                
                partidos_terminados = [p for p in partidos if p.get("estado") == "finalizado"]
                
                if not partidos_terminados:
                    st.info("Aún no hay partidos finalizados con resultados oficiales registrados.")
                else:
                    # Ordenar para que el último finalizado salga primero
                    partidos_terminados.sort(key=lambda x: x.get("id_partido", 0), reverse=True)
                    
                    for p in partidos_terminados:
                        id_p = p["id_partido"]
                        equipo1 = p["equipo_1"]
                        equipo2 = p["equipo_2"]
                        g1_real = p.get("goles_1_real")
                        g2_real = p.get("goles_2_real")
                        
                        # Extraer bandera o poner genérica si no existe
                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")
                        
                        # Verificamos que el partido tenga goles reales y no sea null
                        if g1_real is not None and g2_real is not None:
                            apuestas_partido = [pron for pron in pronosticos if pron["id_partido"] == id_p]
                            
                            if apuestas_partido:
                                with st.expander(f"✅ Partido {id_p}: {b1} {equipo1} {g1_real} - {g2_real} {b2} {equipo2}"):
                                    datos_desglose = []
                                    
                                    for pron in apuestas_partido:
                                        g1_p = pron["goles_1_pronostico"]
                                        g2_p = pron["goles_2_pronostico"]
                                        ganancia = pron.get("puntos_ganados", 0)
                                        
                                        # Determinamos el tipo de acierto visual
                                        if ganancia > 0:
                                            if g1_real == g1_p and g2_real == g2_p:
                                                texto_acierto = "🎯 Marcador Exacto"
                                            elif (g1_real - g2_real) == (g1_p - g2_p):
                                                texto_acierto = "⚖️ Diferencia"
                                            else:
                                                texto_acierto = "✅ Ganador"
                                        else:
                                            texto_acierto = "❌ Fallo"
                                            
                                        # Solo guardamos las dos columnas solicitadas
                                        datos_desglose.append({
                                            "Pronóstico": f"{g1_p} - {g2_p}",
                                            "Resultado": texto_acierto
                                        })
                                        
                                    df_desglose = pd.DataFrame(datos_desglose)
                                    # Se muestra la tabla limpia y sin índices
                                    st.dataframe(df_desglose, use_container_width=True, hide_index=True)
                            else:
                                with st.expander(f"✅ Partido {id_p}: {b1} {equipo1} {g1_real} - {g2_real} {b2} {equipo2}"):
                                    st.write("Ningún familiar registró pronósticos para este encuentro.")

            # --- PESTAÑA: EDICTOS ---
            with tab_edictos:
                st.subheader("📢 Edictos del Comisionado")
                st.markdown("""
                ### ¡Bienvenidos a la gloria eterna! 🌍⚽
                
                Se le informa a toda la familia que el **Banco Central del Sobolev** ha entrado en fase de máxima emisión. 
                
                * **La regla es clara:** Si no apuestas, no existes. Si apuestas y pierdes, bueno... siempre puedes intentar pedirle un préstamo a quien lidere la tabla, aunque dudamos que acepte Sobolevs.
                * **Recuerden:** El que se arriesga, gana. El que no se arriesga, se queda viendo cómo los demás celebran sus aciertos.
                * **Mensaje motivacional:** No importa si tu pronóstico parece hecho por alguien que nunca ha visto un balón en su vida; ¡a veces la suerte favorece a los que no tienen ni idea!
                
                **¡Que empiece el juego, que corran los Sobolevs y que gane el que menos se equivoque!** 🚀
                """)

            # --- PESTAÑA: REGLAS ---
            with tab_reglas:
                st.subheader("📜 Reglas de Puntuación y Multiplicadores")
                st.write("Dependiendo de tu nivel de precisión en los pronósticos, tus Sobolevs invertidos se multiplicarán de la siguiente manera:")
                
                st.markdown("""
                * **🎯 Acierto de Marcador (x10):** Adivinas los goles exactos de ambos equipos. *(Ej: Pronosticas 2-1 y termina 2-1)*. Tu inversión se multiplica por 10.
                * **⚖️ Acierto de Diferencia (x6):** Adivinas el ganador y la diferencia de goles exacta (o el empate). *(Ej: Pronosticas 2-0 y termina 3-1, la diferencia de goles es +2)*. Tu inversión se multiplica por 6.
                * **✅ Acierto de Ganador (x4):** Solo adivinas quién gana o si hay empate, pero fallas la diferencia. *(Ej: Pronosticas 1-0 y termina 3-0)*. Tu inversión se multiplica por 4.
                * **❌ Fallo Total (x0):** No adivinas el resultado final. Pierdes tu inversión.
                """)
                st.info("💡 **Dato clave:** Puedes cambiar tu pronóstico y la cantidad invertida todas las veces que desees. La aplicación tomará únicamente la última apuesta registrada antes del inicio del partido.")

            # --- PESTAÑA: MI PERFIL (Seguridad) ---
            with tab_perfil:
                st.subheader("🔐 Seguridad de la Cuenta")
                st.write("Aquí puedes cambiar tu clave de acceso. ¡Asegúrate de no olvidarla!")
                
                with st.form(key=f"form_pin_{usuario_actual}"):
                    nuevo_pin = st.text_input("Escribe tu nuevo PIN:", type="password")
                    confirmar_pin = st.text_input("Confirma tu nuevo PIN:", type="password")
                    
                    boton_actualizar_pin = st.form_submit_button("Actualizar Contraseña")
                    
                    if boton_actualizar_pin:
                        if nuevo_pin == confirmar_pin and len(nuevo_pin.strip()) > 0:
                            for u in usuarios:
                                if u["nombre"] == usuario_actual:
                                    u["pin"] = nuevo_pin.strip()
                                    break
                            
                            guardar_datos("usuarios.json", usuarios)
                            st.success("✅ ¡Tu contraseña ha sido actualizada con éxito!")
                        elif nuevo_pin != confirmar_pin:
                            st.error("❌ Las contraseñas no coinciden. Inténtalo de nuevo.")
                        else:
                            st.warning("⚠️ El PIN no puede estar completamente vacío.")
                            
            # --- PESTAÑA: TIENDA ---
            with tab_tienda:
                st.subheader("Casa de Cambio Autorizada")
                dolares = st.number_input("Cantidad de Dólares a depositar ($)", min_value=1.0, step=1.0)
                sobolevs_comprados = int(dolares * tasa_actual)
                
                st.info(f"Recibirás **{sobolevs_comprados} Sobolevs**")
                
                if st.button("Ejecutar Transacción"):
                    for u in usuarios:
                        if u["nombre"] == usuario_actual:
                            u["monedas"] += sobolevs_comprados
                            u["dolares_depositados"] += dolares
                        if u["nombre"] == "Banco":
                            u["dolares_depositados"] += dolares
                    
                    guardar_datos("usuarios.json", usuarios)
                    
                    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    registro = f"[{fecha_hora}] Usuario: {usuario_actual} | Depósito: ${dolares} | Sobolevs: {sobolevs_comprados}\n"
                    
                    with open("historial_depositos.txt", "a", encoding="utf-8") as f_log:
                        f_log.write(registro)
                        
                    st.success("¡Transacción procesada y registrada en el historial!")
                    st.rerun()

                st.markdown("---")
                st.write("📄 **Auditoría del Banco Central**")
                
                if os.path.exists("historial_depositos.txt"):
                    with open("historial_depositos.txt", "r", encoding="utf-8") as f_log:
                        contenido_log = f_log.read()
                    
                    st.download_button(
                        label="⬇️ Descargar Historial de Depósitos",
                        data=contenido_log,
                        file_name="historial_depositos.txt",
                        mime="text/plain"
                    )
                else:
                    st.write("Aún no hay transacciones registradas en el historial.")

            # --- PESTAÑA: APUESTAS ---
            with tab_apuestas:
                # Candado de memoria: Muestra el mensaje de éxito con el saldo restante tras el reinicio
                if "mensaje_exito" in st.session_state:
                    st.success(st.session_state["mensaje_exito"])
                    del st.session_state["mensaje_exito"] # Lo borramos para que no se repita eternamente

                hora_actual_local = datetime.utcnow() - timedelta(hours=5)
                
                partidos_abiertos = []
                partidos_en_curso = []
                partidos_finalizados = []
                
                for p in partidos:
                    if p.get("estado") != "futuro":
                        fecha_str = p.get("fecha", "")
                        hora_str = p.get("hora", "23:59")
                        estado_json = p.get("estado", "pendiente")
                        try:
                            fecha_partido = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
                            # LÓGICA DE 2 HORAS: Calculamos cuándo debería terminar el partido
                            hora_fin_estimada = fecha_partido + timedelta(hours=2)
                            
                            # Entra a finalizados si el JSON lo dice, o si ya pasaron 2 horas
                            if estado_json == "finalizado" or hora_actual_local >= hora_fin_estimada:
                                partidos_finalizados.append((p, fecha_partido))
                            elif hora_actual_local >= fecha_partido:
                                partidos_en_curso.append((p, fecha_partido))
                            else:
                                partidos_abiertos.append(p)
                        except ValueError:
                            pass
                
                # ==========================================
                # SECCIÓN 1: PARTIDOS EN CURSO (TOP / ARRIBA)
                # ==========================================
                if partidos_en_curso:
                    st.subheader("🔥 Partidos en Curso")
                    st.write("*(El balón está rodando. Mira las tendencias de la familia 🤫)*")
                    
                    partidos_en_curso.sort(key=lambda x: x[1], reverse=True)
                    
                    for p, _ in partidos_en_curso:
                        id_p = p["id_partido"]
                        equipo1 = p["equipo_1"]
                        equipo2 = p["equipo_2"]
                        grupo = p.get("grupo", "")
                        
                        # Extraer bandera o poner genérica si no existe
                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")
                        
                        with st.expander(f"Partido {id_p} ({grupo}): {b1} {equipo1} vs {b2} {equipo2} - Cerrado (En Curso) 🟢"):
                            mi_apuesta = next((pron for pron in pronosticos if pron["usuario"] == usuario_actual and pron["id_partido"] == id_p), None)
                            
                            if mi_apuesta:
                                st.info(f"📝 **Tu pronóstico:** {b1} {equipo1} **{mi_apuesta['goles_1_pronostico']} - {mi_apuesta['goles_2_pronostico']}** {b2} {equipo2} | Inversión: **{mi_apuesta.get('monto_apostado', 0)}** Sobolevs")
                            else:
                                st.warning("No registraste ningún pronóstico para este encuentro.")
                                
                            st.markdown("---")
                            
                            apuestas_partido = [pron for pron in pronosticos if pron["id_partido"] == id_p]
                            if apuestas_partido:
                                conteo_marcadores = {}
                                for pron in apuestas_partido:
                                    marcador = f"{pron['goles_1_pronostico']} - {pron['goles_2_pronostico']}"
                                    conteo_marcadores[marcador] = conteo_marcadores.get(marcador, 0) + 1
                                
                                st.markdown("**Tendencias del Mercado (Anónimo):**")
                                for marcador, cantidad in sorted(conteo_marcadores.items(), key=lambda x: x[1], reverse=True):
                                    st.write(f"📊 Marcador **{marcador}** ➔ Votado por **{cantidad}** persona(s)")
                            else:
                                st.write("Ningún familiar registró pronósticos para este encuentro.")

                # ==========================================
                # SECCIÓN 2: PARTIDOS PARA PRONOSTICAR (MEDIO)
                # ==========================================
                st.markdown("---")
                st.subheader("📅 Próximos Partidos Disponibles")
                
                if not partidos_abiertos:
                    st.info("No hay partidos abiertos para pronósticos en este momento.")
                else:
                    st.warning(f"🕒 Hora del servidor: {hora_actual_local.strftime('%H:%M:%S')}. Los formularios se bloquean al pitazo inicial.")
                    
                    partidos_abiertos.sort(key=lambda x: datetime.strptime(f"{x.get('fecha','')} {x.get('hora','23:59')}", "%Y-%m-%d %H:%M"))
                    
                    for partido in partidos_abiertos:
                        id_p = partido["id_partido"]
                        equipo1 = partido["equipo_1"]
                        equipo2 = partido["equipo_2"]
                        hora_partido = partido.get("hora", "")
                        grupo = partido.get("grupo", "")
                        
                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")
                        
                        pick_actual = next((pron for pron in pronosticos if pron["usuario"] == usuario_actual and pron["id_partido"] == id_p), None)
                        
                        st.markdown("---")
                        if pick_actual:
                            st.info(f"👉 **Tu pick actual:** {b1} {equipo1} **{pick_actual['goles_1_pronostico']} - {pick_actual['goles_2_pronostico']}** {b2} {equipo2} | Inversión: **{pick_actual['monto_apostado']}** Sobolevs.")
                        
                        with st.form(key=f"form_apuesta_{id_p}"):
                            st.write(f"**Partido {id_p}** | **{grupo}** | {partido.get('fecha', '')} {hora_partido}")
                            
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                            with col1:
                                st.markdown(f"<h4 style='text-align: right;'>{b1} {equipo1}</h4>", unsafe_allow_html=True)
                            with col2:
                                default_g1 = int(pick_actual["goles_1_pronostico"]) if pick_actual else 0
                                goles1 = st.number_input("Goles", min_value=0, max_value=15, step=1, value=default_g1, key=f"g1_{id_p}")
                            with col3:
                                default_g2 = int(pick_actual["goles_2_pronostico"]) if pick_actual else 0
                                goles2 = st.number_input("Goles", min_value=0, max_value=15, step=1, value=default_g2, key=f"g2_{id_p}")
                            with col4:
                                st.markdown(f"<h4>{b2} {equipo2}</h4>", unsafe_allow_html=True)
                                
                            max_apuesta = int(saldo_usuario) if saldo_usuario > 0 else 1
                            default_monto = int(pick_actual["monto_apostado"]) if pick_actual else 1
                            monto_apostado = st.number_input("Sobolevs a invertir:", min_value=1, max_value=max_apuesta + default_monto, step=1, value=default_monto, key=f"monto_{id_p}")
                            
                            texto_boton = "Actualizar Pronóstico" if pick_actual else "Guardar Pronóstico"
                            boton_apostar = st.form_submit_button(texto_boton)
                            
                            if boton_apostar:
                                hora_verificacion = datetime.utcnow() - timedelta(hours=5)
                                if hora_verificacion >= datetime.strptime(f"{partido.get('fecha')} {partido.get('hora', '23:59')}", "%Y-%m-%d %H:%M"):
                                    st.error("❌ Demasiado tarde. El partido ya ha comenzado.")
                                    continue

                                if saldo_usuario + (pick_actual["monto_apostado"] if pick_actual else 0) >= monto_apostado:
                                    apuesta_existente = False
                                    for pron in pronosticos:
                                        if pron["usuario"] == usuario_actual and pron["id_partido"] == id_p:
                                            monto_anterior = pron.get("monto_apostado", 0)
                                            for u in usuarios:
                                                if u["nombre"] == usuario_actual:
                                                    u["monedas"] += monto_anterior
                                                    
                                            pron["goles_1_pronostico"] = goles1
                                            pron["goles_2_pronostico"] = goles2
                                            pron["monto_apostado"] = monto_apostado
                                            apuesta_existente = True
                                            break
                                    
                                    if not apuesta_existente:
                                        pronosticos.append({
                                            "usuario": usuario_actual,
                                            "id_partido": id_p,
                                            "goles_1_pronostico": goles1,
                                            "goles_2_pronostico": goles2,
                                            "monto_apostado": monto_apostado,
                                            "puntos_ganados": 0
                                        })

                                    for u in usuarios:
                                        if u["nombre"] == usuario_actual:
                                            u["monedas"] -= monto_apostado
                                    
                                    guardar_datos("usuarios.json", usuarios)
                                    guardar_datos("pronosticos.json", pronosticos)
                                    
                                    registro_apuesta = f"[{hora_verificacion.strftime('%Y-%m-%d %H:%M:%S')}] APUESTA | {usuario_actual} | Partido {id_p} | Goles: {goles1}-{goles2} | Monto: {monto_apostado}\n"
                                    with open("historial_apuestas.txt", "a", encoding="utf-8") as f_log:
                                        f_log.write(registro_apuesta)
                                        
                                    saldo_restante = saldo_usuario + (pick_actual["monto_apostado"] if pick_actual else 0) - monto_apostado
                                    st.session_state["mensaje_exito"] = f"🎯 ¡Pronóstico guardado! {b1} {equipo1} **{goles1} - {goles2}** {b2} {equipo2} por **{monto_apostado}** Sobolevs. Tu saldo disponible restante es: 💰 **{saldo_restante} Sobolevs**."
                                    st.rerun()
                                else:
                                    st.error("❌ No tienes suficientes Sobolevs.")

                # ==========================================
                # SECCIÓN 3: PARTIDOS FINALIZADOS (AL FONDO)
                # ==========================================
                st.markdown("---")
                st.subheader("✅ Partidos Finalizados")
                
                if not partidos_finalizados:
                    st.info("Aún no hay partidos finalizados.")
                else:
                    partidos_finalizados.sort(key=lambda x: x[1], reverse=True)
                    
                    for p, _ in partidos_finalizados:
                        id_p = p["id_partido"]
                        equipo1 = p["equipo_1"]
                        equipo2 = p["equipo_2"]
                        grupo = p.get("grupo", "")
                        estado_json = p.get("estado", "pendiente")
                        
                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")
                        
                        with st.expander(f"Partido {id_p} ({grupo}): {b1} {equipo1} vs {b2} {equipo2} - Finalizado"):
                            
                            # Mostrar resultado real solo si la administradora ya lo guardó en el JSON
                            if estado_json == "finalizado":
                                st.success(f"**Resultado Final Oficial:** {b1} {equipo1} **{p.get('goles_1_real')} - {p.get('goles_2_real')}** {b2} {equipo2}")
                            else:
                                st.warning("⏳ Esperando que la administradora registre el resultado oficial para pagar los premios.")
                                
                            mi_apuesta = next((pron for pron in pronosticos if pron["usuario"] == usuario_actual and pron["id_partido"] == id_p), None)
                            
                            if mi_apuesta:
                                st.info(f"📝 **Tu pronóstico:** {b1} {equipo1} **{mi_apuesta['goles_1_pronostico']} - {mi_apuesta['goles_2_pronostico']}** {b2} {equipo2} | Inversión: **{mi_apuesta.get('monto_apostado', 0)}** Sobolevs")
                                if estado_json == "finalizado":
                                    st.write(f"🏆 Ganancia obtenida: **{mi_apuesta.get('puntos_ganados', 0)} Sobolevs**")
                            else:
                                st.warning("No registraste ningún pronóstico para este encuentro.")
                                
                            st.markdown("---")
                            
                            apuestas_partido = [pron for pron in pronosticos if pron["id_partido"] == id_p]
                            if apuestas_partido:
                                conteo_marcadores = {}
                                for pron in apuestas_partido:
                                    marcador = f"{pron['goles_1_pronostico']} - {pron['goles_2_pronostico']}"
                                    conteo_marcadores[marcador] = conteo_marcadores.get(marcador, 0) + 1
                                
                                st.markdown("**Tendencias del Mercado (Anónimo):**")
                                for marcador, cantidad in sorted(conteo_marcadores.items(), key=lambda x: x[1], reverse=True):
                                    st.write(f"📊 Marcador **{marcador}** ➔ Votado por **{cantidad}** persona(s)")
                            else:
                                st.write("Ningún familiar registró pronósticos para este encuentro.")

            # --- PESTAÑA: POSICIONES ---
            with tab_posiciones:
                st.subheader("📊 Ranking de Pronósticos")
                st.write("*(Aquí puedes ver el rendimiento neto de las apuestas de toda la familia)*")
                
                datos_ranking = []
                
                for u in usuarios:
                    if u["nombre"] == "Banco": 
                        continue
                        
                    nombre_familiar = u["nombre"]
                    apostado_total = 0
                    balance_neto = 0
                    
                    for pron in pronosticos:
                        if pron["usuario"] == nombre_familiar:
                            monto = pron.get("monto_apostado", 0)
                            ganado = pron.get("puntos_ganados", 0)
                            
                            apostado_total += monto
                            
                            estado_partido = "pendiente"
                            for p in partidos:
                                if p["id_partido"] == pron["id_partido"]:
                                    estado_partido = p.get("estado", "pendiente")
                                    break
                            
                            if estado_partido == "finalizado":
                                balance_neto += (ganado - monto)
                    
                    datos_ranking.append({
                        "Familiar": nombre_familiar,
                        "Rendimiento Neto": balance_neto
                    })
                    
                if datos_ranking:
                    df_ranking = pd.DataFrame(datos_ranking)
                    df_ranking = df_ranking.sort_values(by="Rendimiento Neto", ascending=False).reset_index(drop=True)
                    
                    # 1. Creamos la columna de posiciones
                    df_ranking["Puesto"] = df_ranking.index + 1
                    df_ranking["Puesto"] = df_ranking["Puesto"].apply(lambda x: f"{x}º")
                    
                    # 2. Mostramos TODO de forma pública
                    df_publico = df_ranking[["Puesto", "Familiar", "Rendimiento Neto"]]
                    st.dataframe(df_publico, use_container_width=True)
                    
                else:
                    st.info("Aún no hay estadísticas suficientes para generar el ranking.")
# --- PESTAÑA: CONTROL (Exclusiva para Administradora) ---
            if usuario_actual == "Daniela":
                with tab_control:
                    st.subheader("⚙️ Panel de Administración y Respaldos")
                    st.info("Descarga los archivos actualizados al final del día y súbelos a tu repositorio para guardar los cambios permanentemente.")
                    
                    # ==========================================
                    # ESTADO DE LA BÓVEDA
                    # ==========================================
                    st.markdown("---")
                    st.subheader("🏦 Bóveda del Banco Central")
                    
                    usuarios_banco = cargar_datos("usuarios.json", [])
                    datos_banco_actualizado = next((u for u in usuarios_banco if u["nombre"] == "Banco"), None)
                    
                    if datos_banco_actualizado:
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            st.metric("Reserva del Banco (Sobolevs)", f"{datos_banco_actualizado['monedas']} 💰")
                        with col_b2:
                            st.metric("Respaldo Total (Dólares)", f"${datos_banco_actualizado['dolares_depositados']:.2f} 💵")
                    else:
                        st.warning("No se encontró la cuenta 'Banco' en usuarios.json.")

                    # ==========================================
                    # REPARTICIÓN DE PREMIOS (MODELO DE SUMA CERO)
                    # ==========================================
                    st.markdown("---")
                    st.subheader("🏦 Repartición de Premios")
                    st.write("Presiona este botón después de poner un partido en estado 'finalizado' para transferir las ganancias automáticamente.")
                    
                    if st.button("Calcular y Pagar Premios Pendientes"):
                        cambios_realizados = False
                        
                        for p in partidos:
                            if p.get("estado") == "finalizado":
                                g1_real = p.get("goles_1_real")
                                g2_real = p.get("goles_2_real")
                                
                                if g1_real is not None and g2_real is not None:
                                    for pron in pronosticos:
                                        if pron["id_partido"] == p["id_partido"] and not pron.get("pagado", False):
                                            g1_pron = pron["goles_1_pronostico"]
                                            g2_pron = pron["goles_2_pronostico"]
                                            monto = pron.get("monto_apostado", 0)
                                            
                                            multiplicador = 0
                                            
                                            if g1_real == g1_pron and g2_real == g2_pron:
                                                multiplicador = 10
                                            elif (g1_real - g2_real) == (g1_pron - g2_pron):
                                                multiplicador = 6
                                            elif (g1_real > g2_real and g1_pron > g2_pron) or (g1_real < g2_real and g1_pron < g2_pron):
                                                multiplicador = 4
                                                
                                            ganancia = monto * multiplicador
                                            
                                            # Actualizamos la base de datos de la apuesta
                                            pron["puntos_ganados"] = ganancia
                                            pron["pagado"] = True 
                                            
                                            # LÓGICA DEL BANCO: "La Casa" recauda la inversión inicial y asume los pagos de premios
                                            flujo_banco = monto - ganancia
                                            
                                            for u in usuarios:
                                                # Pagamos al familiar si acertó
                                                if u["nombre"] == pron["usuario"] and ganancia > 0:
                                                    u["monedas"] += ganancia
                                                
                                                # El Banco suma las pérdidas de la familia, o resta si tuvo que pagar premios gigantes
                                                if u["nombre"] == "Banco":
                                                    u["monedas"] += flujo_banco
                                                        
                                            cambios_realizados = True
                                            
                        if cambios_realizados:
                            guardar_datos("usuarios.json", usuarios)
                            guardar_datos("pronosticos.json", pronosticos)
                            st.success("✅ ¡Premios calculados! Los Sobolevs de las apuestas perdidas han pasado al Banco y los ganadores han recibido sus fondos.")
                            st.rerun()
                        else:
                            st.info("No hay premios nuevos pendientes por repartir en este momento.")
                    
                    st.markdown("---")
                    col_json1, col_json2, col_txt = st.columns(3)
                    
                    with col_json1:
                        if os.path.exists("usuarios.json"):
                            with open("usuarios.json", "r", encoding="utf-8") as f_usr:
                                st.download_button(label="⬇️ Descargar usuarios.json", data=f_usr.read(), file_name="usuarios.json", mime="application/json")
                                
                    with col_json2:
                        if os.path.exists("pronosticos.json"):
                            with open("pronosticos.json", "r", encoding="utf-8") as f_pron:
                                st.download_button(label="⬇️ Descargar pronosticos.json", data=f_pron.read(), file_name="pronosticos.json", mime="application/json")
                                
                    with col_txt:
                        if os.path.exists("historial_apuestas.txt"):
                            with open("historial_apuestas.txt", "r", encoding="utf-8") as f_hist:
                                st.download_button(label="⬇️ Descargar Auditoría", data=f_hist.read(), file_name="historial_apuestas.txt", mime="text/plain")
        
        elif pin_ingresado != "":
            st.error("❌ PIN incorrecto. No tienes autorización para ingresar.")
else:
    st.error("No hay usuarios registrados en la base de datos JSON.")