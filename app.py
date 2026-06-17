import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Sobolev", page_icon="⚽", layout="centered")

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

col_vacia1, col_tasa, col_vacia2 = st.columns([1, 2, 1])
with col_tasa:
    st.metric("Cambio actual", f"{tasa_actual:.2f} Sobolevs por cada USD")

st.markdown("---")

nombres_jugadores = [u["nombre"] for u in usuarios if u["nombre"] != "Banco"]

if nombres_jugadores:
    usuario_seleccionado = st.selectbox("👤 Identifícate:", nombres_jugadores)
    
    # SOLUCIÓN CRUCIAL: Buscamos directamente en la lista de diccionarios original de Python
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

            # Declaración reordenada de las 6 pestañas
            tab_perfil, tab_tienda, tab_apuestas, tab_posiciones, tab_reglas, tab_control = st.tabs([
                "🔐 Mi Perfil", "🛒 Tienda", "⚽ Apuestas", "📊 Posiciones", "📜 Reglas", "⚙️ Control"
            ])
            
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
                hora_actual_local = datetime.utcnow() - timedelta(hours=5)
                
                partidos_abiertos = []
                partidos_cerrados = []
                
                for p in partidos:
                    if p.get("estado") != "futuro":
                        fecha_str = p.get("fecha", "")
                        hora_str = p.get("hora", "23:59")
                        try:
                            fecha_partido = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
                            if hora_actual_local < fecha_partido and p.get("estado") == "pendiente":
                                partidos_abiertos.append(p)
                            else:
                                partidos_cerrados.append((p, fecha_partido))
                        except ValueError:
                            pass
                
                st.subheader("📅 Partidos Disponibles")
                if not partidos_abiertos:
                    st.info("No hay partidos abiertos para pronósticos en este momento.")
                else:
                    st.warning(f"🕒 Hora del servidor: {hora_actual_local.strftime('%H:%M:%S')}. Los formularios se bloquean al pitazo inicial.")
                    
                    for partido in partidos_abiertos:
                        id_p = partido["id_partido"]
                        equipo1 = partido["equipo_1"]
                        equipo2 = partido["equipo_2"]
                        hora_partido = partido.get("hora", "")
                        
                        # NUEVO: Buscar si el usuario ya tiene un pick guardado para este partido
                        pick_actual = next((pron for pron in pronosticos if pron["usuario"] == usuario_actual and pron["id_partido"] == id_p), None)
                        
                        st.markdown("---")
                        # Mostrar el pick actual si existe
                        if pick_actual:
                            st.info(f"👉 **Tu pick actual:** {equipo1} **{pick_actual['goles_1_pronostico']} - {pick_actual['goles_2_pronostico']}** {equipo2} | Inversión: **{pick_actual['monto_apostado']}** Sobolevs. *(Puedes cambiarlo abajo)*")
                        
                        with st.form(key=f"form_apuesta_{id_p}"):
                            grupo = partido.get("grupo", "")
                            st.write(f"**Partido {id_p}** | **{grupo}** | {partido.get('fecha', '')} {hora_partido}")
                            
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                            with col1:
                                st.markdown(f"<h4 style='text-align: right;'>{equipo1}</h4>", unsafe_allow_html=True)
                            with col2:
                                # Si ya hay pick, ponemos esos goles por defecto en el formulario
                                default_g1 = int(pick_actual["goles_1_pronostico"]) if pick_actual else 0
                                goles1 = st.number_input("Goles", min_value=0, max_value=15, step=1, value=default_g1, key=f"g1_{id_p}")
                            with col3:
                                default_g2 = int(pick_actual["goles_2_pronostico"]) if pick_actual else 0
                                goles2 = st.number_input("Goles", min_value=0, max_value=15, step=1, value=default_g2, key=f"g2_{id_p}")
                            with col4:
                                st.markdown(f"<h4>{equipo2}</h4>", unsafe_allow_html=True)
                                
                            max_apuesta = int(saldo_usuario) if saldo_usuario > 0 else 1
                            default_monto = int(pick_actual["monto_apostado"]) if pick_actual else 1
                            monto_apostado = st.number_input("Sobolevs a invertir:", min_value=1, max_value=max_apuesta + default_monto, step=1, value=default_monto, key=f"monto_{id_p}")
                            
                            # Cambiamos el texto del botón si ya hay una apuesta
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
                                        
                                    st.success(f"¡Pronóstico actualizado: {equipo1} {goles1} - {goles2} {equipo2} por {monto_apostado} Sobolevs!")
                                    st.rerun()
                                else:
                                    st.error("❌ No tienes suficientes Sobolevs.")
                st.markdown("---")
                st.subheader("🔒 Partidos en Juego / Finalizados")
                st.write("*(Mira qué marcadores predijo la familia. Los nombres se mantienen en secreto 🤫)*")
                
                partidos_cerrados.sort(key=lambda x: x[1], reverse=True)
                
                for p, _ in partidos_cerrados:
                    id_p = p["id_partido"]
                    equipo1 = p["equipo_1"]
                    equipo2 = p["equipo_2"]
                    estado = p.get("estado", "pendiente")
                    
                    grupo = p.get("grupo", "")
                    with st.expander(f"Partido {id_p} ({grupo}): {equipo1} vs {equipo2} ({estado.capitalize()})"):
                        if estado == "finalizado":
                            st.success(f"**Resultado Final:** {equipo1} **{p.get('goles_1_real')} - {p.get('goles_2_real')}** {equipo2}")
                        
                        apuestas_partido = [pron for pron in pronosticos if pron["id_partido"] == id_p]
                        
                        if apuestas_partido:
                            conteo_marcadores = {}
                            for pron in apuestas_partido:
                                marcador = f"{pron['goles_1_pronostico']} - {pron['goles_2_pronostico']}"
                                conteo_marcadores[marcador] = conteo_marcadores.get(marcador, 0) + 1
                            
                            st.markdown("**Tendencias del Mercado:**")
                            for marcador, cantidad in sorted(conteo_marcadores.items(), key=lambda x: x[1], reverse=True):
                                st.write(f"📊 Marcador **{marcador}** ➔ Votado por **{cantidad}** persona(s)")
                        else:
                            st.write("Ningún familiar registró pronósticos para este encuentro.")

            # --- PESTAÑA: POSICIONES ---
            with tab_posiciones:
                st.subheader("📊 Ranking de Pronósticos")
                st.write("*(Los saldos totales son secretos 🤫. Aquí solo se muestra el rendimiento de las apuestas)*")
                
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
                        "Total Invertido": apostado_total,
                        "Rendimiento Neto": balance_neto
                    })
                    
                if datos_ranking:
                    df_ranking = pd.DataFrame(datos_ranking)
                    df_ranking = df_ranking.sort_values(by="Rendimiento Neto", ascending=False).reset_index(drop=True)
                    st.dataframe(df_ranking, use_container_width=True)
                else:
                    st.info("Aún no hay estadísticas suficientes para generar el ranking.")

            # --- PESTAÑA: CONTROL ---
            with tab_control:
                st.subheader("⚙️ Panel de Administración y Respaldos")
                st.info("Descarga los archivos actualizados al final del día y súbelos a tu repositorio para guardar los cambios permanentemente.")
                
                st.markdown("---")
                st.subheader("🏦 Repartición de Premios")
                st.write("Presiona este botón después de poner un partido en estado 'finalizado' para transferir las ganancias automáticamente.")
                
                if st.button("Calcular y Pagar Premios Pendientes"):
                    cambios_realizados = False
                    
                    for p in partidos:
                        if p.get("estado") == "finalizado":
                            g1_real = p.get("goles_1_real")
                            g2_real = p.get("goles_2_real")
                            
                            # Verificamos que los goles reales sí estén registrados en el JSON
                            if g1_real is not None and g2_real is not None:
                                
                                for pron in pronosticos:
                                    # Buscamos apuestas de este partido que no tengan la etiqueta 'pagado'
                                    if pron["id_partido"] == p["id_partido"] and not pron.get("pagado", False):
                                        g1_pron = pron["goles_1_pronostico"]
                                        g2_pron = pron["goles_2_pronostico"]
                                        monto = pron.get("monto_apostado", 0)
                                        
                                        multiplicador = 0
                                        
                                        # 1. Acierto de Marcador (x10)
                                        if g1_real == g1_pron and g2_real == g2_pron:
                                            multiplicador = 10
                                        # 2. Acierto de Diferencia o Empate (x6)
                                        elif (g1_real - g2_real) == (g1_pron - g2_pron):
                                            multiplicador = 6
                                        # 3. Acierto de Ganador (x4)
                                        elif (g1_real > g2_real and g1_pron > g2_pron) or (g1_real < g2_real and g1_pron < g2_pron):
                                            multiplicador = 4
                                            
                                        ganancia = monto * multiplicador
                                        
                                        # Actualizamos la base de datos de la apuesta
                                        pron["puntos_ganados"] = ganancia
                                        pron["pagado"] = True # Candado de seguridad para no pagar dos veces
                                        
                                        # Depositamos los Sobolevs ganados al usuario
                                        if ganancia > 0:
                                            for u in usuarios:
                                                if u["nombre"] == pron["usuario"]:
                                                    u["monedas"] += ganancia
                                                    break
                                                    
                                        cambios_realizados = True
                                        
                    if cambios_realizados:
                        guardar_datos("usuarios.json", usuarios)
                        guardar_datos("pronosticos.json", pronosticos)
                        st.success("✅ ¡Premios calculados! Los multiplicadores han sido aplicados y el dinero está en sus billeteras.")
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
            # Se añade esta alerta visual por si escriben mal el PIN
            st.error("❌ PIN incorrecto. No tienes autorización para ingresar.")
else:
    st.error("No hay usuarios registrados en la base de datos JSON.")