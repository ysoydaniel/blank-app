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
        background-color: #3f3f3f;
    }

    h1, h2, h3 {
        color: #f8fafc;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    p, label, div, span {
        color: #ffffff;
    }

    /* Glass cards base */
    .glass-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 12px 40px rgba(0,0,0,0.22);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 22px;
        padding: 20px;
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
        .vertical-divider { display: none; }
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
        outline: none !important;
    }

    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:hover {
        border: 1px solid rgba(52,211,153,0.45) !important;
        box-shadow: 0 0 0 2px rgba(52,211,153,0.10) !important;
    }

    /* Dropdown selectbox */
    div[data-baseweb="popover"] { background: transparent !important; }

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

    ul[role="listbox"] li {
        background: transparent !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    ul[role="listbox"] li:hover {
        background: rgba(52,211,153,0.12) !important;
    }

    ul[role="listbox"] li[aria-selected="true"] {
        background: rgba(52,211,153,0.18) !important;
        font-weight: 600 !important;
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

    div[role="radiogroup"] label * { color: #f8fafc !important; }
    input[type="radio"] { accent-color: #00c73d !important; }

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
        box-shadow: none;
        transition: all 0.25s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: none;
    }

    .stButton > button:active { transform: translateY(1px); }

    /* Money input */
    div[data-testid="stTextInput"] { position: relative; }

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
        outline: none !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border: 1px solid rgba(52,211,153,0.40) !important;
        box-shadow: 0 0 0 2px rgba(52,211,153,0.10) !important;
        outline: none !important;
    }

    /* Result cards: margen solo en mobile */
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

    @media (max-width: 768px) {
        .result-card { margin-bottom: 18px; }
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

def money_input(label, value=0, key=None, help_text=None, disabled=False):
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
    mostrar_debug = st.checkbox("Mostrar detalle técnico", value=False)
    st.caption("Úsalo para comparar contra el Excel y detectar diferencias.")

# Session state
st.session_state.setdefault("resultado_simulacion", None)
st.session_state.setdefault("inputs_simulacion", None)
st.session_state.setdefault("simulacion_calculada", False)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="soft-card" style="display:flex; align-items:center; gap:16px;">
    <img
        src="https://cdn-icons-png.flaticon.com/512/3861/3861512.png"
        style="height:48px;width:auto;border-radius:12px;"
    />
    <div>
        <div style="font-size:34px; color:#ffffff; font-weight:800; margin-top:6px;">
            Simulador Tributario 2026
        </div>
        <div style="font-size:16px; color:#d1fae5; margin-top:8px;">
            Experiencia web guiada, clara y lista para escalar.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# =========================
# FORMULARIO
# =========================
st.markdown("""
<div class="soft-card">
    <div style="font-size:13px; color:#86efac; font-weight:700; letter-spacing:.08em;">
        FORMULARIO
    </div>
    <div style="font-size:26px; color:#ffffff; font-weight:800; margin-top:6px;">
        Información del cliente
    </div>
    <div style="font-size:15px; color:#d1fae5; margin-top:8px;">
        Completa los datos de ingresos y beneficios tributarios para estimar el impuesto y el ahorro potencial.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

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

    recibe_auxilios = st.radio(
        "¿Recibes auxilios?",
        ["Sí", "No"],
        horizontal=True,
        help="Auxilios no salariales como transporte o conectividad."
    )

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
    st.markdown("<div class='vertical-divider'></div>", unsafe_allow_html=True)

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

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

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

# =========================
# RESULTADOS
# =========================
if st.session_state.simulacion_calculada and st.session_state.resultado_simulacion is not None:
    resultado = st.session_state.resultado_simulacion

    impuesto_original = resultado["impuesto_sin_optimizacion"]
    impuesto_optimizado = resultado["impuesto_optimizado"]
    beneficio = resultado["beneficio"]
    total_ingresos = resultado.get("total_ingresos", 0)
    base_gravable = resultado.get("base_gravable", 0)
    deducciones_admisibles = resultado.get("deducciones_admisibles", 0)

    porcentaje_ahorro = (beneficio / impuesto_original) if impuesto_original > 0 else 0

    eficiencia_actual = (impuesto_original / total_ingresos) if total_ingresos > 0 else 0
    eficiencia_optimizada = (impuesto_optimizado / total_ingresos) if total_ingresos > 0 else 0

    st.markdown("## Resultados")

    # =========================
    # HERO RESULT
    # =========================
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
            <div style="
                font-size:52px;
                font-weight:900;
                color:#ffffff;
                margin-top:6px;
                text-shadow:0 0 12px rgba(134,239,172,0.25);
            ">
                {formato_moneda(beneficio)}
            </div>
            <div style="font-size:14px;color:#d1fae5;margin-top:4px;">
                ahorro potencial estimado
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # CARDS PRINCIPALES
    # =========================
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
            title="Impuesto optimizado con PAC",
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

    # =========================
    # FLUJO DE DINERO + EFICIENCIA
    # =========================
    st.divider()
    st.markdown("## Vista ejecutiva")

    left_exec, right_exec = st.columns([1.25, 1])

    with left_exec:
        st.markdown("### Flujo del dinero")

        f1, f2, f3, f4 = st.columns([1, 0.15, 1, 0.15])

        with f1:
            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center;">
                    <div style="font-size:12px;color:#86efac;font-weight:700;letter-spacing:.06em;">INGRESOS</div>
                    <div style="font-size:16px;color:#d1fae5;margin-top:6px;">Total ingresos</div>
                    <div style="font-size:28px;color:#ffffff;font-weight:800;margin-top:8px;">
                        {formato_moneda(total_ingresos)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with f2:
            st.markdown(
                """
                <div style="display:flex;align-items:center;justify-content:center;height:100%;">
                    <div style="font-size:30px;color:#86efac;">→</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with f3:
            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center;">
                    <div style="font-size:12px;color:#86efac;font-weight:700;letter-spacing:.06em;">DEPURACIÓN</div>
                    <div style="font-size:16px;color:#d1fae5;margin-top:6px;">Deducciones admisibles</div>
                    <div style="font-size:28px;color:#ffffff;font-weight:800;margin-top:8px;">
                        {formato_moneda(deducciones_admisibles)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with f4:
            st.markdown(
                """
                <div style="display:flex;align-items:center;justify-content:center;height:100%;">
                    <div style="font-size:30px;color:#86efac;">→</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        f5, f6, f7 = st.columns([1, 0.15, 1])

        with f5:
            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center;">
                    <div style="font-size:12px;color:#86efac;font-weight:700;letter-spacing:.06em;">RESULTADO FISCAL</div>
                    <div style="font-size:16px;color:#d1fae5;margin-top:6px;">Base gravable</div>
                    <div style="font-size:28px;color:#ffffff;font-weight:800;margin-top:8px;">
                        {formato_moneda(base_gravable)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with f6:
            st.markdown(
                """
                <div style="display:flex;align-items:center;justify-content:center;height:100%;">
                    <div style="font-size:30px;color:#86efac;">→</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with f7:
            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center;">
                    <div style="font-size:12px;color:#86efac;font-weight:700;letter-spacing:.06em;">SALIDA</div>
                    <div style="font-size:16px;color:#d1fae5;margin-top:6px;">Impuesto actual</div>
                    <div style="font-size:28px;color:#ffffff;font-weight:800;margin-top:8px;">
                        {formato_moneda(impuesto_original)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with right_exec:
        st.markdown("### Eficiencia tributaria")

        e1, e2 = st.columns(2)

        with e1:
            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center;height:100%;">
                    <div style="font-size:12px;color:#fbbf24;font-weight:700;letter-spacing:.06em;">ANTES</div>
                    <div style="font-size:34px;color:#ffffff;font-weight:900;margin-top:10px;">
                        {eficiencia_actual:.1%}
                    </div>
                    <div style="font-size:13px;color:#d1fae5;margin-top:8px;">
                        carga tributaria sobre ingresos
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with e2:
            st.markdown(
                f"""
                <div class="soft-card" style="text-align:center;height:100%;">
                    <div style="font-size:12px;color:#86efac;font-weight:700;letter-spacing:.06em;">DESPUÉS</div>
                    <div style="font-size:34px;color:#ffffff;font-weight:900;margin-top:10px;">
                        {eficiencia_optimizada:.1%}
                    </div>
                    <div style="font-size:13px;color:#d1fae5;margin-top:8px;">
                        carga tributaria optimizada
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        delta_eficiencia = eficiencia_actual - eficiencia_optimizada

        st.markdown(
            f"""
            <div class="soft-card">
                <div style="font-size:13px;color:#86efac;font-weight:700;letter-spacing:.06em;text-transform:uppercase;">
                    Mejora relativa
                </div>
                <div style="font-size:30px;color:#ffffff;font-weight:900;margin-top:8px;">
                    {delta_eficiencia:.1%}
                </div>
                <div style="font-size:13px;color:#d1fae5;margin-top:8px;line-height:1.5;">
                    reducción estimada en la proporción de impuesto frente al ingreso total.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    

    # =========================
    # DESGLOSE + INTERPRETACIÓN (SIEMPRE DENTRO DEL IF PRINCIPAL)
    # =========================
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

    # =========================
    # SIMULACIÓN DINÁMICA + RECOMENDACIÓN  ✅ (YA DENTRO DEL IF PRINCIPAL)
    # =========================
    st.divider()
    st.markdown("## Simulación dinámica")

    topup_max = int(resultado.get("topup_full", 0))

    if topup_max > 0:
        sim_left, sim_right = st.columns([0.9, 1.4])

        # IZQUIERDA: slider + métricas
        with sim_left:
            st.markdown("### Ajuste del aporte")

            topup_usuario = st.slider(
                "Aporte adicional en pensión voluntaria / AFC",
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
            impuesto_topup = calcular_impuesto_renta(base_uvt_temp, resultado["uvt"])
            ahorro_topup = resultado["impuesto_sin_optimizacion"] - impuesto_topup

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tc1, tc2, tc3 = st.columns(3)
            with tc1:
                st.metric("Aporte adicional", formato_moneda(topup_usuario))
            with tc2:
                st.metric("Nuevo impuesto", formato_moneda(impuesto_topup))
            with tc3:
                st.metric("Ahorro", formato_moneda(ahorro_topup))

        # DERECHA: gráfica + recomendación
        with sim_right:
            st.markdown("### Trayectoria del ahorro")

            aportes = []
            ahorros = []

            step = topup_max / 30 if topup_max > 0 else 1

            for i in range(31):
                aporte = step * i
                base = resultado["base_gravable"] - aporte
                if base < 0:
                    base = 0

                base_uvt_temp = base / resultado["uvt"]
                impuesto_temp = calcular_impuesto_renta(base_uvt_temp, resultado["uvt"])
                ahorro_temp = resultado["impuesto_sin_optimizacion"] - impuesto_temp

                aportes.append(aporte)
                ahorros.append(ahorro_temp)

            max_ahorro = max(ahorros)
            idx_optimo = ahorros.index(max_ahorro)
            aporte_optimo = aportes[idx_optimo]
            ahorro_optimo = ahorros[idx_optimo]

            # a millones
            aportes_m = [x / 1_000_000 for x in aportes]
            ahorros_m = [y / 1_000_000 for y in ahorros]
            aporte_optimo_m = aporte_optimo / 1_000_000
            ahorro_optimo_m = ahorro_optimo / 1_000_000

            fig, ax = plt.subplots(figsize=(6.8, 2.5))
            fig.patch.set_alpha(0)
            ax.set_facecolor((0, 0, 0, 0))

            ax.plot(aportes_m, ahorros_m, linewidth=2.4)
            ax.fill_between(aportes_m, ahorros_m, alpha=0.06)
            ax.scatter([aporte_optimo_m], [ahorro_optimo_m], s=55, zorder=5)

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color((1, 1, 1, 0.18))
            ax.spines["bottom"].set_color((1, 1, 1, 0.18))

            ax.tick_params(axis="both", length=0, colors="white", labelsize=9)
            ax.grid(alpha=0.08)

            ax.set_xlabel("Aporte adicional (millones)", color="white", fontsize=9, labelpad=8)
            ax.set_ylabel("Ahorro (millones)", color="white", fontsize=9, labelpad=8)

            st.pyplot(fig, use_container_width=True)

            st.caption(
                f"Punto óptimo estimado: {formato_moneda(aporte_optimo)} "
                f"para un ahorro cercano a {formato_moneda(ahorro_optimo)}."
            )

            st.markdown("### Recomendación sugerida")

            rc1, rc2 = st.columns([1.15, 1])

            with rc1:
                st.markdown(
                    f"""
                    <div class="soft-card" style="
                        padding:22px 24px;
                        background:linear-gradient(135deg,rgba(0,199,61,0.14),rgba(124,224,0,0.06));
                        border:1px solid rgba(0,199,61,0.18);
                    ">
                        <div style="font-size:13px;color:#86efac;font-weight:700;letter-spacing:.08em;">
                            APORTE ÓPTIMO ESTIMADO
                        </div>
                        <div style="font-size:40px;font-weight:900;color:#ffffff;margin-top:6px;">
                            {formato_moneda(aporte_optimo)}
                        </div>
                        <div style="font-size:14px;color:#d1fae5;margin-top:4px;">
                            aporte adicional recomendado
                        </div>
                        <div style="
                            margin-top:14px;
                            padding:12px 14px;
                            border-radius:14px;
                            background:rgba(255,255,255,0.06);
                            border:1px solid rgba(255,255,255,0.10);
                        ">
                            <div style="font-size:13px;color:#86efac;font-weight:700;">
                                Ahorro estimado asociado
                            </div>
                            <div style="font-size:28px;font-weight:800;color:#ffffff;margin-top:2px;">
                                {formato_moneda(ahorro_optimo)}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with rc2:
                st.markdown(
                    f"""
                    <div class="soft-card" style="height:100%;">
                        <div style="font-size:13px;color:#86efac;font-weight:700;letter-spacing:.08em;">
                            LECTURA EJECUTIVA
                        </div>
                        <div style="font-size:15px;color:#ffffff;font-weight:700;margin-top:10px;">
                            Estrategia sugerida
                        </div>
                        <div style="font-size:14px;color:#d1fae5;line-height:1.65;margin-top:10px;">
                            El comportamiento de la simulación sugiere que un aporte cercano a
                            <b>{formato_moneda(aporte_optimo)}</b> podría llevar al cliente a un punto de
                            mayor eficiencia tributaria, generando un ahorro aproximado de
                            <b>{formato_moneda(ahorro_optimo)}</b>.
                            <br><br>
                            Esta recomendación debe validarse dentro del contexto financiero completo del cliente.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("El cliente ya se encuentra en el máximo beneficio tributario permitido.")

    # =========================
    # DEBUG TÉCNICO (solo si checkbox)
    # =========================
    if mostrar_debug:
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

        with st.expander("🔧 Debug técnico"):
            st.dataframe(debug_df, use_container_width=True, hide_index=True)

else:
    st.info("Completa los datos y pulsa **Calcular simulación**.")
