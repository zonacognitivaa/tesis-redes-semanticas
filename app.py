elif st.session_state.paso == 2:
        st.write("Selecciona tus palabras en orden de importancia de acuerdo con lo que tú opines:")
        st.markdown(f"<h3 style='text-align: center; color: #4A90E2;'>\"{frase_actual}\"</h3>", unsafe_allow_html=True)
        st.info("💡 La #1 es la de mayor relación y la #10 la de menor relación.") 
        
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            ranking = st.multiselect("Haz clic para elegir:", st.session_state.temp_words, max_selections=10)
        with col_der:
            if ranking:
                st.markdown("### 📌 Tu orden actual:")
                lista = "".join([f"<span style='color:#4A90E2'>**{i+1}.**</span> {p}  \n" for i, p in enumerate(ranking)])
                st.markdown(lista, unsafe_allow_html=True)
        
        if st.button("Guardar y continuar", disabled=st.session_state.bloqueo_boton):
            st.session_state.bloqueo_boton = True
            if len(ranking) == 10 or modo_prueba:
                r, o = (ranking, st.session_state.temp_words)
                
                # 👇 ZONA SEGURA PARA ENVIAR AL EXCEL 👇
                if not modo_prueba:
                    payload = {"tipo": "redes", "iniciales": st.session_state.iniciales, "edad": st.session_state.edad, "sexo": st.session_state.sexo, "estado_civil": st.session_state.estado_civil, "rel_crianza": st.session_state.rel_crianza, "rel_actual": st.session_state.rel_actual, "influencia": st.session_state.influencia_rel, "correo": st.session_state.correo, "institucion": st.session_state.institucion, "detalle": st.session_state.detalle_instit, "grupo": st.session_state.grupo_asignado, "frase": frase_actual, "r1": r[0], "r2": r[1], "r3": r[2], "r4": r[3], "r5": r[4], "r6": r[5], "r7": r[6], "r8": r[7], "r9": r[8], "r10": r[9], "o1": o[0], "o2": o[1], "o3": o[2], "o4": o[3], "o5": o[4], "o6": o[5], "o7": o[6], "o8": o[7], "o9": o[8], "o10": o[9]}
                    
                    if st.session_state.indice_palabra == 0 and st.session_state.archivo_b64 != "":
                        payload["archivo_b64"] = st.session_state.archivo_b64
                    else:
                        payload["archivo_b64"] = ""
                        
                    requests.post(SCRIPT_URL, json=payload)
                # 👆 FIN DE LA ZONA SEGURA 👆
                
                if st.session_state.indice_palabra + 1 < len(PALABRAS_ESTIMULO):
                    st.session_state.indice_palabra += 1
                    st.session_state.paso = 1
                else: 
                    st.session_state.paso = "grupo_focal"
                st.session_state.bloqueo_boton = False
                st.rerun()
            else: 
                st.warning("⚠️ Selecciona las 10 palabras.")
                st.session_state.bloqueo_boton = False
                
    st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
