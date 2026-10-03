import streamlit as st
import pandas as pd
from conexion import obtener_coleccion

# --- Configuración inicial de la página web ---
st.set_page_config(page_title="Dashboard Climatización", page_icon="🌡️", layout="wide")

st.title("🌡️ Panel Analítico: Agente de Climatización")
st.write("Explora las reglas del agente y analiza los datos registrados en MongoDB Atlas.")

# --- SECCIÓN 1: Reglas del Agente ---
st.header("📋 Reglas de Decisión")
st.write("Haz clic en los botones para ver los rangos (Temperatura y Humedad) que activan cada respuesta:")

# Creamos 4 columnas para poner los botones uno al lado del otro
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("❄️ Aire Acondicionado"):
        st.info("**Rango de activación:**\n\nTemperatura > 30°C\n\n**Y**\n\nHumedad > 70%")
        
with col2:
    if st.button("💨 Ventilador"):
        st.info("**Rango de activación:**\n\nTemperatura > 30°C\n\n**Y**\n\nHumedad <= 70%")

with col3:
    if st.button("🔥 Calefacción"):
        st.info("**Rango de activación:**\n\nTemperatura < 18°C\n\n(Sin importar la humedad)")

with col4:
    if st.button("⏸️ Mantener Apagado"):
        st.info("**Rango de activación:**\n\nTemperatura entre 18°C y 30°C\n\n(Sin importar la humedad)")

st.divider() # Línea divisoria visual

# --- SECCIÓN 2: Extracción de Datos y Gráfica ---
st.header("📊 Gráfica de Dispersión de Decisiones")

# ¡Aquí usamos nuestro módulo de conexión!
coleccion = obtener_coleccion()
datos = list(coleccion.find({"tipo_registro": "clima"}, {"_id": 0, "temperatura_C": 1, "humedad_pct": 1, "accion_tomada": 1}))

if not datos:
    st.warning("No hay datos registrados en Atlas. Usa tu aplicación de Tkinter (agente.py) para insertar algunos.")
else:
    # Convertimos los datos de MongoDB a un DataFrame de Pandas
    df = pd.DataFrame(datos)
    
    # Renombrar columnas para que se vean profesionales en los ejes de la gráfica
    df = df.rename(columns={
        "temperatura_C": "Temperatura (°C)", 
        "humedad_pct": "Humedad (%)", 
        "accion_tomada": "Acción del Agente"
    })

    # Dibujar la gráfica de dispersión
    # x = Temperatura, y = Humedad, color = Agrupado por Acción
    st.scatter_chart(
        data=df,
        x='Temperatura (°C)',
        y='Humedad (%)',
        color='Acción del Agente',
        height=500
    )

    # Añadimos un panel desplegable por si quieres ver la tabla de datos exactos
    with st.expander("Ver tabla de datos crudos"):
        st.dataframe(df, use_container_width=True)