import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.calculos import ejecutar_simulador, calcular_impuesto_renta
from src.formateo import formato_moneda, formato_numero

st.set_page_config(
    page_title="Simulador Tributario 2026",
    page_icon="🧮",
    layout="wide"
)

# =========================
# ESTILOS - GLASSMORPHISM
# =========================
st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 15% 20%, rgba(0, 199, 61, 0.18), transparent 28%),
            radial-gradient(circle at 85% 18%, rgba(124, 224, 0, 0.14), transparent 24%),
            radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.10), transparent 24%),
            linear-gradient(135deg, #0b1110 0%, #101a17 42%, #0d1418 100%);
        color: #ecfdf5;
    }

    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    p, label, div, span {
        color: #d1fae5;
    }

    /* Glass cards base */
    .glass-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 12px 40px rgba(0,0,0,0.22);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .soft-card {
        padding: 20px;
        border-radius: 22px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 12px 40px rgba(0,0,0,0.22);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .section-divider {
        margin: 12px 0 20px 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(52,211,153,0.35), transparent);
    }

    .vertical-divider {
        width: 1px;
        height: 540px;
        margin: auto;
        background: linear-gradient(
            to bottom,
            rgba(255,255,255,0.03),
            rgba(52,211,153,0.35),
            rgba(255,255,255,0.03)
        );
    }

    @media (max-width: 900px) {
        .vertical-divider {
            display: none;
        }
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(10, 17, 16, 0.82);
        border-right: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 16px !important;
        min-height: 48px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="select"] span {
        color: #f8fafc !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:hover {
        border: 1px solid rgba(52,211,153,0.45) !important;
        box-shadow: 0 0 0 2px rgba(52,211,153,0.10) !important;
    }

    /* Dropdown selectbox */
    div[data-baseweb="popover"] {
        background: transparent !important;
    }

    div[data-baseweb="menu"] {
        background: rgba(15,23,42,0.92) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 16px !important;
        box-shadow: 0 18px 40px rgba(0,0,0,0.28) !important;
        overflow: hidden !important;
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }

    ul[role="listbox"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 6px !important;
    }

    ul[role="listbox"] li,
    div[role="option"] {
        background: transparent !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    ul[role="listbox"] li:hover,
    div[role="option"]:hover {
        background: rgba(52,211,153,0.12) !important;
        color: #f8fafc !important;
    }

    ul[role="listbox"] li[aria-selected="true"],
    div[role="option"][aria-selected="true"] {
        background: rgba(52,211,153,0.18) !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
    }

    ul[role="listbox"] *,
    div[data-baseweb="menu"] *,
    div[role="option"] * {
        color: #f8fafc !important;
    }

    /* Radio buttons */
    div[role="radiogroup"] label {
        background: rgba(255,255,255,0.07) !important;
        padding: 8px 14px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        margin-right: 8px !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    div[role="radiogroup"] label * {
        color: #f8fafc !important;
    }

    input[type="radio"] {
        accent-color: #00c73d !important;
    }

    /* Toggle */
button[kind="secondaryFormSubmit"],
div[data-testid="stToggle"] label {
    color: #f8fafc !important;
}

div[data-testid="stToggle"] {
    padding-top: 2px;
    padding-bottom: 6px;
}

    /* Botón principal */
    .stButton > button {
        width: 100%;
        max-width: 340px;
        margin: 0 auto;
        display: block;
        background: linear-gradient(135deg, #00c73d 0%, #7ce000 100%);
        color: white;
        border-radius: 16px;
        border: none;
        padding: 0.95rem 1.2rem;
        font-weight: 700;
        box-shadow:
            0 12px 30px rgba(0,199,61,0.30),
            0 0 24px rgba(124,224,0,0.14);
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow:
            0 18px 40px rgba(0,199,61,0.36),
            0 0 28px rgba(124,224,0,0.18);
    }

    .stButton > button:active {
        transform: translateY(1px);
    }

    /* Money input */
    div[data-testid="stTextInput"] {
        position: relative;
    }

    div[data-testid="stTextInput"]::before {
        content: "$";
        position: absolute;
        left: 12px;
        top: 35px;
        color: rgba(255,255,255,0.65);
        font-weight: 700;
        font-size: 15px;
        z-index: 1;
    }

    div[data-testid="stTextInput"] input {
        padding-left: 26px !important;
        background: rgba(255,255,255,0.07) !important;
        border-radius: 16px !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.10) !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border: 1px solid rgba(52,211,153,0.40) !important;
        box-shadow: 0 0 0 2px rgba(52,211,153,0.10) !important;
        outline: none !important;
    }

    /* Result cards */
    .result-card {
        border-radius: 22px;
        padding: 22px 24px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 14px 40px rgba(0,0,0,0.18);
        min-height: 150px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .result-label {
        font-size: 14px;
        color: #cbd5e1;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .result-value {
        font-size: 40px;
        line-height: 1.05;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 10px;
    }

    .result-subtext {
        font-size: 13px;
        color: #cbd5e1;
        line-height: 1.4;
    }

    .result-card.primary {
        background: linear-gradient(135deg, rgba(0,199,61,0.13), rgba(124,224,0,0.06));
        border: 1px solid rgba(0,199,61,0.18);
    }

    .result-card.success {
        background: linear-gradient(135deg, rgba(16,185,129,0.14), rgba(16,185,129,0.06));
        border: 1px solid rgba(16,185,129,0.18);
    }

    .result-card.warning {
        background: linear-gradient(135deg, rgba(245,158,11,0.14), rgba(245,158,11,0.06));
        border: 1px solid rgba(245,158,11,0.18);
    }

    .result-mini {
        font-size: 12px;
        color: #86efac;
        font-weight: 700;
        letter-spacing: .06em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 8px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def _format_money_state(key: str):
    valor = st.session_state.get(key, "")
    solo_numeros = re.sub(r"[^\d]", "", valor)

    if solo_numeros == "":
        st.session_state[key] = ""
        return

    numero = int(solo_numeros)
    st.session_state[key] = f"{numero:,}".replace(",", ".")


def money_input(
    label,
    value=0,
    key=None,
    help_text=None,
    disabled=False
):
    if key not in st.session_state:
        st.session_state[key] = f"{int(value):,}".replace(",", ".")

    st.text_input(
        label,
        key=key,
        help=help_text,
        disabled=disabled,
        on_change=_format_money_state,
        args=(key,)
    )

    valor = re.sub(r"[^\d]", "", st.session_state.get(key, ""))
    return float(valor) if valor else 0.0


def result_card(title: str, value: str, subtitle: str = "", tone: str = "primary", eyebrow: str = ""):
    st.markdown(
        f"""
        <div class="result-card {tone}">
            {f'<div class="result-mini">{eyebrow}</div>' if eyebrow else ''}
            <div class="result-label">{title}</div>
            <div class="result-value">{value}</div>
            {f'<div class="result-subtext">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## Configuración")
    mostrar_debug = st.checkbox("Mostrar detalle técnico", value=True)
    st.caption("Úsalo para comparar contra el Excel y detectar diferencias.")

if "resultado_simulacion" not in st.session_state:
    st.session_state.resultado_simulacion = None

if "inputs_simulacion" not in st.session_state:
    st.session_state.inputs_simulacion = None

if "simulacion_calculada" not in st.session_state:
    st.session_state.simulacion_calculada = False

# =========================
# HEADER
# =========================
st.markdown("""
<div class="soft-card" style="margin-bottom:18px;">
    <div style="font-size:13px;color:#86efac;font-weight:700;letter-spacing:.08em;">
        SIMULADOR TRIBUTARIO • GLASS UI
    </div>
    <div style="font-size:34px; color:#ffffff; font-weight:800; margin-top:6px;">
        🧮 Simulador Tributario 2026
    </div>
    <div style="font-size:16px; color:#d1fae5; margin-top:8px;">
        Convierte un modelo en Excel en una experiencia web guiada, clara y lista para escalar.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# FORMULARIO
# =========================
st.markdown("""
<div class="soft-card">
    <div style="font-size: 13px; color: #86efac; font-weight: 700; letter-spacing: .08em;">
        FORMULARIO
    </div>
    <div style="font-size: 26px; color: #ffffff; font-weight: 800; margin-top: 6px;">
        Información del cliente
    </div>
    <div style="font-size: 15px; color: #d1fae5; margin-top: 8px;">
        Completa los datos de ingresos y beneficios tributarios para estimar el impuesto y el ahorro potencial.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

col1, col2, sep, col3, col4 = st.columns([1, 1, 0.05, 1, 1])

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

    recibe_auxilios_bool = st.toggle(
    "¿Recibes auxilios?",
    value=True,
    help="Auxilios no salariales como transporte o conectividad."
    )
    recibe_auxilios = "Sí" if recibe_auxilios_bool else "No"

    valor_auxilios_mensual = money_input(
        "¿Cuál es el valor mensual de tus auxilios?",
        value=2000000 if recibe_auxilios == "Sí" else 0,
        help_text="Monto mensual de auxilios no salariales. No debería superar el 50% del salario.",
        disabled=(recibe_auxilios == "No"),
        key="valor_auxilios"
    )

with col2:
    st.markdown("### 📈 Variables")

    recibe_variable = st.radio(
        "¿Recibes comisiones o salario variable?",
        ["Sí", "No"],
        horizontal=True,
        help="Ingresos variables como comisiones o incentivos."
    )

    valor_variable_anual = money_input(
        "¿Cuál es el valor anual de tu variable o comisiones?",
        value=24000000 if recibe_variable == "Sí" else 0,
        help_text="Total anual de ingresos variables.",
        disabled=(recibe_variable == "No"),
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
        value=40000000 if tiene_bonificaciones == "Sí" else 0,
        help_text="Monto total anual de bonificaciones recibidas.",
        disabled=(tiene_bonificaciones == "No"),
        key="bonificaciones"
    )

    bono_salarial = st.radio(
        "¿Tu bono es salarial?",
        ["Sí", "No"],
        horizontal=True,
        help="Si el bono es salarial se incluyen aportes a seguridad social."
    )

with sep:
    st.markdown('<div class="vertical-divider"></div>', unsafe_allow_html=True)

with col3:
    st.markdown("### 🧾 Beneficios")

    aporte_voluntario_obligatorio_anual = money_input(
        "¿Cuánto aportas voluntariamente a tu fondo obligatorio?",
        value=15000000,
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
        value=4500000,
        help_text="Intereses pagados por crédito hipotecario.",
        key="intereses_vivienda"
    )

with col4:
    st.markdown("### 🏥 Deducciones")

    pagos_salud_anual = money_input(
        "¿Cuánto pagas en planes de salud al año?",
        value=6700000,
        help_text="Pagos por medicina prepagada o seguros de salud.",
        key="pagos_salud"
    )

    aportes_pension_afc_anual = money_input(
        "¿Cuánto aportas en pensión voluntaria o AFC?",
        value=1500000,
        help_text="Aportes voluntarios que pueden generar beneficios tributarios.",
        key="afc"
    )

    compras_factura_electronica = money_input(
        "¿Cuánto estimas comprar con factura electrónica?",
        value=45000000,
        help_text="Compras realizadas con factura electrónica durante el año. Actualmente no impacta el cálculo base.",
        key="factura_electronica"
    )

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =========================
# NORMALIZACIÓN
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
# EJECUCIÓN
# =========================
if st.button("Calcular simulación", use_container_width=True):
    if errores:
        for error in errores:
            st.error(error)
    else:
        st.session_state.resultado_simulacion = ejecutar_simulador(inputs)
        st.session_state.inputs_simulacion = inputs.copy()
        st.session_state.simulacion_calculada = True

if st.session_state.simulacion_calculada and st.session_state.resultado_simulacion is not None:
    resultado = st.session_state.resultado_simulacion

    impuesto_original = resultado["impuesto_sin_optimizacion"]
    impuesto_optimizado = resultado["impuesto_optimizado"]
    beneficio = resultado["beneficio"]

    porcentaje_ahorro = 0
    if impuesto_original > 0:
        porcentaje_ahorro = beneficio / impuesto_original

    st.markdown("## Resultados")

    st.markdown(
        f"""
        <div class="soft-card" style="
            padding:26px;
            text-align:center;
            margin-bottom:18px;
            background:linear-gradient(135deg,rgba(16,185,129,0.14),rgba(16,185,129,0.06));
            border:1px solid rgba(16,185,129,0.18);
        ">
            <div style="font-size:13px;color:#86efac;font-weight:700;letter-spacing:.08em;">
                OPORTUNIDAD TRIBUTARIA DETECTADA
            </div>
            <div style="font-size:46px;font-weight:900;color:#ffffff;margin-top:6px;">
                {formato_moneda(beneficio)}
            </div>
            <div style="font-size:14px;color:#d1fae5;margin-top:4px;">
                ahorro potencial estimado
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        result_card(
            title="Impuesto actual",
            value=formato_moneda(impuesto_original),
            subtitle="Escenario sin optimización tributaria.",
            tone="warning",
            eyebrow="Escenario base"
        )

    with c2:
        result_card(
            title="Impuesto optimizado",
            value=formato_moneda(impuesto_optimizado),
            subtitle="Escenario con beneficios tributarios aplicados.",
            tone="primary",
            eyebrow="Escenario optimizado"
        )

    with c3:
        result_card(
            title="Ahorro estimado",
            value=formato_moneda(beneficio),
            subtitle=f"Reducción aproximada del {porcentaje_ahorro:.1%} sobre el impuesto.",
            tone="success",
            eyebrow="Impacto"
        )

    st.markdown("### Comparación visual")

    max_valor = max(impuesto_original, impuesto_optimizado)
    porcentaje_actual = impuesto_original / max_valor if max_valor > 0 else 0
    porcentaje_opt = impuesto_optimizado / max_valor if max_valor > 0 else 0

    st.markdown("**Escenario actual**")
    st.progress(porcentaje_actual)
    st.caption(formato_moneda(impuesto_original))

    st.markdown("**Escenario optimizado**")
    st.progress(porcentaje_opt)
    st.caption(formato_moneda(impuesto_optimizado))

    st.markdown("### Impacto de la optimización tributaria")
    st.progress(min(max(porcentaje_ahorro, 0), 1))

    st.markdown(
        f"""
        <div class="soft-card" style="
            margin-top:10px;
            padding:16px 18px;
            background:rgba(16,185,129,0.08);
            border:1px solid rgba(16,185,129,0.18);
        ">
            <div style="font-size:14px; color:#86efac; font-weight:700;">
                💰 Ahorro potencial identificado
            </div>
            <div style="font-size:13px; color:#d1fae5; margin-top:6px;">
                El cliente podría reducir su carga tributaria en <b>{formato_moneda(beneficio)}</b>,
                equivalente a una mejora aproximada del <b>{porcentaje_ahorro:.1%}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if porcentaje_ahorro >= 0.20:
        st.success("🚀 Excelente oportunidad de optimización tributaria.")
    elif porcentaje_ahorro >= 0.10:
        st.info("📊 Hay una oportunidad tributaria relevante para el cliente.")
    else:
        st.warning("💡 El beneficio existe, pero el impacto es más moderado.")

    st.divider()
    st.markdown("## Simulación interactiva de optimización")

    topup_max = int(resultado.get("topup_full", 0))

    if topup_max > 0:
        topup_usuario = st.slider(
            "Simula cuánto más podría aportar el cliente en pensión voluntaria / AFC",
            min_value=0,
            max_value=topup_max,
            value=0,
            step=500000,
            help="Mueve el control para ver cómo cambia el impuesto.",
            key="slider_topup"
        )

        nueva_base = resultado["base_gravable"] - topup_usuario
        if nueva_base < 0:
            nueva_base = 0

        base_uvt_temp = nueva_base / resultado["uvt"]

        impuesto_topup = calcular_impuesto_renta(
            base_uvt_temp,
            resultado["uvt"]
        )

        ahorro_topup = resultado["impuesto_sin_optimizacion"] - impuesto_topup

        tc1, tc2, tc3 = st.columns(3)

        with tc1:
            st.metric("Aporte adicional", formato_moneda(topup_usuario))

        with tc2:
            st.metric("Nuevo impuesto estimado", formato_moneda(impuesto_topup))

        with tc3:
            st.metric("Ahorro tributario", formato_moneda(ahorro_topup))

        st.markdown("### Curva de optimización tributaria")

        aportes = []
        ahorros = []

        step = topup_max / 10 if topup_max > 0 else 1

        for i in range(11):
            aporte = step * i
            base = resultado["base_gravable"] - aporte

            if base < 0:
                base = 0

            base_uvt_temp = base / resultado["uvt"]

            impuesto_temp = calcular_impuesto_renta(
                base_uvt_temp,
                resultado["uvt"]
            )

            ahorro_temp = resultado["impuesto_sin_optimizacion"] - impuesto_temp

            aportes.append(aporte)
            ahorros.append(ahorro_temp)

        fig, ax = plt.subplots()
        ax.plot(aportes, ahorros)
        ax.set_xlabel("Aporte adicional")
        ax.set_ylabel("Ahorro tributario")
        st.pyplot(fig)

    else:
        st.info("El cliente ya se encuentra en el máximo beneficio tributario permitido.")

    st.divider()

    left, right = st.columns([1.35, 1])

    with left:
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

    with right:
        st.markdown("### Interpretación")
        st.markdown(
            f"""
            <div class="soft-card">
                <div style="font-size:13px; color:#86efac; font-weight:700; letter-spacing:.06em; text-transform:uppercase; margin-bottom:8px;">
                    Lectura ejecutiva
                </div>
                <div style="font-size:16px; color:#ffffff; font-weight:700; margin-bottom:10px;">
                    Beneficio tributario estimado
                </div>
                <div style="font-size:28px; color:#86efac; font-weight:800; margin-bottom:12px;">
                    {formato_moneda(resultado["beneficio"])}
                </div>
                <div style="font-size:14px; color:#d1fae5; line-height:1.55;">
                    Con base en la información registrada, el cliente podría reducir su carga tributaria
                    aprovechando beneficios permitidos en el modelo actual.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="soft-card">
                <div style="font-size:14px; color:#d1fae5; margin-bottom:8px;">Comparativo rápido</div>
                <div style="font-size:14px; color:#cbd5e1;">Antes</div>
                <div style="font-size:22px; color:#ffffff; font-weight:800; margin-bottom:10px;">
                    {formato_moneda(impuesto_original)}
                </div>
                <div style="font-size:14px; color:#cbd5e1;">Después</div>
                <div style="font-size:22px; color:#ffffff; font-weight:800;">
                    {formato_moneda(impuesto_optimizado)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if mostrar_debug:
        st.divider()
        st.markdown("## Debug técnico")

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
                {"Variable": "topup_full", "Valor app": resultado.get("topup_full", 0)},
                {"Variable": "impuesto_topup_full", "Valor app": resultado.get("impuesto_topup_full", 0)},
            ]
        )

        st.dataframe(debug_df, use_container_width=True, hide_index=True)

else:
    st.info("Completa los datos y pulsa **Calcular simulación**.")
