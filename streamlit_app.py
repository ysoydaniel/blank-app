import streamlit as st
from src.calculos import ejecutar_simulador

st.set_page_config(
    page_title="Simulador Tributario 2026",
    layout="wide",
)

# ---------------------------------------------------
# TEMA VISUAL PREMIUM
# ---------------------------------------------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#0b1020 0%,#111827 50%,#0f172a 100%);
}

h1,h2,h3 {
    color:white;
    font-weight:700;
}

p,label,span,div {
    color:#E5E7EB;
}

/* Selectbox */

div[data-baseweb="select"] > div {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(96,165,250,0.4);
    border-radius:14px;
}

/* Inputs */

div[data-baseweb="input"] > div {
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(96,165,250,0.4);
    border-radius:14px;
}

/* Botón */

.stButton > button {
    width:100%;
    background:linear-gradient(135deg,#2563EB,#1D4ED8);
    color:white;
    border:none;
    border-radius:14px;
    padding:0.8rem;
    font-weight:700;
}

/* Métricas */

div[data-testid="stMetric"] {
    background:rgba(255,255,255,0.06);
    border-radius:20px;
    padding:20px;
    border:1px solid rgba(255,255,255,0.05);
}

div[data-testid="stMetricValue"] {
    font-size:32px;
    font-weight:800;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown("""
<div style="
padding:24px;
border-radius:20px;
background:rgba(255,255,255,0.05);
border:1px solid rgba(255,255,255,0.08);
margin-bottom:20px;
">
<h1>💰 Simulador Tributario 2026</h1>
<p>Convierte un modelo tributario en Excel en una experiencia web clara y escalable.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FORMULARIO
# ---------------------------------------------------

st.header("Datos del cliente")

col1, col2 = st.columns(2)

with col1:

    salario_mensual = st.number_input(
        "Salario mensual",
        value=25000000,
        step=100000,
        format="%d"
    )

    tipo_salario = st.selectbox(
        "Tipo de salario",
        ["Integral", "Ordinario"]
    )

    recibe_auxilios = st.selectbox(
        "¿Recibe auxilios?",
        ["Sí", "No"]
    )

    valor_auxilios_mensual = st.number_input(
        "Auxilios mensuales",
        value=2000000,
        step=100000,
        format="%d"
    )

    recibe_variable = st.selectbox(
        "¿Recibe comisiones o variable?",
        ["Sí", "No"]
    )

    valor_variable_anual = st.number_input(
        "Variable anual",
        value=24000000,
        step=100000,
        format="%d"
    )

with col2:

    tiene_bono = st.selectbox(
        "¿Tiene bonificaciones?",
        ["Sí", "No"]
    )

    valor_bono = st.number_input(
        "Valor bonificación anual",
        value=40000000,
        step=100000,
        format="%d"
    )

    bono_salarial = st.selectbox(
        "¿El bono es salarial?",
        ["Sí", "No"]
    )

    aporte_voluntario = st.number_input(
        "Aporte voluntario pensión obligatoria",
        value=15000000,
        step=100000,
        format="%d"
    )

    dependientes = st.number_input(
        "Número de dependientes",
        value=2,
        step=1
    )

    intereses_vivienda = st.number_input(
        "Intereses vivienda anual",
        value=4500000,
        step=100000,
        format="%d"
    )

    pagos_salud = st.number_input(
        "Pagos salud anual",
        value=6700000,
        step=100000,
        format="%d"
    )

    aportes_afc = st.number_input(
        "Aportes AFC / pensión voluntaria",
        value=1500000,
        step=100000,
        format="%d"
    )

# ---------------------------------------------------
# NORMALIZACIÓN INPUTS
# ---------------------------------------------------

inputs = {
    "salario_mensual": salario_mensual,
    "tipo_salario": tipo_salario,
    "valor_auxilios_mensual": valor_auxilios_mensual if recibe_auxilios == "Sí" else 0,
    "valor_variable_anual": valor_variable_anual if recibe_variable == "Sí" else 0,
    "valor_bonificaciones": valor_bono if tiene_bono == "Sí" else 0,
    "bono_salarial": bono_salarial,
    "aporte_voluntario_obligatorio_anual": aporte_voluntario,
    "numero_dependientes": dependientes,
    "intereses_vivienda_anual": intereses_vivienda,
    "pagos_salud_anual": pagos_salud,
    "aportes_pension_afc_anual": aportes_afc,
}

# ---------------------------------------------------
# EJECUTAR SIMULACIÓN
# ---------------------------------------------------

if st.button("Calcular simulación"):

    resultado = ejecutar_simulador(inputs)

    st.divider()

    st.header("Resultado de la simulación")

    c1,c2,c3 = st.columns(3)

    with c1:
        st.metric(
            "Impuesto actual",
            f"${resultado['impuesto_sin_optimizacion']:,.0f}"
        )

    with c2:
        st.metric(
            "Impuesto optimizado",
            f"${resultado['impuesto_optimizado']:,.0f}"
        )

    with c3:
        st.metric(
            "Ahorro estimado",
            f"${resultado['beneficio']:,.0f}"
        )

    # ---------------------------------------------------
    # DEBUG COLAPSABLE
    # ---------------------------------------------------

    with st.expander("🔎 Debug cálculos"):

        debug_data = {

            "inputs": inputs,

            "salario_anual": resultado["salario_anual"],
            "ingreso_variable": resultado["ingreso_variable"],
            "auxilios_anuales": resultado["auxilios_anuales"],
            "bonificacion_anual": resultado["bonificacion_anual"],

            "total_ingresos": resultado["total_ingresos"],

            "base_seguridad_social": resultado["base_seg_social"],
            "base_bono": resultado["base_bono"],

            "aporte_eps": resultado["aporte_eps"],
            "aporte_pension": resultado["aporte_pension"],
            "fondo_solidaridad": resultado["fondo_solidaridad"],

            "ingresos_no_constitutivos": resultado["ingresos_no_constitutivos"],

            "renta_liquida": resultado["renta_liquida"],
            "renta_liquida_pac": resultado["renta_liquida_pac"],

            "dependientes": resultado["dependientes"],
            "intereses_vivienda": resultado["intereses_vivienda"],
            "pagos_salud": resultado["pagos_salud"],
            "cesantias": resultado["cesantias"],
            "aportes_pension_afc": resultado["aportes_pension_afc"],

            "renta_exenta_sin_limite": resultado["renta_exenta_sin_limite"],
            "renta_exenta_laboral": resultado["renta_exenta_laboral"],

            "total_deducciones": resultado["total_deducciones"],
            "deducciones_admisibles": resultado["deducciones_admisibles"],

            "base_gravable": resultado["base_gravable"],
            "base_gravable_pac": resultado["base_gravable_pac"],

            "base_uvt": resultado["base_uvt"],
            "base_uvt_pac": resultado["base_uvt_pac"],

            "impuesto_sin_optimizacion": resultado["impuesto_sin_optimizacion"],
            "impuesto_optimizado": resultado["impuesto_optimizado"]
        }

        st.json(debug_data)
