UVT = 52374
SMLV = 1750905
SALARIO_TOPE = SMLV * 25

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


def calcular_salario_anual(salario_mensual: float, tipo_salario: str) -> float:
    # Se replica la lógica identificada en el Excel analizado
    if tipo_salario == "Integral":
        return salario_mensual * 12
    return salario_mensual * 14.12


def calcular_ingreso_variable(valor_variable_anual: float) -> float:
    return valor_variable_anual


def calcular_auxilios_anuales(valor_auxilios_mensual: float) -> float:
    return valor_auxilios_mensual * 12


def calcular_bonificacion_anual(valor_bonificaciones: float) -> float:
    return valor_bonificaciones


def calcular_total_ingresos(
    salario_anual: float,
    ingreso_variable: float,
    auxilios_anuales: float,
    bonificacion_anual: float,
) -> float:
    return salario_anual + ingreso_variable + auxilios_anuales + bonificacion_anual


Pensado durante 1m 37s

Buenísimo, el CSV ya cantó.

Dónde está el error

Las primeras variables que se desvían son estas:

aporte_eps: app 10.192.000 vs Excel 9.072.000

aporte_pension: app 10.192.000 vs Excel 9.072.000

Luego todo lo demás se corre en cascada:

ingresos_no_constitutivos: +2.240.000

renta_liquida: -2.240.000

base_gravable: -2.240.000

impuesto: -739.200

O sea: el problema nace antes del impuesto, exactamente en el cálculo de seguridad social.

Qué sí coincide

total_ingresos

fondo_solidaridad

Así que el bug está en una de estas dos funciones:

calcular_base_seguridad_social(...)

calcular_aporte_eps(...)

Lo que debería pasar en tu caso base

Con:

salario anual = 300.000.000

variable anual = 24.000.000

tipo salario = Integral

La base correcta de seguridad social debe ser:

(300000000 + 24000000) * 0.70 = 226800000

Y por tanto:

EPS = 226800000 * 0.04 = 9072000
Pensión = 9072000

Tu app está sacando 10.192.000, así que está usando una base de aprox. 254.800.000.

Ese número no corresponde al Excel. Ahí está el duende con corbata.

Ajuste recomendado en src/calculos.py

Revisa y deja exactamente así estas funciones:

def calcular_base_seguridad_social(
    salario_anual: float,
    ingreso_variable: float,
    tipo_salario: str,
) -> float:
    # Según el Excel:
    # Integral -> (salario_anual + ingreso_variable) * 70%
    # Ordinario -> salario_anual + ingreso_variable
    if tipo_salario == "Integral":
        return (salario_anual + ingreso_variable) * 0.70

    return salario_anual + ingreso_variable



def calcular_base_seguridad_social_bono(
    bonificacion_anual: float,
    tipo_salario: str,
    bono_salarial: str,
) -> float:
    if bono_salarial != "Sí":
        return 0.0

    if tipo_salario == "Integral":
        return bonificacion_anual * 0.70

    return bonificacion_anual


def calcular_aporte_eps(
    base_seg_social: float,
    base_bono: float,
) -> float:
    # Replica el comportamiento del Excel para tu caso base
    # EPS = 4% de la base de seguridad social + 4% de la base del bono salarial
    return (base_seg_social * 0.04) + (base_bono * 0.04)


def calcular_aporte_pension(aporte_eps: float) -> float:
    return aporte_eps


def calcular_fondo_solidaridad(base_seg_social: float, tabla_fsp: list[dict]) -> float:
    for tramo in tabla_fsp:
        desde = tramo["desde"]
        hasta = tramo["hasta"]
        tarifa = tramo["tarifa"]

        if hasta is None:
            if base_seg_social >= desde:
                return base_seg_social * tarifa
        else:
            if desde <= base_seg_social < hasta:
                return base_seg_social * tarifa

    return 0.0


def calcular_ingresos_no_constitutivos(
    aporte_eps: float,
    aporte_pension: float,
    fondo_solidaridad: float,
    aporte_voluntario_obligatorio: float,
) -> float:
    return aporte_eps + aporte_pension + fondo_solidaridad + aporte_voluntario_obligatorio


def calcular_renta_liquida(
    total_ingresos: float,
    ingresos_no_constitutivos: float,
) -> float:
    return total_ingresos - ingresos_no_constitutivos


def calcular_renta_liquida_con_pac(
    total_ingresos: float,
    bonificacion_anual: float,
    ingresos_no_constitutivos: float,
) -> float:
    return total_ingresos - bonificacion_anual - ingresos_no_constitutivos


def calcular_maximo_beneficio_ley_2277(uvt: float) -> float:
    return uvt * 1340


def calcular_dependientes(
    numero_dependientes: int,
    salario_mensual: float,
    uvt: float,
) -> float:
    if numero_dependientes == 0:
        return 0.0

    tope_mensual = uvt * 32

    # Replica la fórmula observada en el Excel
    if salario_mensual * 0.10 > tope_mensual:
        return tope_mensual * 12

    return salario_mensual * 12


def calcular_intereses_vivienda(intereses_vivienda_anual: float) -> float:
    return intereses_vivienda_anual


def calcular_pagos_salud(pagos_salud_anual: float) -> float:
    return pagos_salud_anual


def calcular_cesantias(salario_mensual: float, tipo_salario: str) -> float:
    if tipo_salario == "Integral":
        return 0.0
    return salario_mensual


def calcular_aportes_pension_voluntaria_afc(aportes_pension_afc_anual: float) -> float:
    return aportes_pension_afc_anual


def calcular_renta_exenta_sin_limite(
    renta_liquida: float,
    dependientes: float,
    intereses_vivienda: float,
    pagos_salud: float,
    cesantias: float,
    aportes_pension_afc: float,
) -> float:
    base = renta_liquida - dependientes - intereses_vivienda - pagos_salud - cesantias - aportes_pension_afc
    return base * 0.25


def calcular_renta_exenta_laboral(renta_exenta_sin_limite: float, uvt: float) -> float:
    tope = uvt * 790
    return min(renta_exenta_sin_limite, tope)


def calcular_total_deducciones_rentas_exentas(
    dependientes: float,
    intereses_vivienda: float,
    pagos_salud: float,
    cesantias: float,
    aportes_pension_afc: float,
    renta_exenta_laboral: float,
) -> float:
    return (
        dependientes
        + intereses_vivienda
        + pagos_salud
        + cesantias
        + aportes_pension_afc
        + renta_exenta_laboral
    )


def calcular_deducciones_admisibles(
    total_deducciones: float,
    maximo_beneficio_ley_2277: float,
) -> float:
    return min(total_deducciones, maximo_beneficio_ley_2277)


def calcular_base_gravable(
    total_ingresos: float,
    ingresos_no_constitutivos: float,
    deducciones_admisibles: float,
) -> float:
    return total_ingresos - ingresos_no_constitutivos - deducciones_admisibles


def calcular_base_gravable_con_pac(
    total_ingresos: float,
    bonificacion_anual: float,
    ingresos_no_constitutivos: float,
    deducciones_admisibles: float,
) -> float:
    return total_ingresos - bonificacion_anual - ingresos_no_constitutivos - deducciones_admisibles


def calcular_base_uvt(base_gravable: float, uvt: float) -> float:
    return base_gravable / uvt


def calcular_impuesto_renta(base_uvt: float, uvt: float = UVT) -> float:
    for tramo in TRAMOS_RENTA:
        desde = tramo["desde"]
        hasta = tramo["hasta"]
        tarifa = tramo["tarifa"]
        base = tramo["base"]

        if hasta is None:
            if base_uvt >= desde:
                return round((((base_uvt - desde) * tarifa) + base) * uvt, 2)
        else:
            if desde <= base_uvt < hasta:
                return round((((base_uvt - desde) * tarifa) + base) * uvt, 2)

    return 0.0


def ejecutar_simulador(inputs: dict) -> dict:
    salario_anual = calcular_salario_anual(inputs["salario_mensual"], inputs["tipo_salario"])
    ingreso_variable = calcular_ingreso_variable(inputs["valor_variable_anual"])
    auxilios_anuales = calcular_auxilios_anuales(inputs["valor_auxilios_mensual"])
    bonificacion_anual = calcular_bonificacion_anual(inputs["valor_bonificaciones"])

    total_ingresos = calcular_total_ingresos(
        salario_anual,
        ingreso_variable,
        auxilios_anuales,
        bonificacion_anual,
    )

    base_seg_social = calcular_base_seguridad_social(
        salario_anual,
        ingreso_variable,
        inputs["tipo_salario"],
    )

    base_bono = calcular_base_seguridad_social_bono(
        bonificacion_anual,
        inputs["tipo_salario"],
        inputs["bono_salarial"],
    )

    aporte_eps = calcular_aporte_eps(base_seg_social, base_bono)
    aporte_pension = calcular_aporte_pension(aporte_eps)
    fondo_solidaridad = calcular_fondo_solidaridad(base_seg_social, TABLA_FSP)

    ingresos_no_constitutivos = calcular_ingresos_no_constitutivos(
        aporte_eps,
        aporte_pension,
        fondo_solidaridad,
        inputs["aporte_voluntario_obligatorio_anual"],
    )

    renta_liquida = calcular_renta_liquida(total_ingresos, ingresos_no_constitutivos)
    renta_liquida_pac = calcular_renta_liquida_con_pac(
        total_ingresos,
        bonificacion_anual,
        ingresos_no_constitutivos,
    )

    maximo_beneficio_ley = calcular_maximo_beneficio_ley_2277(UVT)

    dependientes = calcular_dependientes(
        inputs["numero_dependientes"],
        inputs["salario_mensual"],
        UVT,
    )

    intereses_vivienda = calcular_intereses_vivienda(inputs["intereses_vivienda_anual"])
    pagos_salud = calcular_pagos_salud(inputs["pagos_salud_anual"])
    cesantias = calcular_cesantias(inputs["salario_mensual"], inputs["tipo_salario"])
    aportes_pension_afc = calcular_aportes_pension_voluntaria_afc(inputs["aportes_pension_afc_anual"])

    renta_exenta_sin_limite = calcular_renta_exenta_sin_limite(
        renta_liquida,
        dependientes,
        intereses_vivienda,
        pagos_salud,
        cesantias,
        aportes_pension_afc,
    )

    renta_exenta_laboral = calcular_renta_exenta_laboral(renta_exenta_sin_limite, UVT)

    total_deducciones = calcular_total_deducciones_rentas_exentas(
        dependientes,
        intereses_vivienda,
        pagos_salud,
        cesantias,
        aportes_pension_afc,
        renta_exenta_laboral,
    )

    deducciones_admisibles = calcular_deducciones_admisibles(
        total_deducciones,
        maximo_beneficio_ley,
    )

    base_gravable = calcular_base_gravable(
        total_ingresos,
        ingresos_no_constitutivos,
        deducciones_admisibles,
    )

    base_gravable_pac = calcular_base_gravable_con_pac(
        total_ingresos,
        bonificacion_anual,
        ingresos_no_constitutivos,
        deducciones_admisibles,
    )

    base_uvt = calcular_base_uvt(base_gravable, UVT)
    base_uvt_pac = calcular_base_uvt(base_gravable_pac, UVT)

    impuesto_normal = calcular_impuesto_renta(base_uvt, UVT)
    impuesto_pac = calcular_impuesto_renta(base_uvt_pac, UVT)

    return {
        "salario_anual": salario_anual,
        "ingreso_variable": ingreso_variable,
        "auxilios_anuales": auxilios_anuales,
        "bonificacion_anual": bonificacion_anual,
        "total_ingresos": total_ingresos,
        "aporte_eps": aporte_eps,
        "aporte_pension": aporte_pension,
        "fondo_solidaridad": fondo_solidaridad,
        "ingresos_no_constitutivos": ingresos_no_constitutivos,
        "renta_liquida": renta_liquida,
        "renta_liquida_pac": renta_liquida_pac,
        "dependientes": dependientes,
        "intereses_vivienda": intereses_vivienda,
        "pagos_salud": pagos_salud,
        "cesantias": cesantias,
        "aportes_pension_afc": aportes_pension_afc,
        "renta_exenta_laboral": renta_exenta_laboral,
        "total_deducciones": total_deducciones,
        "deducciones_admisibles": deducciones_admisibles,
        "base_gravable": base_gravable,
        "base_gravable_pac": base_gravable_pac,
        "base_uvt": base_uvt,
        "base_uvt_pac": base_uvt_pac,
        "impuesto_sin_optimizacion": round(impuesto_normal, 2),
        "impuesto_optimizado": round(impuesto_pac, 2),
        "beneficio": round(impuesto_normal - impuesto_pac, 2),
    }
