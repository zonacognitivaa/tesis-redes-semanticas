import streamlit as st
import pandas as pd
import requests
import base64

# --- 1. CONFIGURACIÓN ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyclCu2yhaLeb-uJkhzbXKEnXyB2Kx8f-je3GCmmL65woi1_ejKgriNVKUbkPhZTgrP/exec"

PALABRAS_ESTIMULO = [
    "Las mujeres son:", "Los hombres son:", "las mujeres son mejor para:", 
    "Los hombres son mejor para:", "La mujer para la religión es:", 
    "El hombre para la religión es:", "La violencia es:", 
    "La violencia se manifiesta en:"
]

st.set_page_config(page_title="Estudio de Redes Semánticas", layout="centered")

# --- ESTILOS ---
st.markdown("""
<style>
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="textarea"] > div:focus-within {
        border-color: #4A90E2 !important;
        box-shadow: inset 0 0 0 1px #4A90E2 !important;
    }
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
    st.session_state.rel_crianza = ""
    st.session_state.rel_actual = ""
    st.session_state.influencia_rel = "" 
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
    st.warning("📱 **RECOMENDACIÓN: Realiza el llenado desde una computadora o usa el celular horizontal.**")
    st.info("**Investigadoras:** Karen Guadalupe Aguirre Rojas, Ana Karen Gómez Arriaga. **Asesora:** Jaqueline Mota Palma.")
    
    st.write("---")
    st.write("### Firma de Consentimiento")
    
    col1, col2 = st.columns(2)
    opciones_relig = ["- Selecciona -", "Católica", "Cristiana", "Evangélica", "Testigos de Jehová", "Pentecostal", "Ateísta", "Otra"]

    with col1:
        iniciales = st.text_input("Mis iniciales (Ej: A.M.A.G)").upper()
        edad = st.number_input("Edad", min_value=15, max_value=40, step=1, value=18)
        sexo = st.selectbox("Sexo", ["- Selecciona -", "Mujer", "Hombre", "Prefiero no decirlo"])
        estado_civil = st.selectbox("Estado Civil", ["- Selecciona -", "Soltero/a", "Casado/a", "Vivo con mi pareja en unión libre", "Viudo/a"])
        
        st.write("**Creencias Religiosas:**")
        rel_crianza = st.selectbox("Religión en la que me criaron", opciones_relig)
        rel_crianza_otra = st.text_input("Especifica religión de crianza:", placeholder="Escribe aquí...") if rel_crianza == "Otra" else ""
        
        rel_actual = st.selectbox("Religión actual", opciones_relig)
        rel_actual_otra = st.text_input("Especifica religión actual:", placeholder="Escribe aquí...") if rel_actual == "Otra" else ""

        # --- PREGUNTA DE INFLUENCIA CON LA NUEVA OPCIÓN ---
        influencia_rel = st.selectbox(
            "¿En qué medida tu religión o espiritualidad guía tus decisiones y visión del mundo?",
            ["- Selecciona -",
             "No profeso ninguna religión",
             "No influye en mis decisiones ni en mi forma de ver el mundo.",
             "Influye solo en momentos específicos o festividades.",
             "Es un marco de referencia importante, pero no el único.",
             "Guía la gran mayoría de mis acciones y pensamientos.",
             "Mi visión del mundo está totalmente regida por los principios de mi religión."]
        )
        
        correo = st.text_input("Correo electrónico (Opcional)")
        
    with col2:
        institucion = st.selectbox("Institución", ["- Selecciona una opción -", "1. Facultad de Ciencias de la Conducta (Psicología)", "2. Preparatoria UAEMex", "3. Preparatoria"])
        semestre = ""
        detalle_prepa = ""
        archivo_padres = None
        
        if institucion == "1. Facultad de Ciencias de la Conducta (Psicología)":
            semestre = st.selectbox("¿Qué semestre cursas?", ["- Selecciona tu semestre -", "1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "Otro"])
        elif "Preparatoria" in institucion:
            if "UAEMex" in institucion:
                detalle_prepa = st.selectbox("Plantel", ["- Selecciona -", "Plantel 1", "Plantel 2", "Plantel 3", "Plantel 4", "Plantel 5"])
            else:
                detalle_prepa = st.text_input("Nombre de tu prepa:")
            st.warning("⚠️ Requiere consentimiento de padres.")
            archivo_padres = st.file_uploader("Sube el documento", type=["pdf", "jpg", "png"])

    acepto = st.checkbox("Confirmo los datos y acepto participar voluntariamente.")
    
    if st.button("Continuar"):
        rel_otra_ok = (rel_crianza != "Otra" or rel_crianza_otra) and (rel_actual != "Otra" or rel_actual_otra)
        datos_completos = (iniciales and edad and sexo != "- Selecciona -" and estado_civil != "- Selecciona -" and 
                          rel_crianza != "- Selecciona -" and rel_actual != "- Selecciona -" and 
                          influencia_rel != "- Selecciona -" and rel_otra_ok and
                          institucion != "- Selecciona una opción -")
        
        if (acepto and datos_completos) or modo_prueba:
            st.session_state.iniciales = iniciales
            st.session_state.edad = edad
            st.session_state.sexo = sexo
            st.session_state.estado_civil = estado_civil
            st.session_state.rel_crianza = rel_crianza_otra if rel_crianza == "Otra" else rel_crianza
            st.session_state.rel_actual = rel_actual_otra if rel_actual == "Otra" else rel_actual
            st.session_state.influencia_rel = influencia_rel 
            st.session_state.correo = correo
            st.session_state.institucion = institucion
            st.session_state.detalle_instit = semestre if semestre else detalle_prepa
            st.session_state.grupo_asignado = "Licenciatura" if "Facultad" in institucion else "Preparatoria"
            if archivo_padres: st.session_state.archivo_b64 = base64.b64encode(archivo_padres.getvalue()).decode()
            st.session_state.paso = "instrucciones"; st.rerun()
        else:
            st.error("⚠️ Por favor completa todos los campos obligatorios.")

# --- PANTALLAS DE REDES SEMÁNTICAS ---
elif st.session_state.paso == "instrucciones":
    st.subheader("¡Bienvenido(a)!"); st.write("Lee la frase, escribe 10 palabras y ordénalas.")
    if st.button("Comenzar"): st.session_state.paso = 1; st.rerun()

elif st.session_state.paso == "grupo_focal":
    st.subheader("🗣️ Grupo Focal"); st.write("¿Te gustaría participar?")
    participa = st.radio("Opción:", ["-", "Sí", "No"])
    if participa == "Sí":
        whatsapp = st.text_input("WhatsApp")
        correo_focal = st.text_input("Correo")
        modalidad = st.multiselect("Modalidad", ["En línea", "Presencial"])
        dias = st.multiselect("Días", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        horarios = st.multiselect("Horario", ["Mañana", "Tarde", "Noche"])
        detalle_h = st.text_area("Detalle de horarios")
        if st.button("Finalizar"):
            payload_focal = {"tipo": "focal", "nombre": st.session_state.iniciales, "whatsapp": whatsapp, "correo_focal": correo_focal, "modalidad": ", ".join(modalidad), "dias": ", ".join(dias), "horarios": ", ".join(horarios), "detalle_horarios": detalle_h, "archivo_b64": st.session_state.archivo_b64, "iniciales": st.session_state.iniciales}
            if not modo_prueba: requests.post(SCRIPT_URL, json=payload_focal)
            st.session_state.paso = "final"; st.session_state.finalizado = True; st.rerun()
    else:
        if st.button("Finalizar"): st.session_state.paso = "final"; st.rerun()

elif st.session_state.paso == "final":
    st.balloons(); st.success("¡Muchas gracias!"); st.write("Has completado el estudio.")

else:
    frase_actual = PALABRAS_ESTIMULO[st.session_state.indice_palabra]
    st.progress((st.session_state.indice_palabra) / len(PALABRAS_ESTIMULO))
    if st.session_state.paso == 1:
        st.write(f"### Escribe 10 palabras para: \n ## {frase_actual}")
        w = [st.text_input(f"{i+1}°", key=f"w{i}_{st.session_state.indice_palabra}") for i in range(10)]
        if st.button("Siguiente"):
            if all(w) or modo_prueba:
                st.session_state.temp_words = w; st.session_state.paso = 2; st.rerun()
            else: st.error("Escribe 10 palabras.")

    elif st.session_state.paso == 2:
        st.markdown(f"### Ordena para: \"{frase_actual}\"")
        col_izq, col_der = st.columns(2)
        with col_izq: ranking = st.multiselect("Elige en orden:", st.session_state.temp_words, max_selections=10)
        with col_der: 
            if ranking:
                lista = "".join([f"<span style='color:#4A90E2'>**{i+1}.**</span> {p}  \n" for i, p in enumerate(ranking)])
                st.markdown(lista, unsafe_allow_html=True)
        
        if st.button("Guardar"):
            if len(ranking) == 10 or modo_prueba:
                r, o = (ranking, st.session_state.temp_words)
                if not modo_prueba:
                    payload = {
                        "tipo": "redes", "iniciales": st.session_state.iniciales, "edad": st.session_state.edad,
                        "sexo": st.session_state.sexo, "estado_civil": st.session_state.estado_civil,
                        "rel_crianza": st.session_state.rel_crianza, "rel_actual": st.session_state.rel_actual,
                        "influencia": st.session_state.influencia_rel, 
                        "correo": st.session_state.correo, "institucion": st.session_state.institucion,
                        "detalle": st.session_state.detalle_instit, "grupo": st.session_state.grupo_asignado,
                        "frase": frase_actual, 
                        "r1": r[0], "r2": r[1], "r3": r[2], "r4": r[3], "r5": r[4], "r6": r[5], "r7": r[6], "r8": r[7], "r9": r[8], "r10": r[9],
                        "o1": o[0], "o2": o[1], "o3": o[2], "o4": o[3], "o5": o[4], "o6": o[5], "o7": o[6], "o8": o[7], "o9": o[8], "o10": o[9]
                    }
                    requests.post(SCRIPT_URL, json=payload)
                if st.session_state.indice_palabra + 1 < len(PALABRAS_ESTIMULO):
                    st.session_state.indice_palabra += 1; st.session_state.paso = 1
                else: st.session_state.paso = "grupo_focal"
                st.rerun()


