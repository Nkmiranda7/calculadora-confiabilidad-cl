import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Título y Configuración de la página
st.set_page_config(page_title="Confiabilidad Chile", layout="centered")
st.title("🇨🇱 Calculadora de Confiabilidad Industrial")
st.markdown("Herramienta para cálculo de disponibilidad en equipos mineros e industriales.")

# 2. Barra lateral para ingresar datos (Inputs)
st.sidebar.header("Parámetros del Equipo")
mtbf = st.sidebar.number_input("MTBF (Horas promedio entre fallas)", value=500.0, min_value=1.0)
mttr = st.sidebar.number_input("MTTR (Horas promedio para reparar)", value=24.0, min_value=0.1)

# 3. Lógica Matemática (El cálculo)
# Fórmula: A = MTBF / (MTBF + MTTR)
disponibilidad = (mtbf / (mtbf + mttr)) * 100
indisponibilidad = 100 - disponibilidad

# 4. Mostrar Resultados (KPIs)
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Disponibilidad Inherente", value=f"{disponibilidad:.2f}%")
    
with col2:
    st.metric(label="Tiempo Muerto (Unavailability)", value=f"{indisponibilidad:.2f}%")

# 5. Gráfico de Torta (Visualización)
st.subheader("Distribución de Tiempo")
fig, ax = plt.subplots()
labels = ['Operativo (MTBF)', 'En Reparación (MTTR)']
sizes = [disponibilidad, indisponibilidad]
colors = ['#4CAF50', '#FF5722'] # Verde y Naranja industrial

ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
ax.axis('equal') # Para que sea un círculo perfecto

st.pyplot(fig)

# Nota al pie
st.info("Cálculo basado en estándares de Mantenimiento Clase Mundial.")

# --- MÓDULO 2: ANÁLISIS DE WEIBULL (CRÍTICO PARA CONFIABILIDAD) ---

st.divider()
st.header("🔬 Análisis de Weibull (Vida Útil)")
st.markdown("Ingresa un set de tiempos de falla de equipos similares (separados por coma).")

# Input para los tiempos de falla
falla_input = st.text_area(
    "Tiempos de Falla (Horas o Ciclos)", 
    "1500, 1800, 1950, 2100, 2400, 2750, 2900, 3100, 3300"
)

# Botón para activar el cálculo de Weibull
if st.button("Calcular Distribución Weibull"):
    try:
        # Convertir la cadena de texto a una lista de números (horas de falla)
        tiempos_falla = np.array([float(x.strip()) for x in falla_input.split(',')])
        
        # 1. Calcular los parámetros de Weibull (Beta y Eta)
        from scipy.stats import weibull_min
        
        # Ajuste de los datos para encontrar los parámetros
        # Usamos fit(datos, c, loc=0, scale=1)
        # c = parámetro de forma (beta), loc = ubicación (0), scale = vida característica (eta)
        params = weibull_min.fit(tiempos_falla, floc=0)
        beta_weibull = params[0] # Parámetro de Forma (beta)
        eta_weibull = params[2]  # Parámetro de Escala (eta) o vida característica

        st.subheader("Resultados del Análisis de Weibull")
        
        col_w1, col_w2 = st.columns(2)
        
        with col_w1:
            st.metric(label="Parámetro de Forma (β - Beta)", value=f"{beta_weibull:.3f}")
        with col_w2:
            st.metric(label="Vida Característica (η - Eta)", value=f"{eta_weibull:.2f} Horas")
        
        st.info(f"""
        **Interpretación de β (Beta):**
        * Si β < 1: Fallas decrecientes (Mortalidad Infantil).
        * Si **β ≈ 1**: Fallas constantes (Vida Útil Normal, tasa de falla aleatoria).
        * Si **β > 1**: Fallas crecientes (Desgaste, envejecimiento del equipo).
        En este caso, β = **{beta_weibull:.3f}**.
        """)
        
        # 2. Generar y mostrar el gráfico de Densidad de Probabilidad (PDF)
        st.subheader("Gráfico de Densidad de Probabilidad (PDF)")
        
        t_max = np.max(tiempos_falla) * 1.5
        t = np.linspace(0, t_max, 100)
        
        # Función de Densidad de Probabilidad de Weibull (PDF)
        pdf = weibull_min.pdf(t, beta_weibull, loc=0, scale=eta_weibull)
        
        fig_w, ax_w = plt.subplots()
        ax_w.plot(t, pdf, color='purple')
        ax_w.set_xlabel("Tiempo (t)")
        ax_w.set_ylabel("Probabilidad de Falla")
        ax_w.set_title("Distribución de Weibull")
        st.pyplot(fig_w)

    except Exception as e:
        st.error(f"Error en el cálculo de Weibull. Asegúrate que los datos sean números separados por comas. Error: {e}")