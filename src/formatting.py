"""Formatação de números para exibição (padrão brasileiro: milhar '.', decimal ',')."""

from __future__ import annotations

import pandas as pd


def formatar(valor: float, casas: int = 0) -> str:
    if pd.isna(valor):
        return "—"
    return f"{valor:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")
