import streamlit as st
import pandas as pd
import requests
import base64

# --- 1. CONFIGURACIÓN ---
# Esta URL la obtendrás al final cuando configuremos Google Apps Script
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyhSeeThn1WowGHOf4uSQzJD8zViyPBc42SMQM-ArWN5FFCzUZkKu_61NgYPKO3Inu5/exec"

PALABRAS_ESTIMULO = [
    "Las mujeres son:", "Los hombres son:", "las mujeres deben ser:", 
    "Los hombres deben ser:", "La mujer para la religión es:", 
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

# --- MODO PRUEBA PARA REVISAR DISEÑO ---
st.sidebar.markdown("### 🛠️ Herramientas de Desarrollo")
modo_prueba = st.sidebar.checkbox("Activar MODO PRUEBA (Permite avanzar sin contestar nada)", value=True)
if modo_prueba:
    st.sidebar.warning("El Modo Prueba está ACTIVADO. Los candados están apagados y no se enviarán datos al servidor.")

# --- 2. LÓGICA DE GRUPOS Y ESTADOS ---
if 'indice_palabra' not in st.session_state:
    st.session_state.indice_palabra = 0
    st.session_state.paso = "consentimiento"
    st.session_state.finalizado = False
    
    st.session_state.iniciales = ""
    st.session_state.edad = ""
    st.session_state.sexo = ""
    st.session_state.estado_civil = ""
    st.session_state.correo = ""
    st.session_state.institucion = ""
    st.session_state.detalle_instit = ""
    st.session_state.grupo_asignado = "" 
    
    st.session_state.archivo_b64 = ""
    st.session_state.archivo_nombre = ""
    st.session_state.archivo_tipo = ""

# --- 3. INTERFAZ ---
st.title("Construcción Social de Roles, Estereotipos de Género y Normalización de la Violencia en Jóvenes Estudiantes: Redes Semánticas")

# --- PANTALLA 0: CONSENTIMIENTO INFORMADO ---
if st.session_state.paso == "consentimiento":
    st.subheader("📄 Consentimiento Informado")
    
    st.warning("📱 **RECOMENDACIÓN: Realiza el llenado desde una computadora para mayor comodidad. Utiliza el celular de manera horizontal.**")

    st.info("""
    
    **Título de la investigación:** Construcción Social de Roles, Estereotipos de Género y Normalización de la Violencia en Jóvenes Estudiantes 
    
    **Duración estimada y procedimiento:** La aplicación de las redes semánticas será desarrollada en un tiempo estimado de 1 hora, dando tiempo suficiente al sujeto para responder de la manera más sincera posible, teniendo en cuenta que los datos obtenidos serán confidenciales y serán empleados para investigación.
    
    **Instituto a realizar la investigación:** Facultad de Ciencias de la Conducta UAEMEX.
    
    **Investigadoras:** 
    * Karen Guadalupe Aguirre Rojas (Investigadora)
    * Ana Karen Gómez Arriaga (Investigadora)
    * Jaqueline Mota Palma (Asesora de tesis)

    **Objetivo de la Investigación:** Identificar cómo se da la construcción social de los roles y estereotipos de género y la normalización de la violencia en estudiantes de último grado de preparatoria y último semestre de licenciatura de una universidad pública del Estado de México. 
    
    **Beneficios de la Investigación:** Ampliar el conocimiento que se tiene acerca de temas de género, para así promover una visión de la vida libre de la heteronormatividad.
    
    **Aclaraciones:**
    1. Su decisión de participar en el estudio es voluntaria.
    2. En caso de decidir no participar en esta investigación, no habrá ninguna consecuencia desfavorable para usted, su familia o su institución.
    3. Si decide participar en la investigación usted puede retirarse en el momento que así lo disponga.
    4. La información obtenida en este estudio mantendrá estricta confidencialidad acerca de los participantes.
    5. Los resultados de la investigación podrán difundirse en tesis, artículos científicos o presentaciones académicas, garantizando siempre el anonimato de los participantes.
    """)
    
    st.write("---")
    st.write("### Firma de Consentimiento")
    st.write("Yo, acepto de manera voluntaria que se me incluya como sujeto de estudio en este proyecto de investigación, luego de haber conocido y comprendido la finalidad sobre dicho proyecto, y de estar seguro(a) de que mis datos serán utilizados de manera anónima y segura.")
    
    col1, col2 = st.columns(2)
    with col1:
        iniciales = st.text_input("Mis iniciales (Ej: A.M.A.G)").upper()
        edad = st.text_input("Edad (Solo números, Ej: 18)")
        sexo = st.selectbox("Sexo", ["- Selecciona -", "Mujer", "Hombre"])
        estado_civil = st.selectbox("Estado Civil", ["- Selecciona -", "Soltero/a", "Casado/a", "Vivo con mi pareja en unión libre"])
        correo = st.text_input("Correo electrónico (Opcional)")
        
    with col2:
        institucion = st.selectbox("Institución a la que pertenezco", ["- Selecciona una opción -", "1. Facultad de Ciencias de la Conducta (Psicología)", "2. Preparatoria UAEMex", "3. Preparatoria"])
        
        semestre = ""
        detalle_prepa = ""
        archivo_padres = None
        
        if institucion == "1. Facultad de Ciencias de la Conducta (Psicología)":
            semestre = st.selectbox("¿Qué semestre cursas?", ["- Selecciona tu semestre -", "1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°", "Otro"])
            
            if semestre == "Otro":
                semestre_otro = st.text_input("Especifica tu situación (Ej: Egresado, Rezago, etc.):")
                semestre = semestre_otro
                
        elif institucion in ["2. Preparatoria UAEMex", "3. Preparatoria"]:
            if institucion == "2. Preparatoria UAEMex":
                detalle_prepa = st.selectbox("Selecciona tu plantel", [
                    "- Selecciona tu plantel -", 
                    "Plantel 1: Lic. Adolfo López Mateos", 
                    "Plantel 2: Nezahualcóyotl", 
                    "Plantel 3: Cuauhtémoc", 
                    "Plantel 4: Ignacio Ramírez Calzada", 
                    "Plantel 5: Dr. Ángel Ma. Garibay Kintana"
                ])
            else:
                detalle_prepa = st.text_input("Nombre de tu preparatoria:")
                
            st.warning("⚠️ Al ser estudiante de preparatoria, es obligatorio el consentimiento de tus padres.")
            
            url_drive = "https://drive.google.com/file/d/1gg09wf1bHp2hbMZza4J_GqfEmIqvJ0fK/view?usp=sharing" 
            st.link_button("📥 Descargar Consentimiento para Padres", url_drive)
            
            archivo_padres = st.file_uploader("Sube el documento firmado (Foto o PDF)", type=["pdf", "jpg", "jpeg", "png"])

    acepto = st.checkbox("Confirmo los datos y acepto participar voluntariamente.")
    
    if st.button("Continuar"):
        datos_completos = (iniciales and edad and sexo != "- Selecciona -" and estado_civil != "- Selecciona -" and institucion != "- Selecciona una opción -" and (detalle_prepa != "- Selecciona tu plantel -" or semestre != ""))
        
        if (acepto and datos_completos) or modo_prueba:
            st.session_state.iniciales = iniciales if iniciales else "PRUEBA"
            st.session_state.edad = edad if edad else "99"
            st.session_state.sexo = sexo
            st.session_state.estado_civil = estado_civil
            st.session_state.correo = correo
            st.session_state.institucion = institucion
            st.session_state.detalle_instit = semestre if "Facultad" in institucion else detalle_prepa
            st.session_state.grupo_asignado = "Licenciatura" if "Facultad" in institucion else "Preparatoria"
            
            if archivo_padres:
                st.session_state.archivo_b64 = base64.b64encode(archivo_padres.getvalue()).decode()
            st.session_state.paso = "instrucciones"
            st.rerun()
        else:
            st.error("⚠️ Por favor completa todos los campos obligatorios.")

# --- PANTALLA 1: BIENVENIDA ---
elif st.session_state.paso == "instrucciones":
    st.subheader("¡Bienvenido(a)!")
    st.markdown(f"**Grupo:** {st.session_state.grupo_asignado}")
    
    st.warning("📱 **RECOMENDACIÓN:** Si estás realizando este estudio desde un **celular**, por favor gíralo a **posición horizontal** para que puedas escribir y ordenar las palabras con mayor facilidad.")

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
        
        dias = st.multiselect("¿Qué días de la semana te acomodan mejor considerando el grupo focal?", 
                              ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
        
        horarios = st.multiselect("¿En qué horario preferirías?", 
                                  ["Mañana (9:00 - 12:00)", "Tarde (12:00 - 16:00)", "Noche (16:00 - 20:00)"])
        
        detalle_h = st.text_area("Detalla tus horarios con tus propias palabras (Opcional):", 
                                 placeholder="Ej: Solo puedo los martes después de las 5pm porque salgo de trabajar.")
        
        if st.button("Enviar mis datos y finalizar"):
            if (whatsapp and correo_focal and modalidad and dias and horarios) or modo_prueba:
                payload_focal = {
                    "tipo": "focal",
                    "nombre": st.session_state.iniciales,
                    "whatsapp": whatsapp,
                    "correo_focal": correo_focal,
                    "modalidad": ", ".join(modalidad),
                    "dias": ", ".join(dias),
                    "horarios": ", ".join(horarios),
                    "detalle_horarios": detalle_h,
                    "archivo_b64": st.session_state.archivo_b64,
                    "iniciales": st.session_state.iniciales  
                }
                
                if not modo_prueba:
                    try:
                        requests.post(SCRIPT_URL, json=payload_focal)
                    except:
                        pass 
                
                st.session_state.paso = "final"
                st.session_state.finalizado = True
                st.rerun()
            else:
                st.warning("Por favor completa al menos tu WhatsApp, correo, modalidad, días y horarios preferidos.")
                
    elif participa == "No, gracias":
        if st.button("Finalizar estudio"):
            st.session_state.paso = "final"
            st.session_state.finalizado = True
            st.rerun()

# --- PANTALLA FINAL ---
elif st.session_state.paso == "final" or st.session_state.finalizado:
    st.balloons()
    st.success("¡Muchas gracias! Has completado el estudio.")
    st.write("Damos gracias porque estás contribuyendo enormemente a nuestra tesis.")
    st.info("""
    **Contacto para dudas o aclaraciones:**
    Para cualquier duda, aclaración o mayor información del estudio, puedes contactar con las investigadoras a los siguientes correos:
    * **Karen Guadalupe Aguirre Rojas:** kaguirrer848@alumno.uaemex.mx
    * **Ana Karen Gómez Arriaga:** agomeza586@alumno.uaemex.mx
    """)

# --- PANTALLAS DE REDES SEMÁNTICAS (Lógica principal de las frases) ---
else:
    frase_actual = PALABRAS_ESTIMULO[st.session_state.indice_palabra]
    st.progress((st.session_state.indice_palabra) / len(PALABRAS_ESTIMULO))
    
    # PASO 1: Escribir las palabras
    if st.session_state.paso == 1:
        st.write("### Escribe las primeras diez palabras que se te vengan a la mente después de leer la siguiente frase")
        st.markdown(f"<h2 style='text-align: center; color: #4A90E2;'>{frase_actual}</h2>", unsafe_allow_html=True)
        w = [st.text_input(f"{i+1}° palabra", key=f"w{i}_{st.session_state.indice_palabra}") for i in range(10)]

        if st.button("Siguiente: Ordenar importancia"):
            if (all(w) and len(set(w)) == 10) or modo_prueba:
                st.session_state.temp_words = w if all(w) else [f"Prueba {i+1}" for i in range(10)]
                st.session_state.paso = 2
                st.rerun()
            else:
                st.error("Por favor escribe 10 palabras diferentes.")

    # PASO 2: Ordenar las palabras (Aquí es donde estaba el error)
    elif st.session_state.paso == 2:
        
        st.write("Selecciona tus palabras en orden de importancia de acuerdo con lo que tú opines:")
                
        # Mostramos la frase estímulo aquí también como pediste
        st.markdown(f"<h3 style='text-align: center; color: #4A90E2;'>\"{frase_actual}\"</h3>", unsafe_allow_html=True)
        st.info("💡 La #1 es la de mayor relación y la #10 la de menor relación.")     
        
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            ranking = st.multiselect("Haz clic para elegir en orden:", st.session_state.temp_words, max_selections=10)
            if len(ranking) < 10:
                st.info(f"Has seleccionado {len(ranking)} de 10 palabras.")
                
        with col_der:
            if ranking:
                st.markdown("### 📌 Tu orden actual:")
                # Creamos una sola cadena de texto para reducir el espacio entre líneas
                lista_compacta = ""
                for i, palabra in enumerate(ranking):
                    # El doble espacio al final de la línea es el truco para el interlineado pegadito
                    lista_compacta += f"<span style='color:#4A90E2'>**{i+1}.**</span> {palabra}  \n"

                st.markdown(lista_compacta, unsafe_allow_html=True)
        
        st.write("---") 
        
        if st.button("Guardar y continuar"):
            if len(ranking) == 10 or modo_prueba:
                r = ranking if len(ranking) == 10 else st.session_state.temp_words
                
                # --- NUEVO: Capturamos el orden en que las escribieron ---
                orig = st.session_state.temp_words
                
                if not modo_prueba:
                    payload = {
                        "tipo": "redes", "iniciales": st.session_state.iniciales, "edad": st.session_state.edad,
                        "sexo": st.session_state.sexo, "estado_civil": st.session_state.estado_civil,
                        "correo": st.session_state.correo, "institucion": st.session_state.institucion,
                        "detalle": st.session_state.detalle_instit, "grupo": st.session_state.grupo_asignado,
                        "frase": frase_actual, 
                        # ORDEN DE IMPORTANCIA (El que eligieron al final)
                        "r1": r[0], "r2": r[1], "r3": r[2], "r4": r[3], "r5": r[4],
                        "r6": r[5], "r7": r[6], "r8": r[7], "r9": r[8], "r10": r[9],
                        # ORDEN ORIGINAL (Como las escribieron al principio)
                        "o1": orig[0], "o2": orig[1], "o3": orig[2], "o4": orig[3], "o5": orig[4],
                        "o6": orig[5], "o7": orig[6], "o8": orig[7], "o9": orig[8], "o10": orig[9]
                    }
                    try:
                        requests.post(SCRIPT_URL, json=payload)
                    except:
                        st.error("Error al conectar con la base de datos.")
                
                if st.session_state.indice_palabra + 1 < len(PALABRAS_ESTIMULO):
                    st.session_state.indice_palabra += 1
                    st.session_state.paso = 1
                else:
                    st.session_state.paso = "grupo_focal"
                st.rerun()
            else:
                st.warning("Debes seleccionar tus 10 palabras antes de guardar.")














