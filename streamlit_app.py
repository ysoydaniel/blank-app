import streamlit as st
import pandas as pd

from src.calculos import ejecutar_simulador
from src.formateo import formato_moneda, formato_numero, formato_porcentaje

st.set_page_config(
    page_title="Simulador Tributario 2026",
    page_icon="💰",
    layout="wide"
)

st.title("Simulador Tributario 2026")
st.caption("Prototipo funcional basado en la maqueta de Excel")

st.markdown("## Datos de ingreso del cliente")

col1, col2 = st.columns(2)

with col1:
    salario_mensual = st.number_input(
        "¿Cuál es tu salario mensual?",
        min_value=0.0,
        value=25000000.0,
        step=100000.0,
        help="Si es salario ordinario se multiplica por 12; si es salario integral se usa la lógica del simulador."
    )

    tipo_salario = st.selectbox(
        "¿Qué tipo de salario tienes?",
        ["Ordinario", "Integral"]
    )

    recibe_auxilios = st.radio(
        "¿Recibes auxilios? Tipo conectividad o transporte",
        ["Sí", "No"],
        horizontal=True
    )

    valor_auxilios_mensual = st.number_input(
        "¿Cuál es el valor mensual de tus auxilios?",
        min_value=0.0,
        value=2000000.0 if recibe_auxilios == "Sí" else 0.0,
        step=100000.0,
        disabled=(recibe_auxilios == "No"),
        help="El valor mensual de auxilios no debería ser mayor al 50% del salario mensual."
    )

    recibe_variable = st.radio(
        "¿Recibes comisiones o salario variable?",
        ["Sí", "No"],
        horizontal=True
    )

    valor_variable_anual = st.number_input(
        "¿Cuál es el valor anual de tu variable o comisiones?",
        min_value=0.0,
        value=24000000.0 if recibe_variable == "Sí" else 0.0,
        step=100000.0,
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
        min_value=0.0,
        value=40000000.0 if tiene_bonificaciones == "Sí" else 0.0,
        step=100000.0,
        disabled=(tiene_bonificaciones == "No")
    )

    bono_salarial = st.radio(
        "¿Tu bono es salarial?",
        ["Sí", "No"],
        horizontal=True,
        help="Si marcas sí, el bono tiene aporte a seguridad social; si marcas no, no tiene aporte."
    )

st.divider()

st.markdown("## Beneficios y deducciones")

col3, col4 = st.columns(2)

with col3:
    aporte_voluntario_obligatorio_anual = st.number_input(
        "¿Cuánto aportas anualmente de manera voluntaria a tu fondo obligatorio?",
        min_value=0.0,
        value=15000000.0,
        step=100000.0
    )

    numero_dependientes = st.number_input(
        "¿Cuántos dependientes tienes?",
        min_value=0,
        max_value=4,
        value=2,
        step=1,
        help="Máximo 4 dependientes."
    )

    intereses_vivienda_anual = st.number_input(
        "¿Cuánto pagas anualmente de intereses de vivienda?",
        min_value=0.0,
        value=4500000.0,
        step=100000.0
    )

with col4:
    pagos_salud_anual = st.number_input(
        "¿Cuánto pagas anualmente en planes de salud?",
        min_value=0.0,
        value=6700000.0,
        step=100000.0
    )

    aportes_pension_afc_anual = st.number_input(
        "¿Cuánto aportas anualmente en pensión voluntaria o AFC?",
        min_value=0.0,
        value=1500000.0,
        step=100000.0
    )

    compras_factura_electronica = st.number_input(
        "¿Cuál crees que va a ser el valor de tus compras con factura electrónica?",
        min_value=0.0,
        value=45000000.0,
        step=100000.0,
        help="Por ahora este campo se captura, pero no se está usando en el cálculo base del MVP."
    )

st.divider()

errores = []

if recibe_auxilios == "No":
    valor_auxilios_mensual = 0.0

if recibe_variable == "No":
    valor_variable_anual = 0.0

if tiene_bonificaciones == "No":
    valor_bonificaciones = 0.0

if valor_auxilios_mensual > salario_mensual * 0.5:
    errores.append("El valor mensual de los auxilios no puede ser mayor al 50% del salario mensual.")

if numero_dependientes > 4:
    errores.append("El número de dependientes no puede ser mayor a 4.")

inputs = {
    "salario_mensual": salario_mensual,
    "tipo_salario": tipo_salario,
    "valor_auxilios_mensual": valor_auxilios_mensual,
    "valor_variable_anual": valor_variable_anual,
    "valor_bonificaciones": valor_bonificaciones,
    "bono_salarial": bono_salarial,
    "aporte_voluntario_obligatorio_anual": aporte_voluntario_obligatorio_anual,
    "numero_dependientes": numero_dependientes,
    "intereses_vivienda_anual": intereses_vivienda_anual,
    "pagos_salud_anual": pagos_salud_anual,
    "aportes_pension_afc_anual": aportes_pension_afc_anual,
    "compras_factura_electronica": compras_factura_electronica,
}

if st.button("Calcular simulación", use_container_width=True):
    if errores:
        for error in errores:
            st.error(error)
    else:
        resultado = ejecutar_simulador(inputs)

        st.markdown("## Resultados")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Tu impuesto de renta sin optimización",
            formato_moneda(resultado["impuesto_sin_optimizacion"])
        )
        c2.metric(
            "Tu impuesto de renta optimizado al máximo",
            formato_moneda(resultado["impuesto_optimizado"])
        )
        c3.metric(
            "Beneficio",
            formato_moneda(resultado["beneficio"])
        )

        st.divider()

        c4, c5 = st.columns([1.2, 1])

        with c4:
            st.markdown("### Desglose del cálculo")

            df_detalle = pd.DataFrame(
                [
                    {"Concepto": "Salario anual", "Valor": formato_moneda(resultado["salario_anual"])},
                    {"Concepto": "Ingreso variable anual", "Valor": formato_moneda(resultado["ingreso_variable"])},
                    {"Concepto": "Auxilios anuales", "Valor": formato_moneda(resultado["auxilios_anuales"])},
                    {"Concepto": "Bonificación anual", "Valor": formato_moneda(resultado["bonificacion_anual"])},
                    {"Concepto": "Total ingresos", "Valor": formato_moneda(resultado["total_ingresos"])},
                    {"Concepto": "Ingresos no constitutivos", "Valor": formato_moneda(resultado["ingresos_no_constitutivos"])},
                    {"Concepto": "Deducciones admisibles", "Valor": formato_moneda(resultado["deducciones_admisibles"])},
                    {"Concepto": "Base gravable", "Valor": formato_moneda(resultado["base_gravable"])},
                    {"Concepto": "Base gravable con PAC", "Valor": formato_moneda(resultado["base_gravable_pac"])},
                    {"Concepto": "Base gravable UVT", "Valor": formato_numero(resultado["base_uvt"])},
                    {"Concepto": "Base gravable UVT con PAC", "Valor": formato_numero(resultado["base_uvt_pac"])},
                ]
            )

            st.dataframe(df_detalle, use_container_width=True, hide_index=True)

        with c5:
            st.markdown("### Interpretación")
            st.success(
                f"Con base en la información registrada, el cliente podría obtener un beneficio tributario estimado de "
                f"{formato_moneda(resultado['beneficio'])}."
            )

            st.info(
                "Este MVP replica la lógica base del Excel. "
                "Antes de producción conviene validar reglas puntuales como dependientes y compras con factura electrónica."
            )

        with st.expander("Ver detalle técnico"):
            st.write({
                "aporte_eps": resultado["aporte_eps"],
                "aporte_pension": resultado["aporte_pension"],
                "fondo_solidaridad": resultado["fondo_solidaridad"],
                "renta_liquida": resultado["renta_liquida"],
                "renta_liquida_pac": resultado["renta_liquida_pac"],
                "dependientes": resultado["dependientes"],
                "intereses_vivienda": resultado["intereses_vivienda"],
                "pagos_salud": resultado["pagos_salud"],
                "cesantias": resultado["cesantias"],
                "aportes_pension_afc": resultado["aportes_pension_afc"],
                "renta_exenta_laboral": resultado["renta_exenta_laboral"],
                "total_deducciones": resultado["total_deducciones"],
            })
else:
    st.info("Completa los datos y pulsa **Calcular simulación**.")
