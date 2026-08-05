import streamlit as st

st.title("⚙️ AGROCISA Core - Prueba")

# 1. Preguntamos si está autenticado
if "acceso" not in st.session_state:
    st.session_state["acceso"] = False

# 2. Si NO tiene acceso, mostramos el login
if not st.session_state["acceso"]:
    clave = st.text_input("Mete la clave de TI:", type="password")
    
    if st.button("Entrar"):
        if clave == "bicho123":
            st.session_state["acceso"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
            
    st.stop() # ¡Aquí se frena todo si no hay clave!

# 3. Si SÍ tiene acceso, se abre el sistema
st.success("¡Bienvenido al sistema, bicho!")
st.write("Aquí va a ir tu panel para controlar la red y los equipos.")