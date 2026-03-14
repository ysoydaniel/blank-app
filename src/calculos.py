import math

UVT = 52374
SMLV = 1750905
MINIMO_INT = 22761765
SALARIO_TOPE = SMLV * 25  # 43.772.625

TRAMOS_RENTA = [
    {"desde": 0, "hasta": 1090, "tarifa": 0.00, "base": 0},
    {"desde": 1090, "hasta": 1700, "tarifa": 0.19, "base": 0},
    {"desde": 1700, "hasta": 4100, "tarifa": 0.28, "base": 116},
    {"desde": 4100, "hasta": 8670, "tarifa": 0.33, "base": 788},
    {"desde": 8670, "hasta": 18970, "tarifa": 0.35, "base": 2296},
    {"desde": 18970, "hasta": 31000, "tarifa": 0.37, "base": 5901},
    {"desde": 31000, "hasta": None, "tarifa": 0.39, "base": 10352},
]

TABLA_FSP = [
    {"desde": 0, "hasta": 6986110.95 * 12, "tarifa": 0.00},
    {"desde": 7003620 * 12, "hasta": 27996970.95 * 12, "tarifa": 0.01},
    {"desde": 28014480 * 12, "hasta": 29747875.95 * 12, "tarifa": 0.012},
    {"desde": 29765385 * 12, "hasta": 31498780.95 * 12, "tarifa": 0.014},
    {"desde": 31516290 * 12, "hasta": 33249685.95 * 12, "tarifa": 0.016},
    {"desde": 33267195 * 12, "hasta": 35000590.95 * 12, "tarifa": 0.018},
    {"desde": 35018100 * 12, "hasta": None, "tarifa": 0.02},
]


# =========================
# IMPUESTO
# =========================

def calcular_impuesto_renta(base_uvt: float, uvt: float) -> float:

    for tramo in TRAMOS_RENTA:

        desde = tramo["desde"]
        hasta = tramo["hasta"]
        tarifa = tramo["tarifa"]
        base = tramo["base"]

        if hasta is None:
            if base_uvt >= desde:
                return (((base_uvt - desde) * tarifa) + base) * uvt

        else:
            if desde <= base_uvt < hasta:
                return (((base_uvt - desde) * tarifa) + base) * uvt

    return 0.0


# =========================
# TOP UP
# =========================

def calcular_topup_full(
    ingreso_anual,
    aportes_actuales,
    uvt
):

    limite_porcentaje = ingreso_anual * 0.30
    limite_uvt = 3800 * uvt

    max_aporte = min(limite_porcentaje, limite_uvt)

    topup = max_aporte - aportes_actuales

    return max(topup, 0)


# =========================
# SIMULADOR
# =========================

def ejecutar_simulador(inputs):

    salario_mensual = inputs["salario_mensual"]
    tipo_salario = inputs["tipo_salario"]

    auxilios = inputs["valor_auxilios_mensual"] * 12
    variable = inputs["valor_variable_anual"]
    bonificaciones = inputs["valor_bonificaciones"]

    aportes_voluntarios = inputs["aportes_pension_afc_anual"]

    # =========================
    # INGRESOS
    # =========================

    salario_anual = salario_mensual * 12

    total_ingresos = (
        salario_anual +
        auxilios +
        variable +
        bonificaciones
    )

    # =========================
    # SEGURIDAD SOCIAL
    # =========================

    base_ss = min(salario_mensual, 25 * UVT)

    aporte_eps = base_ss * 0.04 * 12
    aporte_pension = base_ss * 0.04 * 12

    ingresos_no_constitutivos = (
        aporte_eps +
        aporte_pension
    )

    # =========================
    # RENTA LIQUIDA
    # =========================

    renta_liquida = total_ingresos - ingresos_no_constitutivos

    # =========================
    # DEDUCCIONES
    # =========================

    dependientes = min(inputs["numero_dependientes"] * 0.10 * renta_liquida, 72 * UVT)

    intereses_vivienda = min(inputs["intereses_vivienda_anual"], 100 * UVT)

    pagos_salud = min(inputs["pagos_salud_anual"], 192 * UVT)

    deducciones = (
        dependientes +
        intereses_vivienda +
        pagos_salud +
        aportes_voluntarios
    )

    deducciones_admisibles = min(deducciones, renta_liquida * 0.40)

    # =========================
    # BASE GRAVABLE
    # =========================

    base_gravable = renta_liquida - deducciones_admisibles

    base_uvt = base_gravable / UVT

    impuesto = calcular_impuesto_renta(base_uvt, UVT)

    # =========================
    # TOP UP FULL
    # =========================

    topup_full = calcular_topup_full(
        ingreso_anual=total_ingresos,
        aportes_actuales=aportes_voluntarios,
        uvt=UVT
    )

    base_gravable_topup = base_gravable - topup_full

    base_uvt_topup = base_gravable_topup / UVT

    impuesto_topup = calcular_impuesto_renta(base_uvt_topup, UVT)

    beneficio = impuesto - impuesto_topup

    # =========================
    # RESULTADO
    # =========================

    return {

        "uvt": UVT,

        "salario_anual": salario_anual,
        "ingreso_variable": variable,
        "auxilios_anuales": auxilios,
        "bonificacion_anual": bonificaciones,

        "total_ingresos": total_ingresos,

        "aporte_eps": aporte_eps,
        "aporte_pension": aporte_pension,

        "ingresos_no_constitutivos": ingresos_no_constitutivos,

        "renta_liquida": renta_liquida,

        "dependientes": dependientes,
        "intereses_vivienda": intereses_vivienda,
        "pagos_salud": pagos_salud,

        "total_deducciones": deducciones,
        "deducciones_admisibles": deducciones_admisibles,

        "base_gravable": base_gravable,

        "base_uvt": base_uvt,

        "impuesto_sin_optimizacion": impuesto,

        "topup_full": topup_full,
        "impuesto_topup": impuesto_topup,

        "beneficio": beneficio
    }
