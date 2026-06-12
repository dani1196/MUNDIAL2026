import streamlit as st
import pandas as pd
import json
import os

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Prode Mundial", page_icon="🏆", layout="centered")

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
nombres_usuarios = [u["nombre"] for u in usuarios]

# ==========================================
# 2. ENCABEZADO (Siempre visible)
# ==========================================
st.title("🏆 Prode Familiar")

if nombres_usuarios:
    # Este selector rige para toda la app, sin importar en qué pestaña estés
    usuario_actual = st.selectbox("👤 ¿Quién está usando la app?", nombres_usuarios)
    
    saldo_actual = 0
    for u in usuarios:
        if u["nombre"] == usuario_actual:
            saldo_actual = u["monedas"]
            
    st.markdown(f"**Tu saldo actual:** {saldo_actual} Sobolevs")
    st.markdown("---")

    # ==========================================
    # 3. CREACIÓN DE LAS PESTAÑAS
    # ==========================================
    tab_tienda, tab_apuestas, tab_posiciones = st.tabs([
        "🛒 Tienda", 
        "⚽ Apuestas", 
        "🏆 Posiciones"
    ])

    # --- PESTAÑA 1: LA TIENDA ---
    with tab_tienda:
        st.subheader("🏦 Comprar Sobolevs")
        dolares = st.number_input("Monto en Dólares ($)", min_value=1.0, step=1.0)
        sobolevs_a_recibir = int(dolares * 10)
        
        st.info(f"Recibirás: **{sobolevs_a_recibir} Sobolevs**")
        
        if st.button("Confirmar Compra"):
            for u in usuarios:
                if u["nombre"] == usuario_actual:
                    u["monedas"] += sobolevs_a_recibir
            
            guardar_datos("usuarios.json", usuarios)
            st.success(f"¡Compra exitosa! Tienes {sobolevs_a_recibir} Sobolevs más.")
            st.rerun() # Actualiza la página para reflejar el nuevo saldo arriba

    # --- PESTAÑA 2: LOS PARTIDOS ---
    with tab_apuestas:
        st.subheader("📅 Partidos Disponibles")
        st.write("*(Aquí mostraremos la lista de partidos de partidos.json para que puedas ingresar tus pronósticos)*")
        # Más adelante conectaremos esto con partidos.json y pronosticos.json

    # --- PESTAÑA 3: TABLA DE POSICIONES ---
    with tab_posiciones:
        st.subheader("📊 Ranking Familiar")
        
        # Convertimos la lista de usuarios en una tabla ordenada usando Pandas
        if usuarios:
            df_posiciones = pd.DataFrame(usuarios)
            # Renombramos las columnas para que se vean mejor
            df_posiciones = df_posiciones.rename(columns={"nombre": "Familiar", "monedas": "Sobolevs"})
            # Ordenamos de mayor a menor cantidad de Sobolevs
            df_posiciones = df_posiciones.sort_values(by="Sobolevs", ascending=False).reset_index(drop=True)
            # Quitamos la columna ID que no necesitamos mostrar
            df_posiciones = df_posiciones[["Familiar", "Sobolevs"]]
            
            # Mostramos la tabla adaptada al ancho de la pantalla
            st.dataframe(df_posiciones, use_container_width=True)

else:
    st.error("No hay usuarios registrados en usuarios.json.")