def formato_moneda(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def formato_numero(valor: float, decimales: int = 2) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formato_porcentaje(valor: float, decimales: int = 2) -> str:
    return f"{valor:.{decimales}%}".replace(".", ",")
