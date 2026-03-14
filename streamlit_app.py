import streamlit as st
import matplotlib.pyplot as plt

from src.calculos import ejecutar_simulador, calcular_impuesto_renta
from src.formateo import formato_moneda

st.set_page_config(
    page_title="Simulador Tributario 2026",
    page_icon="🧮",
    layout="wide"
)

# =========================
# HEADER
# =========================

st.markdown(
    """
    <div style="
        padding:24px;
        border-radius:20px;
        background:linear-gradient(135deg,#1f2937,#111827);
        border:1px solid #374151;
        margin-bottom:25px;
    ">
        <div style="font-size:13px;color:#9ca3af;">
        Herramienta de asesoría financiera
        </div>
        <div style="font-size:34px;font-weight:700;margin-top:6px;">
        Simulador Tributario 2026
        </div>
        <div style="font-size:14px;color:#9ca3af;margin-top:6px;">
        Identifica oportunidades de optimización tributaria
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# INPUTS
# =========================

col1, col2 = st.columns(2)

with col1:

    salario_mensual = st.number_input("Salario mensual", value=25000000)

    valor_auxilios_mensual = st.number_input("Auxilios mensuales", value=2000000)

    valor_variable_anual = st.number_input("Variable anual", value=24000000)

with col2:

    valor_bonificaciones = st.number_input("Bonificaciones", value=40000000)

    numero_dependientes = st.number_input("Dependientes", value=2)

    intereses_vivienda_anual = st.number_input("Intereses vivienda", value=4500000)

    pagos_salud_anual = st.number_input("Pagos salud", value=6700000)

    aportes_pension_afc_anual = st.number_input("Aportes AFC", value=1500000)

inputs = {
    "salario_mensual": salario_mensual,
    "valor_auxilios_mensual": valor_auxilios_mensual,
    "valor_variable_anual": valor_variable_anual,
    "valor_bonificaciones": valor_bonificaciones,
    "numero_dependientes": numero_dependientes,
    "intereses_vivienda_anual": intereses_vivienda_anual,
    "pagos_salud_anual": pagos_salud_anual,
    "aportes_pension_afc_anual": aportes_pension_afc_anual,
}

# =========================
# SIMULACION
# =========================

if st.button("Calcular simulación"):

    resultado = ejecutar_simulador(inputs)

    ahorro = resultado["beneficio"]
    impuesto_original = resultado["impuesto_sin_optimizacion"]
    impuesto_optimizado = resultado["impuesto_optimizado"]

    st.markdown("## Oportunidad tributaria detectada")

    st.markdown(
        f"""
        <div style="
        padding:30px;
        border-radius:22px;
        background:linear-gradient(135deg,#10b98122,#10b98108);
        border:1px solid #10b98155;
        text-align:center;
        ">
        <div style="font-size:42px;font-weight:800;">
        {formato_moneda(ahorro)}
        </div>
        <div style="font-size:14px;color:#9ca3af;">
        ahorro potencial estimado
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # COMPARACION
    # =========================

    st.markdown("## Comparación tributaria")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Escenario actual", formato_moneda(impuesto_original))

    with col2:
        st.metric("Escenario optimizado", formato_moneda(impuesto_optimizado))

    porcentaje = ahorro / impuesto_original

    st.progress(porcentaje)

    # =========================
    # SIMULACION TOP UP
    # =========================

    st.markdown("## Simulación interactiva")

    topup_max = int(resultado["topup_full"])

    topup_usuario = st.slider(
        "Aporte adicional",
        0,
        topup_max,
        step=500000
    )

    nueva_base = resultado["base_gravable"] - topup_usuario

    base_uvt = nueva_base / resultado["uvt"]

    impuesto_topup = calcular_impuesto_renta(
        base_uvt,
        resultado["uvt"]
    )

    ahorro_topup = impuesto_original - impuesto_topup

    col1, col2, col3 = st.columns(3)

    col1.metric("Aporte adicional", formato_moneda(topup_usuario))
    col2.metric("Nuevo impuesto", formato_moneda(impuesto_topup))
    col3.metric("Ahorro", formato_moneda(ahorro_topup))

    # =========================
    # GRAFICA
    # =========================

    aportes = []
    ahorros = []

    step = topup_max / 10 if topup_max > 0 else 1

    for i in range(11):

        aporte = step * i

        base = resultado["base_gravable"] - aporte

        base_uvt = base / resultado["uvt"]

        impuesto_temp = calcular_impuesto_renta(
            base_uvt,
            resultado["uvt"]
        )

        ahorro_temp = impuesto_original - impuesto_temp

        aportes.append(aporte)
        ahorros.append(ahorro_temp)

    fig, ax = plt.subplots()

    ax.plot(aportes, ahorros)

    ax.set_xlabel("Aporte adicional")
    ax.set_ylabel("Ahorro tributario")

    st.pyplot(fig)

    # =========================
    # INSIGHT
    # =========================

    if porcentaje > 0.25:

        st.success("Alta oportunidad de optimización tributaria")

    elif porcentaje > 0.10:

        st.info("Existe una oportunidad relevante de optimización tributaria")

    else:

        st.warning("La optimización tributaria posible es moderada")
