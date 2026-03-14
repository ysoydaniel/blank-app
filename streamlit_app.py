import streamlit as st
from src.calculos import ejecutar_simulador

st.set_page_config(page_title="Simulador Tributario", layout="wide")

st.title("💰 Simulador Tributario 2026")

st.header("Datos de ingreso del cliente")

col1, col2 = st.columns(2)

with col1:

    salario_mensual = st.number_input(
        "¿Cuál es tu salario mensual?",
        value=25000000,
        step=100000,
        format="%d"
    )

    tipo_salario = st.selectbox(
        "¿Qué tipo de salario tienes?",
        ["Integral", "Ordinario"]
    )

    recibe_auxilios = st.selectbox(
        "¿Recibes auxilios?",
        ["Sí", "No"]
    )

    valor_auxilios_mensual = st.number_input(
        "Valor mensual de auxilios",
        value=2000000,
        step=100000,
        format="%d"
    )

    recibe_variable = st.selectbox(
        "¿Recibes comisiones o salario variable?",
        ["Sí", "No"]
    )

    valor_variable_anual = st.number_input(
        "Valor anual de variable o comisiones",
        value=24000000,
        step=100000,
        format="%d"
    )

with col2:

    tiene_bonificaciones = st.selectbox(
        "¿Tienes bonificaciones?",
        ["Sí", "No"]
    )

    valor_bonificaciones = st.number_input(
        "Valor anual de bonificaciones",
        value=40000000,
        step=100000,
        format="%d"
    )

    bono_salarial = st.selectbox(
        "¿Tu bono es salarial?",
        ["Sí", "No"]
    )

    aporte_voluntario_obligatorio_anual = st.number_input(
        "Aportes voluntarios al fondo obligatorio",
        value=15000000,
        step=100000,
        format="%d"
    )

    numero_dependientes = st.number_input(
        "Número de dependientes",
        value=2,
        step=1
    )

    intereses_vivienda_anual = st.number_input(
        "Intereses de vivienda al año",
        value=4500000,
        step=100000,
        format="%d"
    )

    pagos_salud_anual = st.number_input(
        "Pagos anuales de salud",
        value=6700000,
        step=100000,
        format="%d"
    )

    aportes_pension_afc_anual = st.number_input(
        "Aportes a pensión voluntaria o AFC",
        value=1500000,
        step=100000,
        format="%d"
    )

    compras_factura = st.number_input(
        "Compras con factura electrónica",
        value=45000000,
        step=100000,
        format="%d"
    )


inputs = {
    "salario_mensual": salario_mensual,
    "tipo_salario": tipo_salario,
    "valor_auxilios_mensual": valor_auxilios_mensual if recibe_auxilios == "Sí" else 0,
    "valor_variable_anual": valor_variable_anual if recibe_variable == "Sí" else 0,
    "valor_bonificaciones": valor_bonificaciones if tiene_bonificaciones == "Sí" else 0,
    "bono_salarial": bono_salarial,
    "aporte_voluntario_obligatorio_anual": aporte_voluntario_obligatorio_anual,
    "numero_dependientes": numero_dependientes,
    "intereses_vivienda_anual": intereses_vivienda_anual,
    "pagos_salud_anual": pagos_salud_anual,
    "aportes_pension_afc_anual": aportes_pension_afc_anual,
}

if st.button("Calcular simulación"):

    resultado = ejecutar_simulador(inputs)

    st.divider()
    st.header("Resultados")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Impuesto sin optimización",
            f"${resultado['impuesto_sin_optimizacion']:,.0f}"
        )

    with col2:
        st.metric(
            "Impuesto optimizado",
            f"${resultado['impuesto_optimizado']:,.0f}"
        )

    with col3:
        st.metric(
            "Beneficio",
            f"${resultado['beneficio']:,.0f}"
        )

    # -----------------------------
    # DEBUG COMPLETO
    # -----------------------------

    st.divider()
    st.subheader("🔎 Debug cálculos")

    debug_data = {

        "INPUTS": inputs,

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
        "impuesto_optimizado": resultado["impuesto_optimizado"],
    }

    st.json(debug_data)
