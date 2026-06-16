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
# Identificar las reservas del banco
if not df_usuarios.empty and "Banco" in df_usuarios["nombre"].values:
    datos_banco = df_usuarios[df_usuarios["nombre"] == "Banco"].iloc[0]
    dolares_reserva = float(datos_banco["dolares_depositados"])
    sobolevs_reserva = float(datos_banco["monedas"])
else:
    dolares_reserva = 0.0
    sobolevs_reserva = 0.0

# Cálculo de la tasa de cambio dinámica
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

# Mostramos únicamente el Tipo de Cambio, centrado para mejor estética
col_vacia1, col_tasa, col_vacia2 = st.columns([1, 2, 1])
with col_tasa:
    st.metric("Cambio actual", f"{tasa_actual:.2f} Sobolevs por cada USD")

st.markdown("---")

nombres_jugadores = df_usuarios[df_usuarios["nombre"] != "Banco"]["nombre"].tolist() if not df_usuarios.empty else []

if nombres_jugadores:
    # Selector de usuario (sigue siendo libre la selección inicial)
    usuario_seleccionado = st.selectbox("👤 Identifícate:", nombres_jugadores)
    
    # Buscamos los datos y el PIN del usuario seleccionado en el archivo
    datos_usuario_sel = df_usuarios[df_usuarios["nombre"] == usuario_seleccionado].iloc[0]
    pin_correcto = str(datos_usuario_sel.get("pin", "1234"))
    
    # Campo para ingresar la contraseña (se ocultan los caracteres con tipo 'password')
    pin_ingresado = st.text_input("🔑 Ingresa tu PIN de acceso:", type="password", key=f"pin_{usuario_seleccionado}")
    
    # VALIDACIÓN: Solo si el PIN coincide, se permite ver y usar la aplicación
    if pin_ingresado == pin_correcto:
        usuario_actual = usuario_seleccionado
        saldo_usuario = datos_usuario_sel["monedas"]
        
        st.success(f"🔓 Acceso concedido a la sesión de {usuario_actual}")

        # Agregamos "tab_perfil" a la lista de pestañas
        tab_tienda, tab_apuestas, tab_posiciones, tab_control, tab_perfil = st.tabs([
            "🛒 Tienda", "⚽ Apuestas", "📊 Posiciones", "⚙️ Control", "🔐 Mi Perfil"
        ])
        # --- PESTAÑA: MI PERFIL (Seguridad) ---
        with tab_perfil:
            st.subheader("🔐 Seguridad de la Cuenta")
            st.write("Aquí puedes cambiar tu clave de acceso. ¡Asegúrate de no olvidarla!")
            
            # Usamos st.form para que no se recargue la página mientras escriben
            with st.form(key=f"form_pin_{usuario_actual}"):
                nuevo_pin = st.text_input("Escribe tu nuevo PIN:", type="password")
                confirmar_pin = st.text_input("Confirma tu nuevo PIN:", type="password")
                
                boton_actualizar_pin = st.form_submit_button("Actualizar Contraseña")
                
                if boton_actualizar_pin:
                    if nuevo_pin == confirmar_pin and len(nuevo_pin.strip()) > 0:
                        # 1. Buscamos al usuario en la lista y le cambiamos el PIN
                        for u in usuarios:
                            if u["nombre"] == usuario_actual:
                                u["pin"] = nuevo_pin
                                break
                        
                        # 2. Guardamos los cambios permanentemente en el archivo JSON
                        guardar_datos("usuarios.json", usuarios)
                        
                        st.success("✅ ¡Tu contraseña ha sido actualizada con éxito!")
                        # No usamos st.rerun() aquí inmediatamente para que el usuario alcance a leer el mensaje de éxito
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
                # Actualizar saldos en JSON
                for u in usuarios:
                    if u["nombre"] == usuario_actual:
                        u["monedas"] += sobolevs_comprados
                        u["dolares_depositados"] += dolares
                    if u["nombre"] == "Banco":
                        u["dolares_depositados"] += dolares
                
                guardar_datos("usuarios.json", usuarios)
                
                # Escribir en el archivo de texto (Historial)
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                registro = f"[{fecha_hora}] Usuario: {usuario_actual} | Depósito: ${dolares} | Sobolevs: {sobolevs_comprados}\n"
                
                with open("historial_depositos.txt", "a", encoding="utf-8") as f_log:
                    f_log.write(registro)
                    
                st.success("¡Transacción procesada y registrada en el historial!")
                st.rerun()

            st.markdown("---")
            st.write("📄 **Auditoría del Banco Central**")
            
            # Botón para descargar el archivo de texto a tu computadora
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
            
            # 1. Clasificamos los partidos automáticamente
            for p in partidos:
                if p.get("estado") != "futuro": # Ignoramos los partidos de fases finales aún no definidos
                    fecha_str = p.get("fecha", "")
                    hora_str = p.get("hora", "23:59")
                    try:
                        fecha_partido = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
                        # Si aún no es la hora, está abierto
                        if hora_actual_local < fecha_partido and p.get("estado") == "pendiente":
                            partidos_abiertos.append(p)
                        else:
                            # Si ya pasó la hora o ya finalizó, está cerrado
                            partidos_cerrados.append((p, fecha_partido))
                    except ValueError:
                        pass
            
            # ==========================================
            # SECCIÓN 1: PARTIDOS PARA PRONOSTICAR
            # ==========================================
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
                    
                    with st.form(key=f"form_apuesta_{id_p}"):
                        st.write(f"**Partido {id_p}** | {partido.get('fecha', '')} {hora_partido}")
                        
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                        with col1:
                            st.markdown(f"<h4 style='text-align: right;'>{equipo1}</h4>", unsafe_allow_html=True)
                        with col2:
                            goles1 = st.number_input("Goles", min_value=0, max_value=15, step=1, key=f"g1_{id_p}")
                        with col3:
                            goles2 = st.number_input("Goles", min_value=0, max_value=15, step=1, key=f"g2_{id_p}")
                        with col4:
                            st.markdown(f"<h4>{equipo2}</h4>", unsafe_allow_html=True)
                            
                        st.markdown("---")
                        max_apuesta = int(saldo_usuario) if saldo_usuario > 0 else 1
                        monto_apostado = st.number_input("Sobolevs a invertir:", min_value=1, max_value=max_apuesta, step=1, key=f"monto_{id_p}")
                        
                        boton_apostar = st.form_submit_button("Guardar Pronóstico")
                        
                        if boton_apostar:
                            hora_verificacion = datetime.utcnow() - timedelta(hours=5)
                            if hora_verificacion >= datetime.strptime(f"{partido.get('fecha')} {partido.get('hora', '23:59')}", "%Y-%m-%d %H:%M"):
                                st.error("❌ Demasiado tarde. El partido ya ha comenzado.")
                                continue

                            if saldo_usuario >= monto_apostado:
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
                                    
                                st.success(f"¡Inversión de {monto_apostado} Sobolevs registrada!")
                                st.rerun()
                            else:
                                st.error("❌ No tienes suficientes Sobolevs.")
                                
            # ==========================================
            # SECCIÓN 2: PARTIDOS CERRADOS (Tendencias)
            # ==========================================
            st.markdown("---")
            st.subheader("🔒 Partidos en Juego / Finalizados")
            st.write("*(Mira qué marcadores predijo la familia. Los nombres se mantienen en secreto 🤫)*")
            
            # Ordenamos los partidos para que los más recientes salgan primero
            partidos_cerrados.sort(key=lambda x: x[1], reverse=True)
            
            for p, _ in partidos_cerrados:
                id_p = p["id_partido"]
                equipo1 = p["equipo_1"]
                equipo2 = p["equipo_2"]
                estado = p.get("estado", "pendiente")
                
                # Usamos st.expander para que no ocupe toda la pantalla a menos que el usuario le dé clic
                with st.expander(f"Partido {id_p}: {equipo1} vs {equipo2} ({estado.capitalize()})"):
                    
                    # Si el partido ya acabó y tú pusiste los goles reales en el JSON, se mostrarán aquí:
                    if estado == "finalizado":
                        st.success(f"**Resultado Final:** {equipo1} **{p.get('goles_1_real')} - {p.get('goles_2_real')}** {equipo2}")
                    
                    # Buscamos todas las apuestas asociadas a este ID de partido
                    apuestas_partido = [pron for pron in pronosticos if pron["id_partido"] == id_p]
                    
                    if apuestas_partido:
                        conteo_marcadores = {}
                        # Agrupamos cuántas veces se repite exactamente el mismo marcador
                        for pron in apuestas_partido:
                            marcador = f"{pron['goles_1_pronostico']} - {pron['goles_2_pronostico']}"
                            conteo_marcadores[marcador] = conteo_marcadores.get(marcador, 0) + 1
                        
                        st.markdown("**Tendencias del Mercado:**")
                        # Ordenamos para mostrar los marcadores más votados arriba
                        for marcador, cantidad in sorted(conteo_marcadores.items(), key=lambda x: x[1], reverse=True):
                            st.write(f"📊 Marcador **{marcador}** ➔ Votado por **{cantidad}** persona(s)")
                    else:
                        st.write("Ningún familiar registró pronósticos para este encuentro.")
        # --- PESTAÑA: POSICIONES ---
        with tab_posiciones:
            st.subheader("📊 Ranking de Pronósticos")
            st.write("*(Los saldos totales son secretos 🤫. Aquí solo se muestra el rendimiento de las apuestas)*")
            
            datos_ranking = []
            
            # Recorremos cada usuario para calcular sus estadísticas
            for u in usuarios:
                if u["nombre"] == "Banco": 
                    continue # Omitimos al banco del ranking
                    
                nombre_familiar = u["nombre"]
                apostado_total = 0
                balance_neto = 0
                
                # Buscamos todas las apuestas de este familiar
                for pron in pronosticos:
                    if pron["usuario"] == nombre_familiar:
                        monto = pron.get("monto_apostado", 0)
                        ganado = pron.get("puntos_ganados", 0)
                        
                        apostado_total += monto
                        
                        # Buscamos el estado del partido apostado
                        estado_partido = "pendiente"
                        for p in partidos:
                            if p["id_partido"] == pron["id_partido"]:
                                estado_partido = p.get("estado", "pendiente")
                                break
                        
                        # Solo calculamos pérdidas/ganancias si el partido ya terminó
                        if estado_partido == "finalizado":
                            balance_neto += (ganado - monto)
                
                # Agregamos los datos calculados a nuestra lista
                datos_ranking.append({
                    "Familiar": nombre_familiar,
                    "Total Invertido": apostado_total,
                    "Rendimiento Neto": balance_neto
                })
                
            # Convertimos la lista en una tabla visual con Pandas
            if datos_ranking:
                df_ranking = pd.DataFrame(datos_ranking)
                # Ordenamos para que el que tenga mayor rendimiento neto esté primero
                df_ranking = df_ranking.sort_values(by="Rendimiento Neto", ascending=False).reset_index(drop=True)
                
                # Mostramos la tabla
                st.dataframe(df_ranking, use_container_width=True)
            else:
                st.info("Aún no hay estadísticas suficientes para generar el ranking.")

        # --- PESTAÑA: CONTROL ---
        with tab_control:
            st.subheader("⚙️ Panel de Administración y Respaldos")
            st.info("Descarga los archivos actualizados al final del día y súbelos a tu repositorio para guardar los cambios permanentemente.")
            
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

else:
    st.error("No hay usuarios registrados en la base de datos JSON.")