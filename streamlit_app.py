import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.calculos import ejecutar_simulador, calcular_impuesto_renta
from src.formateo import formato_moneda

st.set_page_config(
    page_title="Simulador Tributario 2026",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Simulador Tributario 2026")
st.caption("Prototipo funcional")

# =========================
# INPUTS
# =========================

col1, col2 = st.columns(2)

with col1:

    salario_mensual = st.number_input(
        "Salario mensual",
        value=25000000
    )

    tipo_salario = st.selectbox(
        "Tipo salario",
        ["Integral", "Ordinario"]
    )

    valor_auxilios_mensual = st.number_input(
        "Auxilios mensuales",
        value=2000000
    )

    valor_variable_anual = st.number_input(
        "Variable anual",
        value=24000000
    )

with col2:

    valor_bonificaciones = st.number_input(
        "Bonificaciones",
        value=40000000
    )

    numero_dependientes = st.number_input(
        "Dependientes",
        value=2
    )

    intereses_vivienda_anual = st.number_input(
        "Intereses vivienda",
        value=4500000
    )

    pagos_salud_anual = st.number_input(
        "Pagos salud",
        value=6700000
    )

    aportes_pension_afc_anual = st.number_input(
        "Aportes AFC",
        value=1500000
    )

inputs = {
    "salario_mensual": salario_mensual,
    "tipo_salario": tipo_salario,
    "valor_auxilios_mensual": valor_auxilios_mensual,
    "valor_variable_anual": valor_variable_anual,
    "valor_bonificaciones": valor_bonificaciones,
    "numero_dependientes": numero_dependientes,
    "intereses_vivienda_anual": intereses_vivienda_anual,
    "pagos_salud_anual": pagos_salud_anual,
    "aportes_pension_afc_anual": aportes_pension_afc_anual,
}

# =========================
# SIMULACIÓN
# =========================

if st.button("Calcular simulación"):

    resultado = ejecutar_simulador(inputs)

    impuesto = resultado["impuesto_sin_optimizacion"]

    st.subheader("Resultados")

    c1, c2, c3 = st.columns(3)

    c1.metric("Impuesto actual", formato_moneda(impuesto))
    c2.metric("Top-Up máximo", formato_moneda(resultado["topup_full"]))
    c3.metric("Beneficio potencial", formato_moneda(resultado["beneficio"]))

    # =========================
    # SLIDER TOP UP
    # =========================

    st.subheader("Simulación interactiva de Top-Up")

    topup_usuario = st.slider(
        "Aporte adicional",
        min_value=0,
        max_value=int(resultado["topup_full"]),
        value=0,
        step=500000
    )

    nueva_base = resultado["base_gravable"] - topup_usuario

    base_uvt = nueva_base / resultado["uvt"]

    impuesto_topup = calcular_impuesto_renta(
        base_uvt,
        resultado["uvt"]
    )

    ahorro = impuesto - impuesto_topup

    c1, c2, c3 = st.columns(3)

    c1.metric("Aporte adicional", formato_moneda(topup_usuario))
    c2.metric("Nuevo impuesto", formato_moneda(impuesto_topup))
    c3.metric("Ahorro generado", formato_moneda(ahorro))

    # =========================
    # GRÁFICA
    # =========================

    st.subheader("Curva de optimización")

    aportes = []
    ahorros = []

    step = resultado["topup_full"] / 10

    for i in range(11):

        aporte = step * i

        base = resultado["base_gravable"] - aporte

        base_uvt = base / resultado["uvt"]

        impuesto_temp = calcular_impuesto_renta(base_uvt, resultado["uvt"])

        ahorro_temp = impuesto - impuesto_temp

        aportes.append(aporte)
        ahorros.append(ahorro_temp)

    fig, ax = plt.subplots()

    ax.plot(aportes, ahorros)

    ax.set_xlabel("Aporte adicional")
    ax.set_ylabel("Ahorro tributario")

    st.pyplot(fig)
