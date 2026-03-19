import streamlit as st
import pandas as pd
import requests
import base64

# --- 1. CONFIGURACIÓN ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxCgn0_fIMpHjjSJyoYeFg8cdLddzuGOov7diwg_cUyNEz5muAwFgFQRC6umV63alH2/exec"

PALABRAS_ESTIMULO = [
    "Las mujeres son:", "Los hombres son:", "las mujeres son mejores para:", 
    "Los hombres son mejores para:", "La mujer para la religión es:", 
    "El hombre para la religión es:", "La violencia es:", 
    "La violencia se manifiesta en:"
]

st.set_page_config(page_title="Estudio de Redes Semánticas", layout="centered")

# --- ESTILOS CSS ---
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
    
    /* Adaptación específica para Celulares */
    @media (max-width: 768px) {
        h2 {
            font-size: 1.5rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
        .stButton>button {
            width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- MODO REVISIÓN DE DISEÑO (OCULTO) ---
modo_prueba = False # Por defecto siempre está apagado

# La "llave secreta" es que aparezca la palabra 'admin' en el link
if "admin" in st.query_params:
    with st.sidebar:
        modo_prueba = st.checkbox("🛠️ Modo Prueba (Revisar diseño)", value=False)
        if modo_prueba:
            st.warning("⚠️ Modo prueba ON: Puedes avanzar sin llenar campos y NO se enviarán datos al Excel.")
            
            # FLECHAS DE NAVEGACIÓN
            st.markdown("---")
            st.markdown("### 🧭 Navegación Rápida")
            
            col_izq, col_der = st.columns(2)
            
            if col_izq.button("⬅️ Atrás"):
                if st.session_state.paso == "instrucciones":
                    st.session_state.paso = "consentimiento"
                elif st.session_state.paso == 1 and st.session_state.indice_palabra == 0:
                    st.session_state.paso = "instrucciones"
                elif st.session_state.paso == 2:
                    st.session_state.paso = 1
                elif st.session_state.paso == 1 and st.session_state.indice_palabra > 0:
                    st.session_state.indice_palabra -= 1
                    st.session_state.paso = 2
                elif st.session_state.paso == "grupo_focal":
                    st.session_state.indice_palabra = len(PALABRAS_ESTIMULO) - 1
                    st.session_state.paso = 2
                elif st.session_state.paso == "final" or st.session_state.finalizado:
                    st.session_state.paso = "grupo_focal"
                    st.session_state.finalizado = False
                st.rerun()

            if col_der.button("Avanzar ➡️"):
                if st.session_state.paso == "consentimiento":
                    st.session_state.paso = "instrucciones"
                elif st.session_state.paso == "instrucciones":
                    st.session_state.paso = 1
                elif st.session_state.paso == 1:
                    # Rellenamos palabras fantasma para que la siguiente pantalla no marque error
                    st.session_state.temp_words = [f"Palabra_{i}" for i in range(1, 11)]
                    st.session_state.paso = 2
                elif st.session_state.paso == 2:
                    if st.session_state.indice_palabra + 1 < len(PALABRAS_ESTIMULO):
                        st.session_state.indice_palabra += 1
                        st.session_state.paso = 1
                    else:
                        st.session_state.paso = "grupo_focal"
                elif st.session_state.paso == "grupo_focal":
                    st.session_state.paso = "final"
                    st.session_state.finalizado = True
                st.rerun()

# --- 2. LÓGICA DE ESTADOS ---
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
    st.session_state.bloqueo_boton = False # Inicia desbloqueado

# --- 3. INTERFAZ ---
st.header("Construcción Social de Roles, Estereotipos de Género y Normalización de la Violencia en Jóvenes Estudiantes: Redes Semánticas")

# --- PANTALLA 0: CONSENTIMIENTO INFORMADO ---
if st.session_state.paso == "consentimiento":
    st.subheader("📄 Consentimiento Informado")
    
    st.info("""
    **Título de la investigación:** Construcción Social de Roles, Estereotipos de Género y Normalización de la Violencia en Jóvenes Estudiantes 
    
    **Duración estimada y procedimiento:** La aplicación de las redes semánticas será desarrollada en un tiempo estimado de 1 hora, dando tiempo suficiente al sujeto para responder de la manera más sincera posible, teniendo en cuenta que los datos obtenidos serán confidenciales y serán empleados para investigación.
    
    **Instituto a realizar la investigación:** Facultad de Ciencias de la Conducta UAEMEX.
    
    **Investigadoras:** * Karen Guadalupe Aguirre Rojas (Investigadora)
    * Ana Karen Gómez Arriaga (Investigadora)
    * Jaqueline Mota Palma (Asesora de tesis)

    **Objetivo de la Investigación:** Identificar cómo se da la construcción social de los roles y estereotipos de género y la normalización de la violencia en estudiantes de último grado de preparatoria y último semestre de licenciatura de una universidad pública del Estado de México. 
    
    **Beneficios de la Investigación:** Ampliar el conocimiento que se tiene acerca de temas de género, para así promover una visión de la vida libre de la heteronormatividad.
    
    **Aclaraciones:**
    1. Su decisión de participar en el estudio es voluntaria.
    2. En caso de decidir no participar en esta investigación, no habrá ninguna consecuencia desfavorable para usted, su familia o su institución.
    3. Si decide participar en la investigación puede retirarse en el momento que así lo disponga.
    4. La información obtenida en este estudio mantendrá estricta confidencialidad acerca de los participantes.
    5. Los resultados de la investigación podrán difundirse en tesis, artículos científicos o presentaciones académicas, garantizando siempre el anonimato de los y las participantes.
    """)
    
    st.write("---")
    st.write("### Firma de Consentimiento")
    st.write("Yo, acepto de manera voluntaria que se me incluya como sujeto de estudio en este proyecto de investigación, luego de haber conocido y comprendido la finalidad sobre dicho proyecto, y de estar seguro(a) de que mis datos serán utilizados de manera anónima y segura.")

    col1, col2 = st.columns(2)
    opciones_relig = ["- Selecciona -", "Católica", "Cristiana", "Evangélica", "Testigos de Jehová", "Pentecostal", "Ateísta", "Otra"]

    with col1:
        iniciales = st.text_input("Mis iniciales (Ej: A.M.A.G)").upper()
        edad = st.number_input("Edad", min_value=15, max_value=40, step=1, value=18)
        sexo = st.selectbox("Sexo", ["- Selecciona -", "Mujer", "Hombre", "Prefiero no decirlo"])
        estado_civil = st.selectbox("Estado Civil", ["- Selecciona -", "Soltero/a", "Casado/a", "Vivo con mi pareja en unión libre", "Divorciado/a", "Viudo/a"])
        
        st.write("**Creencias Religiosas:**")
        rel_crianza = st.selectbox("Religión en la que me criaron", opciones_relig)
        rel_crianza_otra = st.text_input("Especifica crianza:", key="c_otra") if rel_crianza == "Otra" else ""
        
        rel_actual = st.selectbox("Religión actual", opciones_relig)
        rel_actual_otra = st.text_input("Especifica actual:", key="a_otra") if rel_actual == "Otra" else ""

        influencia_rel = st.selectbox(
            "¿En qué medida tu religión o espiritualidad guía tus decisiones y visión del mundo?",
            ["- Selecciona -", "No profeso ninguna religión", "No influye en mis decisiones", "Influye solo en momentos específicos", "Es un marco de referencia importante", "Guía la mayoría de mis acciones", "Mi visión del mundo está regida por mi religión"]
        )
        correo = st.text_input("Correo electrónico (Opcional)")
        
    with col2:
        institucion = st.selectbox("Institución", ["- Selecciona una opción -", "1. Facultad de Ciencias de la Conducta (Psicología)", "2. Preparatoria UAEMex"])
        
        semestre = ""
        detalle_prepa = ""
        archivo_padres = None
        
        if institucion == "1. Facultad de Ciencias de la Conducta (Psicología)":
            semestre = st.selectbox("¿Qué semestre cursas?", ["- Selecciona tu semestre -", "1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "Otro"])
            if semestre == "Otro":
                semestre = st.text_input("Especifica tu situación:")
                
        elif institucion == "2. Preparatoria UAEMex":
            detalle_prepa = st.selectbox("Selecciona tu plantel", ["- Selecciona tu plantel -", "Plantel 1: Lic. Adolfo López Mateos", "Plantel 2: Nezahualcóyotl", "Plantel 3: Cuauhtémoc", "Plantel 4: Ignacio Ramírez Calzada", "Plantel 5: Dr. Ángel Ma. Garibay Kintana"])
        
        if "Preparatoria" in institucion:
            st.warning("⚠️ Al ser estudiante de preparatoria, es obligatorio el consentimiento de tus padres.")
            url_drive = "https://drive.google.com/file/d/1gg09wf1bHp2hbMZza4J_GqfEmIqvJ0fK/view?usp=sharing" 
            st.link_button("📥 Descargar Consentimiento para Padres", url_drive)
            
            archivo_padres = st.file_uploader("Sube el documento firmado (Foto o PDF)", type=["pdf", "jpg", "jpeg", "png"])

    acepto = st.checkbox("Confirmo los datos y acepto participar voluntariamente.")
    
    if st.button("Continuar", disabled=st.session_state.bloqueo_boton):
        st.session_state.bloqueo_boton = True
        rel_otra_ok = (rel_crianza != "Otra" or rel_crianza_otra) and (rel_actual != "Otra" or rel_actual_otra)
        inst_ok = (institucion == "1. Facultad de Ciencias de la Conducta (Psicología)" and semestre != "- Selecciona tu semestre -" and semestre != "") or \
                  (institucion == "2. Preparatoria UAEMex" and detalle_prepa != "- Selecciona tu plantel -") or \
                  (institucion == "3. Preparatoria" and detalle_prepa != "")

        if (acepto and iniciales and edad and sexo != "- Selecciona -" and estado_civil != "- Selecciona -" and 
            rel_crianza != "- Selecciona -" and rel_actual != "- Selecciona -" and influencia_rel != "- Selecciona -" and 
            rel_otra_ok and inst_ok) or modo_prueba:
            
            st.session_state.iniciales = iniciales
            st.session_state.edad = edad
            st.session_state.sexo = sexo
            st.session_state.estado_civil = estado_civil
            st.session_state.rel_crianza = rel_crianza_otra if rel_crianza == "Otra" else rel_crianza
            st.session_state.rel_actual = rel_actual_otra if rel_actual == "Otra" else rel_actual
            st.session_state.influencia_rel = influencia_rel
            st.session_state.correo = correo
            st.session_state.institucion = institucion
            st.session_state.detalle_instit = semestre if institucion == "1. Facultad de Ciencias de la Conducta (Psicología)" else detalle_prepa
            st.session_state.grupo_asignado = "Licenciatura" if "Facultad" in institucion else "Preparatoria"
            if archivo_padres: st.session_state.archivo_b64 = base64.b64encode(archivo_padres.getvalue()).decode()
            st.session_state.paso = "instrucciones"
            st.session_state.bloqueo_boton = False
            st.rerun()
        else:
            st.error("⚠️ Por favor completa todos los campos obligatorios.")
            st.session_state.bloqueo_boton = False
            
# --- PANTALLA 1: BIENVENIDA ---
elif st.session_state.paso == "instrucciones":
    st.subheader("¡Bienvenido(a)!")
    st.markdown(f"**Grupo:** {st.session_state.grupo_asignado}")
    
    st.write("""
    Gracias por participar. Las instrucciones son:
    1. Lee la frase que aparecerá en pantalla.
    2. Escribe las primeras 10 palabras que se te ocurran (de ser muy necesario puedes usar frases cortas).
    3. Ordénalas por importancia (la #1 es la más importante para ti).
    """)
    if st.button("Comenzar Estudio"):
        st.session_state.paso = 1
        st.rerun()

# --- PANTALLA X: GRUPO FOCAL ---
elif st.session_state.paso == "grupo_focal":
    st.subheader("🗣️ Invitación a Grupo Focal")
    st.write("Para enriquecer aún más esta investigación, estaremos realizando un grupo focal (una charla grupal) sobre este tema.")
    st.write("**¿Te gustaría participar?**")
    
    participa = st.radio("Selecciona una opción:", ["-", "Sí, me gustaría participar", "No, gracias"])
    
    if participa == "Sí, me gustaría participar":
        st.info("¡Excelente! Por favor déjanos tus datos para contactarte:")
        whatsapp = st.text_input("Número de WhatsApp")
        correo_focal = st.text_input("Correo que revises constantemente")
        
        modalidad = st.multiselect("¿En qué modalidad prefieres participar?", ["En línea (Teams)", "Presencial"])
