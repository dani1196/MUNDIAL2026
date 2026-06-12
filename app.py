import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="Prode Financiero", page_icon="📊", layout="centered")

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
        st.subheader("Tus Pronósticos")
        st.write("*(Los partidos se cargarán desde partidos.json)*")

    # --- PESTAÑA: POSICIONES ---
    with tab_posiciones:
        st.subheader("Ranking Familiar")
        df_ranking = df_usuarios[df_usuarios["nombre"] != "Banco"][["nombre", "monedas"]].sort_values(by="monedas", ascending=False)
        df_ranking = df_ranking.rename(columns={"nombre": "Familiar", "monedas": "Sobolevs"})
        st.dataframe(df_ranking.reset_index(drop=True), use_container_width=True)

    # --- PESTAÑA: CONTROL ---
    with tab_control:
        st.subheader("Información del Sistema")
        st.write("Estás utilizando bases de datos en formato JSON. Para actualizaciones permanentes, modifica los archivos directamente en tu editor o en GitHub.")

else:
    st.error("No hay usuarios registrados en la base de datos JSON.")