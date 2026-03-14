import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Tributario", page_icon="💰", layout="wide")

st.title("Simulador Tributario")
st.caption("Simulación de impuesto de renta y optimización tributaria")

st.subheader("1. Datos de ingreso del cliente")

col1, col2 = st.columns(2)

with col1:
    salario_mensual = st.number_input(
        "¿Cuál es tu salario mensual?",
        min_value=0,
        value=25000000,
        step=100000
    )

    tipo_salario = st.selectbox(
        "¿Qué tipo de salario tienes?",
        ["Ordinario", "Integral"]
    )

    recibe_auxilios = st.radio(
        "¿Recibes auxilios?",
        ["Sí", "No"],
        horizontal=True
    )

    valor_auxilios_mensual = st.number_input(
        "¿Cuál es el valor mensual de tus auxilios?",
        min_value=0,
        value=2000000 if recibe_auxilios == "Sí" else 0,
        step=100000,
        disabled=(recibe_auxilios == "No")
    )

    recibe_variable = st.radio(
        "¿Recibes comisiones o salario variable?",
        ["Sí", "No"],
        horizontal=True
    )

    valor_variable_anual = st.number_input(
        "¿Cuál es el valor anual de tu variable o comisiones?",
        min_value=0,
        value=24000000 if recibe_variable == "Sí" else 0,
        step=100000,
        disabled=(recibe_variable == "No")
    )

with col2:
    tiene_bonificaciones = st.radio(
        "¿Tienes bonificaciones?",
        ["Sí", "No"],
        horizontal=True
    )

    valor_bonificaciones = st.number_input(
        "¿Cuál es el valor de tus bonificaciones?",
        min_value=0,
        value=40000000 if tiene_bonificaciones == "Sí" else 0,
        step=100000,
        disabled=(tiene_bonificaciones == "No")
    )

    bono_salarial = st.radio(
        "¿Tu bono es salarial?",
        ["Sí", "No"],
        horizontal=True
    )

st.divider()

st.subheader("2. Beneficios y deducciones")

col3, col4 = st.columns(2)

with col3:
    aporte_voluntario_obligatorio_anual = st.number_input(
        "¿Cuánto aportas anualmente de manera voluntaria a tu fondo obligatorio?",
        min_value=0,
        value=15000000,
        step=100000
    )

    numero_dependientes = st.number_input(
        "¿Cuántos dependientes tienes?",
        min_value=0,
        max_value=4,
        value=2,
        step=1
    )

    intereses_vivienda_anual = st.number_input(
        "¿Cuánto pagas anualmente de intereses de vivienda?",
        min_value=0,
        value=4500000,
        step=100000
    )

with col4:
    pagos_salud_anual = st.number_input(
        "¿Cuánto pagas anualmente en planes de salud?",
        min_value=0,
        value=6700000,
        step=100000
    )

    aportes_pension_afc_anual = st.number_input(
        "¿Cuánto aportas anualmente en pensión voluntaria o AFC?",
        min_value=0,
        value=1500000,
        step=100000
    )

    compras_factura_electronica = st.number_input(
        "¿Cuál crees que va a ser el valor de tus compras con factura electrónica?",
        min_value=0,
        value=45000000,
        step=100000
    )

if st.button("Calcular simulación", use_container_width=True):
    st.success("Formulario listo. Aquí conectas la lógica del simulador.")
