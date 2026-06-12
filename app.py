import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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

col_usd, col_sob, col_tasa = st.columns(3)
with col_usd:
    st.metric("Reservas del Banco", f"${dolares_reserva:.2f}")
with col_sob:
    st.metric("Liquidez del Banco", f"{sobolevs_reserva:.0f} Sob")
with col_tasa:
    st.metric("Tipo de Cambio", f"{tasa_actual:.2f} Sob/USD")

st.markdown("---")

nombres_jugadores = df_usuarios[df_usuarios["nombre"] != "Banco"]["nombre"].tolist() if not df_usuarios.empty else []

if nombres_jugadores:
    usuario_actual = st.selectbox("👤 Identifícate:", nombres_jugadores)
    
    saldo_usuario = df_usuarios[df_usuarios["nombre"] == usuario_actual].iloc[0]["monedas"]
    st.warning(f"Tu billetera: **{saldo_usuario:.2f} Sobolevs**")

    tab_tienda, tab_apuestas, tab_posiciones, tab_control = st.tabs([
        "🛒 Tienda", "⚽ Apuestas", "📊 Posiciones", "⚙️ Control"
    ])

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
        st.subheader("📅 Partidos Disponibles")
        
        partidos_pendientes = [p for p in partidos if p.get("estado") == "pendiente"]
        
        if not partidos_pendientes:
            st.info("No hay partidos pendientes para apostar en este momento.")
        else:
            for partido in partidos_pendientes:
                id_p = partido["id_partido"]
                equipo1 = partido["equipo_1"]
                equipo2 = partido["equipo_2"]
                
                with st.form(key=f"form_apuesta_{id_p}"):
                    st.write(f"**Partido {id_p}** | {partido.get('fecha', '')}")
                    
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
                    # Nuevo selector de inversión dinámico
                    max_apuesta = int(saldo_usuario) if saldo_usuario > 0 else 1
                    monto_apostado = st.number_input("Sobolevs a invertir en este pronóstico:", min_value=1, max_value=max_apuesta, step=1, key=f"monto_{id_p}")
                    
                    boton_apostar = st.form_submit_button("Guardar Pronóstico")
                    
                    if boton_apostar:
                        if saldo_usuario >= monto_apostado:
                            apuesta_existente = False
                            
                            # Revisar si ya existía una apuesta previa para este partido
                            for pron in pronosticos:
                                if pron["usuario"] == usuario_actual and pron["id_partido"] == id_p:
                                    # Reembolsar el monto de la apuesta anterior al usuario
                                    monto_anterior = pron.get("monto_apostado", 0)
                                    for u in usuarios:
                                        if u["nombre"] == usuario_actual:
                                            u["monedas"] += monto_anterior
                                            
                                    # Actualizar el pronóstico con los nuevos valores
                                    pron["goles_1_pronostico"] = goles1
                                    pron["goles_2_pronostico"] = goles2
                                    pron["monto_apostado"] = monto_apostado
                                    apuesta_existente = True
                                    break
                            
                            if not apuesta_existente:
                                # Es una apuesta nueva
                                nuevo_pronostico = {
                                    "usuario": usuario_actual,
                                    "id_partido": id_p,
                                    "goles_1_pronostico": goles1,
                                    "goles_2_pronostico": goles2,
                                    "monto_apostado": monto_apostado,
                                    "puntos_ganados": 0
                                }
                                pronosticos.append(nuevo_pronostico)

                            # Descontar el nuevo monto apostado del saldo actual
                            for u in usuarios:
                                if u["nombre"] == usuario_actual:
                                    u["monedas"] -= monto_apostado
                            
                            # Guardar bases de datos JSON
                            guardar_datos("usuarios.json", usuarios)
                            guardar_datos("pronosticos.json", pronosticos)
                            
                            # Registrar en el archivo de texto para auditoría
                            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            registro_apuesta = f"[{fecha_hora}] APUESTA | Usuario: {usuario_actual} | Partido {id_p} ({equipo1} vs {equipo2}) | Goles: {goles1}-{goles2} | Monto: {monto_apostado} Sobolevs\n"
                            with open("historial_apuestas.txt", "a", encoding="utf-8") as f_log:
                                f_log.write(registro_apuesta)
                                
                            st.success(f"¡Inversión de {monto_apostado} Sobolevs registrada con éxito!")
                            st.rerun()
                        else:
                            st.error("❌ No tienes suficientes Sobolevs para esta apuesta.")

    # --- PESTAÑA: POSICIONES ---
    with tab_posiciones:
        st.subheader("Ranking Familiar")
        df_ranking = df_usuarios[df_usuarios["nombre"] != "Banco"][["nombre", "monedas"]].sort_values(by="monedas", ascending=False)
        df_ranking = df_ranking.rename(columns={"nombre": "Familiar", "monedas": "Sobolevs"})
        st.dataframe(df_ranking.reset_index(drop=True), use_container_width=True)

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