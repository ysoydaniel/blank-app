import streamlit as st
import pandas as pd
import re

from src.calculos import ejecutar_simulador
from src.formateo import formato_moneda, formato_numero

st.set_page_config(
    page_title="Simulador Tributario 2026 ",
    page_icon="💰",
    layout="wide"
)

st.title("Simulador Tributario 2026")
st.caption("Prototipo funcional")

# =========================
# Helpers
# =========================
def valor_si_no_a_bool(valor: str) -> bool:
    return valor == "Sí"

def money_input(
    label,
    value=0,
    key=None,
    help_text=None,
    disabled=False
):

    # valor inicial formateado
    valor_inicial =f"${value:,.0f}".replace(",", "."),

    valor_str = st.text_input(
        label,
        value=valor_inicial,
        key=key,
        help=help_text,
        disabled=disabled
    )

    # limpiar caracteres que no sean números
    solo_numeros = re.sub(r"[^\d]", "", valor_str)

    if solo_numeros == "":
        valor_num = 0
    else:
        valor_num = int(solo_numeros)

    # formatear nuevamente
    valor_formateado = f"{valor_num:,}".replace(",", ".")

    # actualizar estado para mantener formato
    st.session_state[key] = valor_formateado

    return float(valor_num)


# =========================
# Header / modo debug
# =========================
with st.sidebar:
    st.markdown("## Configuración")
    mostrar_debug = st.checkbox("Mostrar detalle técnico", value= False)
    st.caption("Úsalo para comparar contra el Excel y encontrar diferencias.")

# =========================
# Formulario
# =========================


st.markdown("""
<div style="
    padding: 22px 24px;
    border-radius: 22px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 18px;
">
    <div style="font-size: 13px; color: #93C5FD; font-weight: 700; letter-spacing: .08em;">
        FORMULARIO
    </div>
    <div style="font-size: 26px; color: white; font-weight: 800; margin-top: 6px;">
        Información del cliente
    </div>
    <div style="font-size: 15px; color: #CBD5E1; margin-top: 8px;">
        Completa los datos de ingresos y beneficios tributarios para estimar el impuesto y el ahorro potencial.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, sep, col3, col4 = st.columns([1, 1, 0.06, 1, 1])

with col1:
    st.markdown("### 💼 Ingresos")
    
    salario_mensual = money_input(
    "¿Cuál es tu salario mensual?",
    value=25000000,
    help_text="Ingresa tu salario mensual antes de deducciones.",
    key="salario_mensual"
)

    tipo_salario = st.selectbox(
        "¿Qué tipo de salario tienes?",
        ["Integral", "Ordinario"],
        help="El salario integral ya incluye prestaciones sociales. El ordinario sí genera prestaciones."
    )

    recibe_auxilios = st.radio(
        "¿Recibes auxilios?",
        ["Sí", "No"],
        horizontal=True,
        help="Auxilios no salariales como conectividad, transporte u otros beneficios."
    )

    valor_auxilios_mensual = money_input(
        "¿Cuál es el valor mensual de tus auxilios?",
        value=2000000.0 if recibe_auxilios == "Sí" else 0.0,
        disabled=(recibe_auxilios == "No"),
        help_text="El valor mensual de auxilios no debería superar el 50% del salario.",
        key="valor_auxilios"
    )
    
    recibe_variable = st.radio(
        "¿Recibes comisiones o salario variable?",
        ["Sí", "No"],
        horizontal=True,
        help="Ingresos variables como comisiones, bonos comerciales o incentivos."
    )

with col2:
    st.markdown("### 📈 Variables")

    valor_variable_anual = money_input(
        "¿Cuál es el valor anual de tu variable o comisiones?",
        value=24000000.0 if recibe_variable == "Sí" else 0.0,
        disabled=(recibe_variable == "No"),
        help_text="Total anual de ingresos variables.",
        key="variable_anual"
    )

    tiene_bonificaciones = st.radio(
        "¿Tienes bonificaciones?",
        ["Sí", "No"],
        horizontal=True,
        help="Bonos adicionales otorgados por la empresa."
    )

    valor_bonificaciones = money_input(
        "¿Cuál es el valor de tus bonificaciones?",
        value=40000000.0 if tiene_bonificaciones == "Sí" else 0.0,
        disabled=(tiene_bonificaciones == "No"),
        help_text="Monto total anual de bonificaciones.",
        key="bonificaciones"
    )

    bono_salarial = st.radio(
        "¿Tu bono es salarial?",
        ["Sí", "No"],
        horizontal=True,
        help="Si el bono es salarial se incluyen aportes a seguridad social."
    )

with sep:
    st.markdown(
        """
        <div class="vertical-divider"></div>

        <style>
        .vertical-divider {
            width: 1px;
            height: 520px;
            margin: auto;
            background: linear-gradient(
                to bottom,
                rgba(255,255,255,0.05),
                rgba(96,165,250,0.45),
                rgba(255,255,255,0.05)
            );
        }

        /* Ocultar divisor en pantallas pequeñas */
        @media (max-width: 900px) {
            .vertical-divider {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown("### 🧾 Beneficios")

    aporte_voluntario_obligatorio_anual = money_input(
        "¿Cuánto aportas voluntariamente a tu fondo obligatorio?",
        value=15000000.0,
        help_text="Aportes voluntarios adicionales al fondo de pensiones.",
        key="aporte_voluntario"
    )

    numero_dependientes = st.number_input(
        "¿Cuántos dependientes tienes?",
        min_value=0,
        max_value=4,
        value=2,
        step=1,
        help="Personas que dependen económicamente de ti. Máximo permitido: 4."
    )

    intereses_vivienda_anual = money_input(
        "¿Cuánto pagas de intereses de vivienda al año?",
        value=4500000.0,
        help_text="Intereses pagados por crédito hipotecario.",
        key="intereses_vivienda"
    )

with col4:
    st.markdown("### 🏥 Deducciones")

    pagos_salud_anual = money_input(
        "¿Cuánto pagas en planes de salud al año?",
        value=6700000.0,
        help_text="Pagos por medicina prepagada o seguros de salud.",
        key="pagos_salud"
    )

    aportes_pension_afc_anual = money_input(
        "¿Cuánto aportas en pensión voluntaria o AFC?",
        value=1500000.0,
        help_text="Aportes voluntarios que generan beneficios tributarios.",
        key="afc"
    )

    compras_factura_electronica = money_input(
        "¿Cuánto estimas comprar con factura electrónica?",
        value=45000000.0,
        help_text="Compras con factura electrónica durante el año.",
        key="factura_electronica"
    )
st.divider()

# =========================
# Normalización de inputs
# =========================
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

# =========================
# Ejecutar simulación
# =========================
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

        c4, c5 = st.columns([1.3, 1])

        with c4:
            st.markdown("### Desglose del cálculo")

            df_detalle = pd.DataFrame(
                [
                    {"Concepto": "Salario anual", "Valor": formato_moneda(resultado["salario_anual"])},
                    {"Concepto": "Ingreso variable anual", "Valor": formato_moneda(resultado["ingreso_variable"])},
                    {"Concepto": "Auxilios anuales", "Valor": formato_moneda(resultado["auxilios_anuales"])},
                    {"Concepto": "Bonificación anual", "Valor": formato_moneda(resultado["bonificacion_anual"])},
                    {"Concepto": "Total ingresos", "Valor": formato_moneda(resultado["total_ingresos"])},
                    {"Concepto": "Aporte EPS", "Valor": formato_moneda(resultado["aporte_eps"])},
                    {"Concepto": "Aporte pensión", "Valor": formato_moneda(resultado["aporte_pension"])},
                    {"Concepto": "Fondo solidaridad", "Valor": formato_moneda(resultado["fondo_solidaridad"])},
                    {"Concepto": "Ingresos no constitutivos", "Valor": formato_moneda(resultado["ingresos_no_constitutivos"])},
                    {"Concepto": "Renta líquida", "Valor": formato_moneda(resultado["renta_liquida"])},
                    {"Concepto": "Renta líquida PAC", "Valor": formato_moneda(resultado["renta_liquida_pac"])},
                    {"Concepto": "Dependientes", "Valor": formato_moneda(resultado["dependientes"])},
                    {"Concepto": "Intereses vivienda", "Valor": formato_moneda(resultado["intereses_vivienda"])},
                    {"Concepto": "Pagos salud", "Valor": formato_moneda(resultado["pagos_salud"])},
                    {"Concepto": "Cesantías", "Valor": formato_moneda(resultado["cesantias"])},
                    {"Concepto": "Aportes pensión/AFC", "Valor": formato_moneda(resultado["aportes_pension_afc"])},
                    {"Concepto": "Renta exenta laboral", "Valor": formato_moneda(resultado["renta_exenta_laboral"])},
                    {"Concepto": "Total deducciones", "Valor": formato_moneda(resultado["total_deducciones"])},
                    {"Concepto": "Deducciones admisibles", "Valor": formato_moneda(resultado["deducciones_admisibles"])},
                    {"Concepto": "Base gravable", "Valor": formato_moneda(resultado["base_gravable"])},
                    {"Concepto": "Base gravable con PAC", "Valor": formato_moneda(resultado["base_gravable_pac"])},
                    {"Concepto": "Base gravable UVT", "Valor": formato_numero(resultado["base_uvt"], 6)},
                    {"Concepto": "Base gravable UVT con PAC", "Valor": formato_numero(resultado["base_uvt_pac"], 6)},
                ]
            )

            st.dataframe(df_detalle, use_container_width=True, hide_index=True)

        with c5:
            st.markdown("### Interpretación")
            st.success(
                f"Con base en la información registrada, el cliente podría obtener un beneficio tributario estimado de "
                f"{formato_moneda(resultado['beneficio'])}."
            )

        # =========================
        # Debug técnico
        # =========================
        if mostrar_debug:
            st.divider()
            st.markdown("## Debug técnico")

            st.markdown("### Valores calculados por la app")
            debug_df = pd.DataFrame(
                [
                    {"Variable": "salario_anual", "Valor app": resultado["salario_anual"]},
                    {"Variable": "ingreso_variable", "Valor app": resultado["ingreso_variable"]},
                    {"Variable": "auxilios_anuales", "Valor app": resultado["auxilios_anuales"]},
                    {"Variable": "bonificacion_anual", "Valor app": resultado["bonificacion_anual"]},
                    {"Variable": "total_ingresos", "Valor app": resultado["total_ingresos"]},
                    {"Variable": "aporte_eps", "Valor app": resultado["aporte_eps"]},
                    {"Variable": "aporte_pension", "Valor app": resultado["aporte_pension"]},
                    {"Variable": "fondo_solidaridad", "Valor app": resultado["fondo_solidaridad"]},
                    {"Variable": "ingresos_no_constitutivos", "Valor app": resultado["ingresos_no_constitutivos"]},
                    {"Variable": "renta_liquida", "Valor app": resultado["renta_liquida"]},
                    {"Variable": "renta_liquida_pac", "Valor app": resultado["renta_liquida_pac"]},
                    {"Variable": "dependientes", "Valor app": resultado["dependientes"]},
                    {"Variable": "intereses_vivienda", "Valor app": resultado["intereses_vivienda"]},
                    {"Variable": "pagos_salud", "Valor app": resultado["pagos_salud"]},
                    {"Variable": "cesantias", "Valor app": resultado["cesantias"]},
                    {"Variable": "aportes_pension_afc", "Valor app": resultado["aportes_pension_afc"]},
                    {"Variable": "renta_exenta_laboral", "Valor app": resultado["renta_exenta_laboral"]},
                    {"Variable": "total_deducciones", "Valor app": resultado["total_deducciones"]},
                    {"Variable": "deducciones_admisibles", "Valor app": resultado["deducciones_admisibles"]},
                    {"Variable": "base_gravable", "Valor app": resultado["base_gravable"]},
                    {"Variable": "base_gravable_pac", "Valor app": resultado["base_gravable_pac"]},
                    {"Variable": "base_uvt", "Valor app": resultado["base_uvt"]},
                    {"Variable": "base_uvt_pac", "Valor app": resultado["base_uvt_pac"]},
                    {"Variable": "impuesto_sin_optimizacion", "Valor app": resultado["impuesto_sin_optimizacion"]},
                    {"Variable": "impuesto_optimizado", "Valor app": resultado["impuesto_optimizado"]},
                    {"Variable": "beneficio", "Valor app": resultado["beneficio"]},
                ]
            )
            st.dataframe(debug_df, use_container_width=True, hide_index=True)

            st.markdown("### Valores esperados del Excel para el caso base")
            excel_base_df = pd.DataFrame(
                [
                    {"Variable": "salario_anual", "Valor Excel esperado": 300000000},
                    {"Variable": "ingreso_variable", "Valor Excel esperado": 24000000},
                    {"Variable": "auxilios_anuales", "Valor Excel esperado": 24000000},
                    {"Variable": "bonificacion_anual", "Valor Excel esperado": 40000000},
                    {"Variable": "total_ingresos", "Valor Excel esperado": 388000000},
                    {"Variable": "aporte_eps", "Valor Excel esperado": 9072000},
                    {"Variable": "aporte_pension", "Valor Excel esperado": 9072000},
                    {"Variable": "fondo_solidaridad", "Valor Excel esperado": 2268000},
                    {"Variable": "ingresos_no_constitutivos", "Valor Excel esperado": 35412000},
                    {"Variable": "renta_liquida", "Valor Excel esperado": 352588000},
                    {"Variable": "renta_liquida_pac", "Valor Excel esperado": 312588000},
                    {"Variable": "dependientes", "Valor Excel esperado": 20111616},
                    {"Variable": "intereses_vivienda", "Valor Excel esperado": 4500000},
                    {"Variable": "pagos_salud", "Valor Excel esperado": 6700000},
                    {"Variable": "cesantias", "Valor Excel esperado": 0},
                    {"Variable": "aportes_pension_afc", "Valor Excel esperado": 1500000},
                    {"Variable": "renta_exenta_laboral", "Valor Excel esperado": 41375460},
                    {"Variable": "total_deducciones", "Valor Excel esperado": 74187076},
                    {"Variable": "deducciones_admisibles", "Valor Excel esperado": 70181160},
                    {"Variable": "base_gravable", "Valor Excel esperado": 282406840},
                    {"Variable": "base_gravable_pac", "Valor Excel esperado": 242406840},
                    {"Variable": "base_uvt", "Valor Excel esperado": 5392.118990338718},
                    {"Variable": "base_uvt_pac", "Valor Excel esperado": 4628.381257876045},
                    {"Variable": "impuesto_sin_optimizacion", "Valor Excel esperado": 63602947.2},
                    {"Variable": "impuesto_optimizado", "Valor Excel esperado": 50402947.2},
                    {"Variable": "beneficio", "Valor Excel esperado": 13200000},
                ]
            )
            st.dataframe(excel_base_df, use_container_width=True, hide_index=True)

            st.markdown("### Comparación rápida")
            comparacion = {
                "impuesto_sin_optimizacion_app": resultado["impuesto_sin_optimizacion"],
                "impuesto_sin_optimizacion_excel": 63602947.2,
                "delta_impuesto_sin_optimizacion": resultado["impuesto_sin_optimizacion"] - 63602947.2,
                "impuesto_optimizado_app": resultado["impuesto_optimizado"],
                "impuesto_optimizado_excel": 50402947.2,
                "delta_impuesto_optimizado": resultado["impuesto_optimizado"] - 50402947.2,
                "beneficio_app": resultado["beneficio"],
                "beneficio_excel": 13200000,
                "delta_beneficio": resultado["beneficio"] - 13200000,
                "base_gravable_app": resultado["base_gravable"],
                "base_gravable_excel": 282406840,
                "delta_base_gravable": resultado["base_gravable"] - 282406840,
                "base_uvt_app": resultado["base_uvt"],
                "base_uvt_excel": 5392.118990338718,
                "delta_base_uvt": resultado["base_uvt"] - 5392.118990338718,
            }
            st.json(comparacion)

else:
    st.info("Completa los datos y pulsa **Calcular simulación**.")
