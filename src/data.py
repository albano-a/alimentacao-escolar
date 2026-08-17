"""Leitura e limpeza dos 3 conjuntos de dados de alimentação escolar.

Os dados vêm ao vivo de uma planilha do Google Sheets (uma aba por conjunto).
Qualquer edição feita na planilha aparece na dashboard na próxima atualização
(ver o `ttl` do cache em `main.py`), sem precisar tocar neste arquivo.
"""

from __future__ import annotations

import urllib.parse

import pandas as pd

REFEICOES = ["Desjejum", "Lanche", "Almoço", "Janta"]

PLANILHA_ID = "1Mqqp4AJKscJcTE_CjsAQGDQ4PRD017v2Bvzeu2BfcLk"

# Nome da aba na planilha -> nome exibido na dashboard.
ABAS = {
    "Unidades Integrais - Ensino Fundamental": "Unidades Integrais - Ensino Fundamental",
    "Unidades Municipais de Educação Infantil (UMEI) - Integrais": "Unidades Municipais de Educação Infantil (UMEI) - Integrais",
    "Unidades Escolar - Parcial - Ensino Fundamental": "Unidades Escolar - Parcial - Ensino Fundamental",
}

COLUNAS_BASE = ["Polo", "Escola", "Dias letivos", *REFEICOES]


def _normaliza_polo(valor: str) -> str:
    valor = str(valor).strip()
    return valor if valor.upper().startswith("POLO") else f"POLO {valor}"


def _para_numero(serie: pd.Series) -> pd.Series:
    """Converte texto vindo da planilha (ex.: '158,47', '-', vazio) para float."""
    limpo = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(limpo, errors="coerce")


def _url_aba(nome_aba: str) -> str:
    """URL de exportação CSV (gviz) de uma aba específica da planilha pública."""
    query = urllib.parse.quote(nome_aba)
    return f"https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/gviz/tq?tqx=out:csv&sheet={query}"


def _carregar_aba(nome_aba: str) -> pd.DataFrame:
    """Lê uma aba da planilha e recalcula Total/Média a partir das colunas brutas
    (mais simples e confiável do que confiar nos valores já formatados da planilha)."""
    bruto = pd.read_csv(_url_aba(nome_aba))
    print(bruto)
    df = bruto[COLUNAS_BASE].copy()

    df["Polo"] = df["Polo"].map(_normaliza_polo)
    df["Escola"] = df["Escola"].astype(str).str.strip()
    df["Dias letivos"] = _para_numero(df["Dias letivos"])
    for col in REFEICOES:
        df[col] = _para_numero(df[col])

    df["Total de refeições"] = df[REFEICOES].sum(axis=1, min_count=1)
    for col in REFEICOES:
        df[f"Média/dia - {col}"] = df[col] / df["Dias letivos"]
    df["Média/dia - Total"] = df["Total de refeições"] / df["Dias letivos"]
    return df


def carregar_todos() -> dict[str, pd.DataFrame]:
    """Retorna os 3 conjuntos de dados já limpos, lidos ao vivo da planilha."""
    return {nome_exibido: _carregar_aba(aba) for nome_exibido, aba in ABAS.items()}
