import streamlit as st
import pandas as pd
import requests
import base64

# --- 1. CONFIGURACIÓN ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycby4COJaFUYkPtVKGp_cVu4TbOJhNZKX2n4Qw1VqBsZJVd31tzcyhK3a4ZjkloxPJLmh/exec"

PALABRAS_ESTIMULO = [
    "Las mujeres son:", "Los hombres son:", "las mujeres son mejor para:", 
    "Los hombres son mejor para:", "La mujer para la religión es:", 
    "El hombre para la religión es:", "La violencia es:", 
    "La violencia se manifiesta en:"
]

st.set_page_config(page_title="Estudio de Redes Semánticas", layout="centered")

# --- NUEVO: ESTILOS Y OCULTAR SELECT ALL ---
st.markdown("""
<style>
    /* Forzar el color azul en las cajas de texto y selects al hacer clic */
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #4A90E2 !important;
        box-shadow: inset 0 0 0 1px #4A90E2 !important;
    }
    
    /* Ocultar el botón de "Select all" del menú de palabras */
    div[data-baseweb="popover"] ul[role="listbox"] li:first-child:has(svg),
    div[data-baseweb="popover"] ul[aria-multiselectable="true"] li:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

modo_prueba = False

# --- 2. LÓGICA DE GRUPOS Y ESTADOS ---
if 'indice_palabra' not in st.session_state:
    st.session_state.indice_palabra = 0
    st.session_state.paso = "consentimiento"
    st.session_state.finalizado = False
    
    st.session_state.iniciales = ""
    st.session_state.edad = ""
    st.session_state.sexo = ""
    st.session_state.estado_civil = ""
    st.session_state.rel_crianza = ""  # Nuevo
    st.session_state.rel_actual = ""   # Nuevo
    st.session_state.correo = ""
    st.session_state.institucion = ""
    st.session_state.detalle_instit = ""
    st.session_state.grupo_asignado = "" 
    
    st.session_state.archivo_b64 = ""

# --- 3. INTERFAZ ---
st.title("Construcción Social de Roles, Estereotipos de Género y Normalización de la Violencia en Jóvenes Estudiantes: Redes Semánticas")

# --- PANTALLA 0: CONSENTIMIENTO INFORMADO ---
if st.session_state.paso == "consentimiento":
    st.subheader("📄 Consentimiento Informado")
    
    st.warning("📱 **RECOMENDACIÓN: Realiza el llenado desde una computadora para mayor comodidad. Utiliza el celular de manera horizontal.**")

    st.info("""
    **Título de la investigación:** Construcción Social de Roles, Estereotipos de Género y Normalización de la Violencia en Jóvenes Estudiantes 
    **Instituto:** Facultad de Ciencias de la Conducta UAEMEX.
    **Investigadoras:** Karen Guadalupe Aguirre Rojas, Ana Karen Gómez Arriaga. Asesora: Jaqueline Mota Palma.
    """)
    
    st.write("---")
    st.write("### Firma de Consentimiento")
    st.write("Yo, acepto de manera voluntaria que se me incluya como sujeto de estudio...")
    
    col1, col2 = st.columns(2)
    
    opciones_relig = ["- Selecciona -", "Católica", "Cristiana", "Evangélica", "Testigos de Jehová", "Pentecostal", "Ateísta", "Otra"]

    with col1:
        iniciales = st.text_input("Mis iniciales (Ej: A.M.A.G)").upper()
        edad = st.number_input("Edad", min_value=15, max_value=40, step=1, value=18)
        sexo = st.selectbox("Sexo", ["- Selecciona -", "Mujer", "Hombre", "Prefiero no decirlo"])
        estado_civil = st.selectbox("Estado Civil", ["- Selecciona -", "Soltero/a", "Casado/a", "Vivo con mi pareja en unión libre", "Viudo/a"])
        
        # --- NUEVA SECCIÓN DE RELIGIÓN ---
        st.write("**Creencias Religiosas:**")
        rel_crianza = st.selectbox("Religión en la que me criaron", opciones_relig)
        if rel_crianza == "Otra":
            rel_crianza_otra = st.text_input("Especifica tu religión de crianza:", placeholder="Ej: Budismo, Judaismo...")
        
        rel_actual = st.selectbox("Religión de la que formo parte en la actualidad", opciones_relig)
        if rel_actual == "Otra":
            rel_actual_otra = st.text_input("Especifica tu religión actual:", placeholder="Ej: Espiritualidad libre...")
        
        correo = st.text_input("Correo electrónico (Opcional)")
        
    with col2:
        institucion = st.selectbox("Institución a la que pertenezco", ["- Selecciona una opción -", "1. Facultad de Ciencias de la Conducta (Psicología)", "2. Preparatoria UAEMex", "3. Preparatoria"])
        
        semestre = ""
        detalle_prepa = ""
        archivo_padres = None
        
        if institucion == "1. Facultad de Ciencias de la Conducta (Psicología)":
            semestre = st.selectbox("¿Qué semestre cursas?", ["- Selecciona tu semestre -", "1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "Otro"])
            if semestre == "Otro":
                semestre = st.text_input("Especifica tu situación:")
                
        elif institucion in ["2. Preparatoria UAEMex", "3. Preparatoria"]:
            if institucion == "2. Preparatoria UAEMex":
                detalle_prepa = st.selectbox("Selecciona tu plantel", ["- Selecciona tu plantel -", "Plantel 1: Lic. Adolfo López Mateos", "Plantel 2: Nezahualcóyotl", "Plantel 3: Cuauhtémoc", "Plantel 4: Ignacio Ramírez Calzada", "Plantel 5: Dr. Ángel Ma. Garibay Kintana"])
            else:
                detalle_prepa = st.text_input("Nombre de tu preparatoria:")
            
            st.warning("⚠️ Al ser estudiante de preparatoria, es obligatorio el consentimiento de tus padres.")
            url_drive = "https://drive.google.com/file/d/1gg09wf1bHp2hbMZza4J_GqfEmIqvJ0fK/view?usp=sharing" 
            st.link_button("📥 Descargar Consentimiento para Padres", url_drive)
            archivo_padres = st.file_uploader("Sube el documento firmado (Foto o PDF)", type=["pdf", "jpg", "jpeg", "png"])

    acepto = st.checkbox("Confirmo los datos y acepto participar voluntariamente.")
    
    if st.button("Continuar"):
        # Validación de religión "Otra"
        otra_crianza_ok = (rel_crianza != "Otra" or (rel_crianza == "Otra" and rel_crianza_otra))
        otra_actual_ok = (rel_actual != "Otra" or (rel_actual == "Otra" and rel_actual_otra))
        
        datos_completos = (iniciales and edad and sexo != "- Selecciona -" and estado_civil != "- Selecciona -" and 
                          rel_crianza != "- Selecciona -" and rel_actual != "- Selecciona -" and
                          otra_crianza_ok and otra_actual_ok and
                          institucion != "- Selecciona una opción -" and (detalle_prepa != "- Selecciona tu plantel -" or semestre != ""))
        
        if (acepto and datos_completos) or modo_prueba:
            st.session_state.iniciales = iniciales
            st.session_state.edad = edad
            st.session_state.sexo = sexo
            st.session_state.estado_civil = estado_civil
            st.session_state.rel_crianza = rel_crianza_otra if rel_crianza == "Otra" else rel_crianza
            st.session_state.rel_actual = rel_actual_otra if rel_actual == "Otra" else rel_actual
            st.session_state.correo = correo
            st.session_state.institucion = institucion
            st.session_state.detalle_instit = semestre if "Facultad" in institucion else detalle_prepa
            st.session_state.grupo_asignado = "Licenciatura" if "Facultad" in institucion else "Preparatoria"
            
            if archivo_padres:
                st.session_state.archivo_b64 = base64.b64encode(archivo_padres.getvalue()).decode()
            st.session_state.paso = "instrucciones"
            st.rerun()
        else:
            st.error("⚠️ Por favor completa todos los campos obligatorios y especifica si elegiste 'Otra'.")

# --- LÓGICA DE INSTRUCCIONES Y REDES (Sin cambios, solo agregando religión al payload) ---
elif st.session_state.paso == "instrucciones":
    st.subheader("¡Bienvenido(a)!")
    st.warning("📱 **RECOMENDACIÓN:** Gira el celular a **posición horizontal**.")
    st.write("1. Lee la frase. 2. Escribe 10 palabras. 3. Ordénalas por importancia.")
    if st.button("Comenzar Estudio"):
        st.session_state.paso = 1
        st.rerun()

elif st.session_state.paso == "grupo_focal":
    st.subheader("🗣️ Invitación a Grupo Focal")
    participa = st.radio("¿Te gustaría participar?", ["-", "Sí, me gustaría participar", "No, gracias"])
    if participa == "Sí, me gustaría participar":
        whatsapp = st.text_input("Número de WhatsApp")
        correo_focal = st.text_input("Correo")
        modalidad = st.multiselect("Modalidad", ["En línea (Teams)", "Presencial"])
        dias = st.multiselect("Días", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        horarios = st.multiselect("Horario", ["Mañana (9:00 - 12:00)", "Tarde (12:00 - 16:00)", "Noche (16:00 - 20:00)"])
        detalle_h = st.text_area("Detalla tus horarios (Opcional)")
        if st.button("Enviar mis datos y finalizar"):
            if (whatsapp and correo_focal and modalidad and dias and horarios) or modo_prueba:
                payload_focal = {"tipo": "focal", "nombre": st.session_state.iniciales, "whatsapp": whatsapp, "correo_focal": correo_focal, "modalidad": ", ".join(modalidad), "dias": ", ".join(dias), "horarios": ", ".join(horarios), "detalle_horarios": detalle_h, "archivo_b64": st.session_state.archivo_b64, "iniciales": st.session_state.iniciales}
                if not modo_prueba: requests.post(SCRIPT_URL, json=payload_focal)
                st.session_state.paso = "final"; st.session_state.finalizado = True; st.rerun()
    elif participa == "No, gracias":
        if st.button("Finalizar estudio"):
            st.session_state.paso = "final"; st.session_state.finalizado = True; st.rerun()

elif st.session_state.paso == "final" or st.session_state.finalizado:
    st.balloons(); st.success("¡Muchas gracias! Has completado el estudio."); st.write("Damos gracias por contribuir a nuestra tesis.")

else:
    frase_actual = PALABRAS_ESTIMULO[st.session_state.indice_palabra]
    st.progress((st.session_state.indice_palabra) / len(PALABRAS_ESTIMULO))
    if st.session_state.paso == 1:
        st.write("### Escribe las primeras diez palabras...")
        st.markdown(f"<h2 style='text-align: center; color: #4A90E2;'>{frase_actual}</h2>", unsafe_allow_html=True)
        w = [st.text_input(f"{i+1}° palabra", key=f"w{i}_{st.session_state.indice_palabra}") for i in range(10)]
        if st.button("Siguiente: Ordenar importancia"):
            if (all(w) and len(set(w)) == 10) or modo_prueba:
                st.session_state.temp_words = w if all(w) else [f"Prueba {i+1}" for i in range(10)]
                st.session_state.paso = 2; st.rerun()
            else: st.error("Por favor escribe 10 palabras diferentes.")

    elif st.session_state.paso == 2:
        st.write("Selecciona tus palabras en orden de importancia:")
        st.markdown(f"<h3 style='text-align: center; color: #4A90E2;'>\"{frase_actual}\"</h3>", unsafe_allow_html=True)
        col_izq, col_der = st.columns(2)
        with col_izq:
            ranking = st.multiselect("Haz clic para elegir:", st.session_state.temp_words, max_selections=10)
        with col_der:
            if ranking:
                st.markdown("### 📌 Tu orden actual:")
                lista_compacta = "".join([f"<span style='color:#4A90E2'>**{i+1}.**</span> {p}  \n" for i, p in enumerate(ranking)])
                st.markdown(lista_compacta, unsafe_allow_html=True)
        
        if st.button("Guardar y continuar"):
            if len(ranking) == 10 or modo_prueba:
                r = ranking if len(ranking) == 10 else st.session_state.temp_words
                orig = st.session_state.temp_words
                if not modo_prueba:
                    payload = {
                        "tipo": "redes", "iniciales": st.session_state.iniciales, "edad": st.session_state.edad,
                        "sexo": st.session_state.sexo, "estado_civil": st.session_state.estado_civil,
                        "rel_crianza": st.session_state.rel_crianza, "rel_actual": st.session_state.rel_actual, # DATOS NUEVOS
                        "correo": st.session_state.correo, "institucion": st.session_state.institucion,
                        "detalle": st.session_state.detalle_instit, "grupo": st.session_state.grupo_asignado,
                        "frase": frase_actual, 
                        "r1": r[0], "r2": r[1], "r3": r[2], "r4": r[3], "r5": r[4], "r6": r[5], "r7": r[6], "r8": r[7], "r9": r[8], "r10": r[9],
                        "o1": orig[0], "o2": orig[1], "o3": orig[2], "o4": orig[3], "o5": orig[4], "o6": orig[5], "o7": orig[6], "o8": orig[7], "o9": orig[8], "o10": orig[9]
                    }
                    try: requests.post(SCRIPT_URL, json=payload)
                    except: st.error("Error al conectar con la base de datos.")
                
                if st.session_state.indice_palabra + 1 < len(PALABRAS_ESTIMULO):
                    st.session_state.indice_palabra += 1; st.session_state.paso = 1
                else: st.session_state.paso = "grupo_focal"
                st.rerun()
