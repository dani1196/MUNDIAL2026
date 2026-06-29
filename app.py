import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Sobolev", page_icon="⚽", layout="centered")

# ==========================================
# DICCIONARIO DE BANDERAS
# ==========================================
banderas = {
    "Ecuador": "🇪🇨",
    "Ghana": "🇬🇭",
    "Panamá": "🇵🇦",
    "Uzbekistán": "🇺🇿",
    "Colombia": "🇨🇴",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Croacia": "🇭🇷",
    "Portugal": "🇵🇹",
    "RD Congo": "🇨🇩",
    "Austria": "🇦🇹",
    "Jordania": "🇯🇴",
    "Argentina": "🇦🇷",
    "Argelia": "🇩🇿",
    "Irak": "🇮🇶",
    "Noruega": "🇳🇴",
    "Francia": "🇫🇷",
    "Senegal": "🇸🇳",
    "Arabia Saudita": "🇸🇦",
    "Uruguay": "🇺🇾",
    "Irán": "🇮🇷",
    "Nueva Zelanda": "🇳🇿",
    "España": "🇪🇸",
    "Cabo Verde": "🇨🇻",
    "Bélgica": "🇧🇪",
    "Egipto": "🇪🇬",
    "Canadá": "🇨🇦",
    "Bosnia y Herzegovina": "🇧🇦",
    "Corea del Sur": "🇰🇷",
    "República Checa": "🇨🇿",
    "México": "🇲🇽",
    "Sudáfrica": "🇿🇦",
    "Brasil": "🇧🇷",
    "Alemania": "🇩🇪",
    "Italia": "🇮🇹",
    "Países Bajos": "🇳🇱",
    "Estados Unidos": "🇺🇸",
    "Japón": "🇯🇵",
    "Marruecos": "🇲🇦",
    "Suiza": "🇨🇭",
    "Catar": "🇶🇦",
    "Australia": "🇦🇺",
    "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Paraguay": "🇵🇾",
    "Turquía": "🇹🇷",
    "Costa de Marfil": "🇨🇮",
    "Curazao": "🇨🇼",
    "Suecia": "🇸🇪",
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
# CÁLCULO DE TASA DE CAMBIO (SOBOLEVS POR USD)
# ==========================================
if not df_usuarios.empty and "Banco" in df_usuarios["nombre"].values:
    datos_banco = df_usuarios[df_usuarios["nombre"] == "Banco"].iloc[0]
    dolares_reserva = float(datos_banco["dolares_depositados"])
else:
    dolares_reserva = 0.0

# Total de Sobolevs en manos de los usuarios
total_sobolevs_emitidos = df_usuarios[df_usuarios["nombre"] != "Banco"]["monedas"].sum()

if total_sobolevs_emitidos > 0 and dolares_reserva > 0:
    # Calculamos cuántos Sobolevs da el banco por cada 1 dólar
    sobolevs_por_dolar = total_sobolevs_emitidos / dolares_reserva
else:
    # Tasa inicial por defecto si no hay dinero ni monedas aún
    sobolevs_por_dolar = 10.0


# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.title("🏆 Mundial 2026")

# Mostramos el resultado del cálculo anterior
st.metric(label="💵 $1 equivale", value=f"{sobolevs_por_dolar:.2f} Sobolevs")
st.markdown("---")

nombres_jugadores = [u["nombre"] for u in usuarios if u["nombre"] != "Banco"]

if nombres_jugadores:
    usuario_seleccionado = st.selectbox("👤 Identifícate:", nombres_jugadores)

    datos_usuario_sel = next(
        (u for u in usuarios if u["nombre"] == usuario_seleccionado), None
    )

    if datos_usuario_sel:
        pin_correcto = str(datos_usuario_sel.get("pin", "1234")).strip()
        pin_ingresado = st.text_input(
            "🔑 Ingresa tu PIN de acceso:",
            type="password",
            key=f"pin_{usuario_seleccionado}",
        ).strip()

        if pin_ingresado == pin_correcto:
            usuario_actual = usuario_seleccionado
            saldo_usuario = datos_usuario_sel["monedas"]

            st.success(f"🔓 Acceso concedido a la sesión de {usuario_actual}")

            st.sidebar.subheader("🏦 Tu Billetera")
            usuarios_frescos = cargar_datos("usuarios.json", [])
            saldo_fresco = next(
                (
                    u["monedas"]
                    for u in usuarios_frescos
                    if u["nombre"] == usuario_actual
                ),
                0,
            )

            st.sidebar.metric("Sobolevs Disponibles", f"{saldo_fresco} 💰")
            st.sidebar.markdown("---")

            # Declaración dinámica de pestañas
            titulos_pestanas = [
                "🔐 Mi Perfil",
                "🛒 Tienda",
                "⚽ Apuestas",
                "📊 Posiciones",
                "📝 Resultados",
                "📜 Reglas",
                "📢 Edictos",
            ]

            if usuario_actual == "Daniela":
                titulos_pestanas.append("⚙️ Control")

            pestanas = st.tabs(titulos_pestanas)

            tab_perfil = pestanas[0]
            tab_tienda = pestanas[1]
            tab_apuestas = pestanas[2]
            tab_posiciones = pestanas[3]
            tab_resultados = pestanas[4]
            tab_reglas = pestanas[5]
            tab_edictos = pestanas[6]

            if usuario_actual == "Daniela":
                tab_control = pestanas[7]

            # --- PESTAÑA: MI PERFIL ---
            with tab_perfil:
                st.subheader("👤 Mi Perfil y Estadísticas")

                # ==========================================
                # ESTADÍSTICAS DEL JUGADOR
                # ==========================================
                mis_pronosticos = [
                    pron for pron in pronosticos if pron["usuario"] == usuario_actual
                ]

                total_apuestas = len(mis_pronosticos)
                total_invertido = sum(
                    p.get("monto_apostado", 0) for p in mis_pronosticos
                )
                apuestas_ganadas = sum(
                    1 for p in mis_pronosticos if p.get("puntos_ganados", 0) > 0
                )

                col_est1, col_est2, col_est3 = st.columns(3)
                with col_est1:
                    st.metric("Sobolevs Invertidos", f"{total_invertido} 💰")
                with col_est2:
                    st.metric("Apuestas Realizadas", f"{total_apuestas} 🎟️")
                with col_est3:
                    st.metric("Apuestas Ganadas", f"{apuestas_ganadas} 🏆")

                # ==========================================
                # HISTORIAL DE APUESTAS
                # ==========================================
                st.markdown("---")
                st.subheader("📋 Mi Historial de Apuestas")

                if mis_pronosticos:
                    historial_data = []
                    for p in reversed(mis_pronosticos):
                        id_p = p["id_partido"]
                        g1 = p["goles_1_pronostico"]
                        g2 = p["goles_2_pronostico"]
                        monto = p.get("monto_apostado", 0)
                        ganancia = p.get("puntos_ganados", 0)
                        pagado = p.get("pagado", False)

                        # Manejo visual de penales
                        penales_str = ""
                        if (
                            p.get("penales_1_pronostico") is not None
                            and p.get("penales_2_pronostico") is not None
                        ):
                            penales_str = f" (P: {p['penales_1_pronostico']}-{p['penales_2_pronostico']})"

                        if ganancia > 0:
                            estado = "✅ Ganada"
                        elif pagado and ganancia == 0:
                            estado = "❌ Perdida"
                        else:
                            estado = "⏳ Pendiente"

                        equipo1, equipo2 = "Equipo 1", "Equipo 2"
                        b1, b2 = "🏳️", "🏳️"
                        for partido in partidos:
                            if partido["id_partido"] == id_p:
                                equipo1 = partido["equipo_1"]
                                equipo2 = partido["equipo_2"]
                                b1 = banderas.get(equipo1, "🏳️")
                                b2 = banderas.get(equipo2, "🏳️")
                                break

                        historial_data.append(
                            {
                                "Partido": f"{b1} {equipo1} vs {b2} {equipo2}",
                                "Mi Pronóstico": f"{g1} - {g2}{penales_str}",
                                "Inversión": monto,
                                "Retorno": ganancia if estado == "✅ Ganada" else "-",
                                "Estado": estado,
                            }
                        )

                    df_historial = pd.DataFrame(historial_data)
                    st.dataframe(
                        df_historial, use_container_width=True, hide_index=True
                    )
                else:
                    st.info(
                        "Aún no has realizado ninguna apuesta. ¡Ve a la pestaña de Apuestas para empezar!"
                    )

                # ==========================================
                # SEGURIDAD DE LA CUENTA
                # ==========================================
                st.markdown("---")
                st.subheader("🔐 Seguridad de la Cuenta")
                st.write(
                    "Aquí puedes cambiar tu clave de acceso. ¡Asegúrate de no olvidarla!"
                )

                with st.form(key=f"form_pin_{usuario_actual}"):
                    nuevo_pin = st.text_input("Escribe tu nuevo PIN:", type="password")
                    confirmar_pin = st.text_input(
                        "Confirma tu nuevo PIN:", type="password"
                    )

                    boton_actualizar_pin = st.form_submit_button(
                        "Actualizar Contraseña"
                    )

                    if boton_actualizar_pin:
                        if nuevo_pin == confirmar_pin and len(nuevo_pin.strip()) > 0:
                            for u in usuarios:
                                if u["nombre"] == usuario_actual:
                                    u["pin"] = nuevo_pin.strip()
                                    break

                            guardar_datos("usuarios.json", usuarios)
                            st.success(
                                "✅ ¡Tu contraseña ha sido actualizada con éxito!"
                            )
                        elif nuevo_pin != confirmar_pin:
                            st.error(
                                "❌ Las contraseñas no coinciden. Inténtalo de nuevo."
                            )
                        else:
                            st.warning("⚠️ El PIN no puede estar completamente vacío.")

            # --- PESTAÑA: TIENDA ---
            with tab_tienda:
                st.subheader("Casa de Cambio Autorizada")
                st.write(
                    "⚠️ **Aviso:** Una vez verificado el depósito se aprobará la emisión de tus Sobolevs."
                )

                dolares = st.number_input(
                    "Cantidad de Dólares a depositar ($)", min_value=1.0, step=1.0
                )

                sobolevs_comprados = int(dolares * sobolevs_por_dolar)

                st.info(f"Recibirás **{sobolevs_comprados} Sobolevs**")

                if st.button("Solicitar Transacción"):
                    depositos_pendientes = cargar_datos("depositos_pendientes.json", [])

                    nuevo_deposito = {
                        "id_transaccion": len(depositos_pendientes) + 1,
                        "usuario": usuario_actual,
                        "dolares": dolares,
                        "sobolevs": sobolevs_comprados,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "estado": "pendiente",
                    }

                    depositos_pendientes.append(nuevo_deposito)
                    guardar_datos("depositos_pendientes.json", depositos_pendientes)

                    st.success(
                        "✅ ¡Solicitud enviada con éxito! Por favor, realiza la transferencia bancaria. Tus Sobolevs se cargarán en cuanto se apruebe la transacción."
                    )
                    st.rerun()

                st.markdown("---")
                st.subheader("📋 Mis Solicitudes de Recarga")

                depositos_historial = cargar_datos("depositos_pendientes.json", [])
                mis_depositos = [
                    d for d in depositos_historial if d["usuario"] == usuario_actual
                ]

                if mis_depositos:
                    datos_mostrar = []
                    for d in reversed(mis_depositos):
                        if d["estado"] == "aprobado":
                            estado_visual = "✅ Aprobada"
                        elif d["estado"] == "rechazado":
                            estado_visual = "❌ Rechazada"
                        else:
                            estado_visual = "⏳ En proceso"

                        datos_mostrar.append(
                            {
                                "Fecha": d["fecha"],
                                "Dólares": f"${d['dolares']}",
                                "Sobolevs": d["sobolevs"],
                                "Estado": estado_visual,
                            }
                        )

                    df_mis_depositos = pd.DataFrame(datos_mostrar)
                    st.dataframe(
                        df_mis_depositos, use_container_width=True, hide_index=True
                    )
                else:
                    st.info("Aún no has realizado ninguna solicitud de recarga.")

            # --- PESTAÑA: APUESTAS ---
            with tab_apuestas:
                if "mensaje_exito" in st.session_state:
                    st.success(st.session_state["mensaje_exito"])
                    del st.session_state["mensaje_exito"]

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
                            fecha_partido = datetime.strptime(
                                f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M"
                            )
                            hora_fin_estimada = fecha_partido + timedelta(hours=2)

                            if (
                                estado_json == "finalizado"
                                or hora_actual_local >= hora_fin_estimada
                            ):
                                partidos_finalizados.append((p, fecha_partido))
                            elif hora_actual_local >= fecha_partido:
                                partidos_en_curso.append((p, fecha_partido))
                            else:
                                partidos_abiertos.append(p)
                        except ValueError:
                            pass

                if partidos_en_curso:
                    st.subheader("🔥 Partidos en Curso")
                    st.write(
                        "*(El balón está rodando. Mira las tendencias de la familia 🤫)*"
                    )

                    partidos_en_curso.sort(key=lambda x: x[1], reverse=True)

                    for p, _ in partidos_en_curso:
                        id_p = p["id_partido"]
                        equipo1 = p["equipo_1"]
                        equipo2 = p["equipo_2"]
                        grupo = p.get("grupo", "")

                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")

                        with st.expander(
                            f"Partido {id_p} ({grupo}): {b1} {equipo1} vs {b2} {equipo2} - Cerrado (En Curso) 🟢"
                        ):
                            mi_apuesta = next(
                                (
                                    pron
                                    for pron in pronosticos
                                    if pron["usuario"] == usuario_actual
                                    and pron["id_partido"] == id_p
                                ),
                                None,
                            )

                            if mi_apuesta:
                                msj_apuesta = f"📝 **Tu pronóstico:** {b1} {equipo1} **{mi_apuesta['goles_1_pronostico']} - {mi_apuesta['goles_2_pronostico']}** {b2} {equipo2}"
                                if mi_apuesta.get("penales_1_pronostico") is not None:
                                    msj_apuesta += f" | ⚽ Penales: **{mi_apuesta['penales_1_pronostico']} - {mi_apuesta['penales_2_pronostico']}**"
                                msj_apuesta += f" | Inversión: **{mi_apuesta.get('monto_apostado', 0)}** Sobolevs"
                                st.info(msj_apuesta)
                            else:
                                st.warning(
                                    "No registraste ningún pronóstico para este encuentro."
                                )

                            st.markdown("---")

                            apuestas_partido = [
                                pron
                                for pron in pronosticos
                                if pron["id_partido"] == id_p
                            ]
                            if apuestas_partido:
                                conteo_marcadores = {}
                                for pron in apuestas_partido:
                                    marcador = f"{pron['goles_1_pronostico']} - {pron['goles_2_pronostico']}"
                                    if pron.get("penales_1_pronostico") is not None:
                                        marcador += f" (P: {pron['penales_1_pronostico']}-{pron['penales_2_pronostico']})"
                                    conteo_marcadores[marcador] = (
                                        conteo_marcadores.get(marcador, 0) + 1
                                    )

                                st.markdown("**Tendencias del Mercado (Anónimo):**")
                                for marcador, cantidad in sorted(
                                    conteo_marcadores.items(),
                                    key=lambda x: x[1],
                                    reverse=True,
                                ):
                                    st.write(
                                        f"📊 Marcador **{marcador}** ➔ Votado por **{cantidad}** persona(s)"
                                    )
                            else:
                                st.write(
                                    "Ningún familiar registró pronósticos para este encuentro."
                                )

                st.markdown("---")
                st.subheader("📅 Próximos Partidos Disponibles")

                if not partidos_abiertos:
                    st.info(
                        "No hay partidos abiertos para pronósticos en este momento."
                    )
                else:
                    st.warning(
                        f"🕒 Hora del servidor: {hora_actual_local.strftime('%H:%M:%S')}. Los formularios se bloquean al pitazo inicial."
                    )

                    partidos_abiertos.sort(
                        key=lambda x: datetime.strptime(
                            f"{x.get('fecha', '')} {x.get('hora', '23:59')}",
                            "%Y-%m-%d %H:%M",
                        )
                    )

                    for partido in partidos_abiertos:
                        id_p = partido["id_partido"]
                        equipo1 = partido["equipo_1"]
                        equipo2 = partido["equipo_2"]
                        hora_partido = partido.get("hora", "")
                        grupo = partido.get("grupo", "")

                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")

                        pick_actual = next(
                            (
                                pron
                                for pron in pronosticos
                                if pron["usuario"] == usuario_actual
                                and pron["id_partido"] == id_p
                            ),
                            None,
                        )

                        st.markdown("---")
                        if pick_actual:
                            msj_pick = f"👉 **Tu pick actual:** {b1} {equipo1} **{pick_actual['goles_1_pronostico']} - {pick_actual['goles_2_pronostico']}** {b2} {equipo2}"
                            if pick_actual.get("penales_1_pronostico") is not None:
                                msj_pick += f" | ⚽ Penales: **{pick_actual['penales_1_pronostico']} - {pick_actual['penales_2_pronostico']}**"
                            msj_pick += f" | Inversión: **{pick_actual['monto_apostado']}** Sobolevs."
                            st.info(msj_pick)

                        # Reemplazamos el st.form por un contenedor dinámico
                        st.write(
                            f"**Partido {id_p}** | **{grupo}** | {partido.get('fecha', '')} {hora_partido}"
                        )

                        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
                        with col1:
                            st.markdown(
                                f"<h4 style='text-align: right;'>{b1} {equipo1}</h4>",
                                unsafe_allow_html=True,
                            )
                        with col2:
                            default_g1 = (
                                int(pick_actual["goles_1_pronostico"])
                                if pick_actual
                                else 0
                            )
                            goles1 = st.number_input(
                                "Goles",
                                min_value=0,
                                max_value=15,
                                step=1,
                                value=default_g1,
                                key=f"g1_{id_p}",
                            )
                        with col3:
                            default_g2 = (
                                int(pick_actual["goles_2_pronostico"])
                                if pick_actual
                                else 0
                            )
                            goles2 = st.number_input(
                                "Goles",
                                min_value=0,
                                max_value=15,
                                step=1,
                                value=default_g2,
                                key=f"g2_{id_p}",
                            )
                        with col4:
                            st.markdown(
                                f"<h4>{b2} {equipo2}</h4>", unsafe_allow_html=True
                            )

                        # ==========================================
                        # LÓGICA DINÁMICA DE PENALES
                        # ==========================================
                        es_eliminatoria = "Grupo" not in grupo
                        penales_1, penales_2 = None, None

                        if es_eliminatoria and goles1 == goles2:
                            st.markdown("---")
                            st.write(
                                "⚽ **¡Empate!** En fase eliminatoria, define el marcador de los penales:"
                            )
                            col_p1, col_p2 = st.columns(2)
                            with col_p1:
                                def_p1 = (
                                    int(pick_actual.get("penales_1_pronostico", 0))
                                    if pick_actual
                                    and pick_actual.get("penales_1_pronostico")
                                    is not None
                                    else 0
                                )
                                penales_1 = st.number_input(
                                    f"Penales {equipo1}",
                                    min_value=0,
                                    max_value=20,
                                    step=1,
                                    value=def_p1,
                                    key=f"p1_{id_p}",
                                )
                            with col_p2:
                                def_p2 = (
                                    int(pick_actual.get("penales_2_pronostico", 0))
                                    if pick_actual
                                    and pick_actual.get("penales_2_pronostico")
                                    is not None
                                    else 0
                                )
                                penales_2 = st.number_input(
                                    f"Penales {equipo2}",
                                    min_value=0,
                                    max_value=20,
                                    step=1,
                                    value=def_p2,
                                    key=f"p2_{id_p}",
                                )
                            st.markdown("---")

                        max_apuesta = int(saldo_usuario) if saldo_usuario > 0 else 1
                        default_monto = (
                            int(pick_actual["monto_apostado"]) if pick_actual else 1
                        )
                        monto_apostado = st.number_input(
                            "Sobolevs a invertir:",
                            min_value=1,
                            max_value=max_apuesta + default_monto,
                            step=1,
                            value=default_monto,
                            key=f"monto_{id_p}",
                        )

                        texto_boton = (
                            "Actualizar Pronóstico"
                            if pick_actual
                            else "Guardar Pronóstico"
                        )

                        # Cambiamos st.form_submit_button por st.button
                        boton_apostar = st.button(
                            texto_boton, key=f"btn_apostar_{id_p}"
                        )

                        if boton_apostar:
                            hora_verificacion = datetime.utcnow() - timedelta(hours=5)
                            if hora_verificacion >= datetime.strptime(
                                f"{partido.get('fecha')} {partido.get('hora', '23:59')}",
                                "%Y-%m-%d %H:%M",
                            ):
                                st.error(
                                    "❌ Demasiado tarde. El partido ya ha comenzado."
                                )
                                continue

                            if (
                                saldo_usuario
                                + (pick_actual["monto_apostado"] if pick_actual else 0)
                                >= monto_apostado
                            ):
                                apuesta_existente = False
                                for pron in pronosticos:
                                    if (
                                        pron["usuario"] == usuario_actual
                                        and pron["id_partido"] == id_p
                                    ):
                                        monto_anterior = pron.get("monto_apostado", 0)
                                        for u in usuarios:
                                            if u["nombre"] == usuario_actual:
                                                u["monedas"] += monto_anterior

                                        pron["goles_1_pronostico"] = goles1
                                        pron["goles_2_pronostico"] = goles2
                                        pron["penales_1_pronostico"] = (
                                            penales_1
                                            if (es_eliminatoria and goles1 == goles2)
                                            else None
                                        )
                                        pron["penales_2_pronostico"] = (
                                            penales_2
                                            if (es_eliminatoria and goles1 == goles2)
                                            else None
                                        )
                                        pron["monto_apostado"] = monto_apostado
                                        apuesta_existente = True
                                        break

                                if not apuesta_existente:
                                    pronosticos.append(
                                        {
                                            "usuario": usuario_actual,
                                            "id_partido": id_p,
                                            "goles_1_pronostico": goles1,
                                            "goles_2_pronostico": goles2,
                                            "penales_1_pronostico": penales_1
                                            if (es_eliminatoria and goles1 == goles2)
                                            else None,
                                            "penales_2_pronostico": penales_2
                                            if (es_eliminatoria and goles1 == goles2)
                                            else None,
                                            "monto_apostado": monto_apostado,
                                            "puntos_ganados": 0,
                                        }
                                    )

                                for u in usuarios:
                                    if u["nombre"] == usuario_actual:
                                        u["monedas"] -= monto_apostado

                                guardar_datos("usuarios.json", usuarios)
                                guardar_datos("pronosticos.json", pronosticos)

                                registro_apuesta = f"[{hora_verificacion.strftime('%Y-%m-%d %H:%M:%S')}] APUESTA | {usuario_actual} | Partido {id_p} | Goles: {goles1}-{goles2}"
                                if penales_1 is not None and penales_2 is not None:
                                    registro_apuesta += (
                                        f" | Penales: {penales_1}-{penales_2}"
                                    )
                                registro_apuesta += f" | Monto: {monto_apostado}\n"

                                with open(
                                    "historial_apuestas.txt", "a", encoding="utf-8"
                                ) as f_log:
                                    f_log.write(registro_apuesta)

                                saldo_restante = (
                                    saldo_usuario
                                    + (
                                        pick_actual["monto_apostado"]
                                        if pick_actual
                                        else 0
                                    )
                                    - monto_apostado
                                )

                                msj_exito = f"🎯 ¡Pronóstico guardado! {b1} {equipo1} **{goles1} - {goles2}** {b2} {equipo2}"
                                if penales_1 is not None:
                                    msj_exito += (
                                        f" | ⚽ Penales: **{penales_1} - {penales_2}**"
                                    )
                                msj_exito += f" por **{monto_apostado}** Sobolevs. Tu saldo restante es: 💰 **{saldo_restante} Sobolevs**."

                                st.session_state["mensaje_exito"] = msj_exito
                                st.rerun()
                            else:
                                st.error("❌ No tienes suficientes Sobolevs.")

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

                        with st.expander(
                            f"Partido {id_p} ({grupo}): {b1} {equipo1} vs {b2} {equipo2} - Finalizado"
                        ):
                            if estado_json == "finalizado":
                                res_oficial = f"**Resultado Oficial:** {b1} {equipo1} **{p.get('goles_1_real')} - {p.get('goles_2_real')}** {b2} {equipo2}"
                                if p.get("penales_1_real") is not None:
                                    res_oficial += f" | ⚽ Penales: **{p.get('penales_1_real')} - {p.get('penales_2_real')}**"
                                st.success(res_oficial)
                            else:
                                st.warning(
                                    "⏳ Esperando que la administradora registre el resultado oficial para pagar los premios."
                                )

                            mi_apuesta = next(
                                (
                                    pron
                                    for pron in pronosticos
                                    if pron["usuario"] == usuario_actual
                                    and pron["id_partido"] == id_p
                                ),
                                None,
                            )

                            if mi_apuesta:
                                msj_apuesta = f"📝 **Tu pronóstico:** {b1} {equipo1} **{mi_apuesta['goles_1_pronostico']} - {mi_apuesta['goles_2_pronostico']}** {b2} {equipo2}"
                                if mi_apuesta.get("penales_1_pronostico") is not None:
                                    msj_apuesta += f" | ⚽ Penales: **{mi_apuesta['penales_1_pronostico']} - {mi_apuesta['penales_2_pronostico']}**"
                                msj_apuesta += f" | Inversión: **{mi_apuesta.get('monto_apostado', 0)}** Sobolevs"

                                st.info(msj_apuesta)
                                if estado_json == "finalizado":
                                    st.write(
                                        f"🏆 Ganancia obtenida: **{mi_apuesta.get('puntos_ganados', 0)} Sobolevs**"
                                    )
                            else:
                                st.warning(
                                    "No registraste ningún pronóstico para este encuentro."
                                )

                            st.markdown("---")

                            apuestas_partido = [
                                pron
                                for pron in pronosticos
                                if pron["id_partido"] == id_p
                            ]
                            if apuestas_partido:
                                conteo_marcadores = {}
                                for pron in apuestas_partido:
                                    marcador = f"{pron['goles_1_pronostico']} - {pron['goles_2_pronostico']}"
                                    if pron.get("penales_1_pronostico") is not None:
                                        marcador += f" (P: {pron['penales_1_pronostico']}-{pron['penales_2_pronostico']})"
                                    conteo_marcadores[marcador] = (
                                        conteo_marcadores.get(marcador, 0) + 1
                                    )

                                st.markdown("**Tendencias del Mercado (Anónimo):**")
                                for marcador, cantidad in sorted(
                                    conteo_marcadores.items(),
                                    key=lambda x: x[1],
                                    reverse=True,
                                ):
                                    st.write(
                                        f"📊 Marcador **{marcador}** ➔ Votado por **{cantidad}** persona(s)"
                                    )
                            else:
                                st.write(
                                    "Ningún familiar registró pronósticos para este encuentro."
                                )

            # --- PESTAÑA: POSICIONES ---
            with tab_posiciones:
                st.subheader("📊 Ranking de la Familia")
                st.write(
                    "*(El poder económico de Sobolevia. Quien tiene más Sobolevs disponibles, lidera la tabla)*"
                )

                datos_ranking = []

                for u in usuarios:
                    if u["nombre"] == "Banco":
                        continue

                    nombre_familiar = u["nombre"]
                    saldo_actual = u.get("monedas", 0)

                    datos_ranking.append(
                        {
                            "Familiar": nombre_familiar,
                            "Sobolevs Disponibles": saldo_actual,
                        }
                    )

                if datos_ranking:
                    df_ranking = pd.DataFrame(datos_ranking)
                    df_ranking = df_ranking.sort_values(
                        by="Sobolevs Disponibles", ascending=False
                    ).reset_index(drop=True)

                    df_ranking["Puesto"] = df_ranking.index + 1
                    df_ranking["Puesto"] = df_ranking["Puesto"].apply(lambda x: f"{x}º")

                    df_publico = df_ranking[
                        ["Puesto", "Familiar", "Sobolevs Disponibles"]
                    ]
                    st.dataframe(df_publico, use_container_width=True, hide_index=True)
                else:
                    st.info("Aún no hay usuarios suficientes para generar el ranking.")

            # --- PESTAÑA: RESULTADOS ---
            with tab_resultados:
                st.subheader("📝 Desglose de Resultados")
                st.write(
                    "*(Revisa de forma anónima los marcadores apostados y su nivel de acierto en los partidos finalizados)*"
                )

                partidos_terminados = [
                    p for p in partidos if p.get("estado") == "finalizado"
                ]

                if not partidos_terminados:
                    st.info(
                        "Aún no hay partidos finalizados con resultados oficiales registrados."
                    )
                else:
                    partidos_terminados.sort(
                        key=lambda x: x.get("id_partido", 0), reverse=True
                    )

                    for p in partidos_terminados:
                        id_p = p["id_partido"]
                        equipo1 = p["equipo_1"]
                        equipo2 = p["equipo_2"]
                        g1_real = p.get("goles_1_real")
                        g2_real = p.get("goles_2_real")
                        p1_real = p.get("penales_1_real")
                        p2_real = p.get("penales_2_real")

                        b1 = banderas.get(equipo1, "🏳️")
                        b2 = banderas.get(equipo2, "🏳️")

                        if g1_real is not None and g2_real is not None:
                            apuestas_partido = [
                                pron
                                for pron in pronosticos
                                if pron["id_partido"] == id_p
                            ]

                            if apuestas_partido:
                                titulo_exp = f"✅ Partido {id_p}: {b1} {equipo1} {g1_real} - {g2_real} {b2} {equipo2}"
                                if p1_real is not None:
                                    titulo_exp += f" (P: {p1_real}-{p2_real})"

                                with st.expander(titulo_exp):
                                    datos_desglose = []

                                    for pron in apuestas_partido:
                                        g1_p = pron["goles_1_pronostico"]
                                        g2_p = pron["goles_2_pronostico"]
                                        p1_p = pron.get("penales_1_pronostico")
                                        p2_p = pron.get("penales_2_pronostico")
                                        ganancia = pron.get("puntos_ganados", 0)
                                        monto = pron.get("monto_apostado", 1)

                                        # Determinamos el texto según el multiplicador pagado
                                        if ganancia > 0:
                                            if ganancia == (monto * 15):
                                                texto_acierto = "🔥 Penales Exactos"
                                            elif ganancia == (monto * 10):
                                                texto_acierto = "🎯 Marcador Exacto"
                                            elif ganancia == (monto * 6):
                                                texto_acierto = "⚖️ Diferencia"
                                            else:
                                                texto_acierto = "✅ Ganador"
                                        else:
                                            texto_acierto = "❌ Fallo"

                                        pron_str = f"{g1_p} - {g2_p}"
                                        if p1_p is not None:
                                            pron_str += f" (P: {p1_p}-{p2_p})"

                                        datos_desglose.append(
                                            {
                                                "Pronóstico": pron_str,
                                                "Resultado": texto_acierto,
                                            }
                                        )

                                    df_desglose = pd.DataFrame(datos_desglose)
                                    st.dataframe(
                                        df_desglose,
                                        use_container_width=True,
                                        hide_index=True,
                                    )
                            else:
                                titulo_exp = f"✅ Partido {id_p}: {b1} {equipo1} {g1_real} - {g2_real} {b2} {equipo2}"
                                with st.expander(titulo_exp):
                                    st.write(
                                        "Ningún familiar registró pronósticos para este encuentro."
                                    )

            # --- PESTAÑA: REGLAS ---
            with tab_reglas:
                st.subheader("📜 Reglas de Puntuación y Multiplicadores")
                st.write(
                    "Dependiendo de tu nivel de precisión en los pronósticos, tus Sobolevs invertidos se multiplicarán de la siguiente manera:"
                )

                st.markdown("""
                * **🔥 Acierto de Penales (x15):** En eliminatorias, aciertas el empate del partido y el marcador exacto de la tanda de penales. Tu inversión se multiplica por 15.
                * **🎯 Acierto de Marcador (x10):** Adivinas los goles exactos de ambos equipos. *(Ej: Pronosticas 2-1 y termina 2-1)*. Tu inversión se multiplica por 10.
                * **⚖️ Acierto de Diferencia (x6):** Adivinas el ganador y la diferencia de goles exacta (o el empate). *(Ej: Pronosticas 2-0 y termina 3-1, la diferencia de goles es +2)*. Tu inversión se multiplica por 6.
                * **✅ Acierto de Ganador (x4):** Solo adivinas quién gana o si hay empate, pero fallas la diferencia. *(Ej: Pronosticas 1-0 y termina 3-0)*. Tu inversión se multiplica por 4.
                * **❌ Fallo Total (x0):** No adivinas el resultado final. Pierdes tu inversión.
                """)
                st.info(
                    "💡 **Dato clave:** Puedes cambiar tu pronóstico y la cantidad invertida todas las veces que desees. La aplicación tomará únicamente la última apuesta registrada antes del inicio del partido."
                )

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
                            
                ---
                            
                ## 📜 EDICTO ESPECIAL: EL TRIUNFO DE LA FE 🇪🇨🔥
                            
                **A todos los participantes, visionarios, escépticos y matemáticos del fútbol:**

                Se hace saber y se proclama ante toda la comunidad que la Selección de Ecuador nos ha recordado la lección más grande que el deporte —y la vida— nos puede enseñar. 

                Considerando que: Mientras muchos sumaban números y analizaban estadísticas con la cabeza fría, un país entero jugaba con el corazón ardiendo. Celebramos más que tres puntos o una clasificación; celebramos el trinunfo sobre lo imposible.

                Se pone en conocimiento de todos los siguientes decretos: 
                
                ### 📢 DECRETO PRIMERO: DE LO IMPOSIBLE 
                Queda terminantemente prohibido volver a decir *"es imposible"*. Nos demostraron que **todo es imposible... hasta que se hace**. Las barreras solo existen en el papel, y la Tri las rompió en la cancha.

                ### 📢 DECRETO SEGUNDO: EL PODER DE CREER
                Se establece que, de ahora en adelante, **todo lo que somos capaces de soñar, somos capaces de lograrlo**. No importan los pronósticos en contra ni los dados cargados; el destino le pertenece a los que se atreven a creer hasta el último minuto del tiempo de descuento.

                > 💡 **Nota de la localía:** Sigan llenando sus cartillas, sigan apostando por sus corazonadas. Que si Ecuador pudo romper la historia, cualquiera de ustedes puede remontar en la tabla de posiciones. 

                Dado, firmado y sellado por el Comisionado en el fragor de la victoria. 

                **¡SI SE PUDO, SI SE PUEDE Y SIEMPRE SE PODRÁ!**
                """)

            # --- PESTAÑA: CONTROL (Exclusiva para Administradora) ---
            if usuario_actual == "Daniela":
                with tab_control:
                    st.subheader("⚙️ Panel de Administración y Respaldos")
                    st.info(
                        "Descarga los archivos actualizados al final del día y súbelos a tu repositorio para guardar los cambios permanentemente."
                    )

                    # ==========================================
                    # ESTADO DE LA BÓVEDA
                    # ==========================================
                    st.markdown("---")
                    st.subheader("🏦 Bóveda del Banco Central")

                    usuarios_banco = cargar_datos("usuarios.json", [])
                    datos_banco_actualizado = next(
                        (u for u in usuarios_banco if u["nombre"] == "Banco"), None
                    )

                    if datos_banco_actualizado:
                        total_circulacion = sum(
                            u["monedas"]
                            for u in usuarios_banco
                            if u["nombre"] != "Banco"
                        )
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            st.metric(
                                "Sobolevs en Circulación", f"{total_circulacion} 💰"
                            )
                        with col_b2:
                            st.metric(
                                "Respaldo Total (Dólares)",
                                f"${datos_banco_actualizado['dolares_depositados']:.2f} 💵",
                            )
                    else:
                        st.warning("No se encontró la cuenta 'Banco' en usuarios.json.")

                    # ==========================================
                    # APROBACIÓN DE DEPÓSITOS
                    # ==========================================
                    st.markdown("---")
                    st.subheader("🏦 Bandeja de Depósitos Pendientes")
                    st.write(
                        "Aprueba las recargas únicamente cuando hayas confirmado que el dinero está en tu cuenta bancaria real."
                    )

                    depositos_pendientes = cargar_datos("depositos_pendientes.json", [])
                    pendientes = [
                        d
                        for d in depositos_pendientes
                        if d.get("estado") == "pendiente"
                    ]

                    if not pendientes:
                        st.info(
                            "Todo al día. No hay solicitudes de recarga pendientes."
                        )
                    else:
                        for dep in pendientes:
                            id_dep = dep["id_transaccion"]
                            usuario_solicitante = dep["usuario"]
                            dolares_solicitados = dep["dolares"]
                            sobolevs_a_entregar = dep["sobolevs"]

                            with st.expander(
                                f"⏳ Solicitud de {usuario_solicitante} - ${dolares_solicitados} USD"
                            ):
                                st.write(f"**Fecha:** {dep['fecha']}")
                                st.write(
                                    f"**Acreditar:** {sobolevs_a_entregar} Sobolevs"
                                )

                                col_aprobar, col_rechazar = st.columns(2)

                                with col_aprobar:
                                    if st.button(
                                        f"✅ Aprobar y Cargar", key=f"aprobar_{id_dep}"
                                    ):
                                        for u in usuarios:
                                            if u["nombre"] == usuario_solicitante:
                                                u["monedas"] += sobolevs_a_entregar
                                                u["dolares_depositados"] += (
                                                    dolares_solicitados
                                                )
                                            if u["nombre"] == "Banco":
                                                u["dolares_depositados"] += (
                                                    dolares_solicitados
                                                )

                                        guardar_datos("usuarios.json", usuarios)

                                        registro = f"[{dep['fecha']}] APROBADO por Admin | Usuario: {usuario_solicitante} | Depósito: ${dolares_solicitados} | Sobolevs: {sobolevs_a_entregar}\n"
                                        with open(
                                            "historial_depositos.txt",
                                            "a",
                                            encoding="utf-8",
                                        ) as f_log:
                                            f_log.write(registro)

                                        dep["estado"] = "aprobado"
                                        guardar_datos(
                                            "depositos_pendientes.json",
                                            depositos_pendientes,
                                        )

                                        st.success(
                                            f"¡Dinero cargado a la cuenta de {usuario_solicitante}!"
                                        )
                                        st.rerun()

                                with col_rechazar:
                                    if st.button(
                                        f"❌ Rechazar", key=f"rechazar_{id_dep}"
                                    ):
                                        dep["estado"] = "rechazado"
                                        guardar_datos(
                                            "depositos_pendientes.json",
                                            depositos_pendientes,
                                        )
                                        st.error("Solicitud rechazada y anulada.")
                                        st.rerun()

                    # ==========================================
                    # REPARTICIÓN DE PREMIOS
                    # ==========================================
                    st.markdown("---")
                    st.subheader("🏦 Repartición de Premios")
                    st.write(
                        "Presiona este botón después de poner un partido en estado 'finalizado' para transferir las ganancias automáticamente."
                    )

                    if st.button("Calcular y Pagar Premios Pendientes"):
                        cambios_realizados = False

                        for p in partidos:
                            if p.get("estado") == "finalizado":
                                g1_real = p.get("goles_1_real")
                                g2_real = p.get("goles_2_real")
                                p1_real = p.get("penales_1_real")
                                p2_real = p.get("penales_2_real")

                                if g1_real is not None and g2_real is not None:
                                    for pron in pronosticos:
                                        if pron["id_partido"] == p[
                                            "id_partido"
                                        ] and not pron.get("pagado", False):
                                            g1_pron = pron["goles_1_pronostico"]
                                            g2_pron = pron["goles_2_pronostico"]
                                            p1_pron = pron.get("penales_1_pronostico")
                                            p2_pron = pron.get("penales_2_pronostico")
                                            monto = pron.get("monto_apostado", 0)

                                            multiplicador = 0

                                            # 0. ACERTO DE PENALES EXACTOS (x15)
                                            if (
                                                (g1_real == g2_real)
                                                and (g1_pron == g2_pron)
                                                and p1_real is not None
                                                and p2_real is not None
                                            ):
                                                if (p1_real == p1_pron) and (
                                                    p2_real == p2_pron
                                                ):
                                                    multiplicador = 15
                                                else:
                                                    multiplicador = 10  # Falló penales exactos pero acertó el empate de los 120 mins

                                            # 1. ACERTO EXACTO NORMAL (x10)
                                            elif (
                                                g1_real == g1_pron
                                                and g2_real == g2_pron
                                            ) and multiplicador == 0:
                                                multiplicador = 10

                                            # 2. ACERTO DE DIFERENCIA EXACTA (x6)
                                            elif (g1_real - g2_real) == (
                                                g1_pron - g2_pron
                                            ) and multiplicador == 0:
                                                multiplicador = 6

                                            # 3. ACERTO DE GANADOR / EMPATE NO EXACTO (x4)
                                            elif (
                                                (
                                                    g1_real > g2_real
                                                    and g1_pron > g2_pron
                                                )
                                                or (
                                                    g1_real < g2_real
                                                    and g1_pron < g2_pron
                                                )
                                                or (
                                                    g1_real == g2_real
                                                    and g1_pron == g2_pron
                                                )
                                            ) and multiplicador == 0:
                                                multiplicador = 4

                                            ganancia = monto * multiplicador

                                            pron["puntos_ganados"] = ganancia
                                            pron["pagado"] = True

                                            for u in usuarios:
                                                if (
                                                    u["nombre"] == pron["usuario"]
                                                    and ganancia > 0
                                                ):
                                                    u["monedas"] += ganancia

                                            cambios_realizados = True

                        if cambios_realizados:
                            guardar_datos("usuarios.json", usuarios)
                            guardar_datos("pronosticos.json", pronosticos)
                            st.success(
                                "✅ ¡Premios pagados! El Banco Central ha impreso los Sobolevs necesarios para los ganadores."
                            )
                            st.rerun()
                        else:
                            st.info(
                                "No hay premios nuevos pendientes por repartir en este momento."
                            )

                    # ==========================================
                    # RESPALDOS Y DESCARGAS DEL SISTEMA
                    # ==========================================
                    st.markdown("---")
                    st.subheader("💾 Respaldos de la Base de Datos")
                    st.write(
                        "Descarga los archivos al final de la jornada y súbelos a tu repositorio local de GitHub para no perder el historial."
                    )

                    col_archivos1, col_archivos2 = st.columns(2)

                    with col_archivos1:
                        if os.path.exists("usuarios.json"):
                            with open("usuarios.json", "r", encoding="utf-8") as f_usr:
                                st.download_button(
                                    "⬇️ Descargar usuarios.json",
                                    f_usr.read(),
                                    "usuarios.json",
                                    "application/json",
                                    use_container_width=True,
                                )

                        if os.path.exists("pronosticos.json"):
                            with open(
                                "pronosticos.json", "r", encoding="utf-8"
                            ) as f_pron:
                                st.download_button(
                                    "⬇️ Descargar pronosticos.json",
                                    f_pron.read(),
                                    "pronosticos.json",
                                    "application/json",
                                    use_container_width=True,
                                )

                        if os.path.exists("depositos_pendientes.json"):
                            with open(
                                "depositos_pendientes.json", "r", encoding="utf-8"
                            ) as f_dep:
                                st.download_button(
                                    "⬇️ Descargar depositos_pendientes.json",
                                    f_dep.read(),
                                    "depositos_pendientes.json",
                                    "application/json",
                                    use_container_width=True,
                                )

                    with col_archivos2:
                        if os.path.exists("historial_apuestas.txt"):
                            with open(
                                "historial_apuestas.txt", "r", encoding="utf-8"
                            ) as f_hist_ap:
                                st.download_button(
                                    "⬇️ Auditoría de Apuestas (.txt)",
                                    f_hist_ap.read(),
                                    "historial_apuestas.txt",
                                    "text/plain",
                                    use_container_width=True,
                                )

                        if os.path.exists("historial_depositos.txt"):
                            with open(
                                "historial_depositos.txt", "r", encoding="utf-8"
                            ) as f_hist_dep:
                                st.download_button(
                                    "⬇️ Auditoría de Depósitos (.txt)",
                                    f_hist_dep.read(),
                                    "historial_depositos.txt",
                                    "text/plain",
                                    use_container_width=True,
                                )
        elif pin_ingresado != "":
            st.error("❌ PIN incorrecto. No tienes autorización para ingresar.")
else:
    st.error("No hay usuarios registrados en la base de datos JSON.")
