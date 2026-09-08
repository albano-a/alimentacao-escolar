"""Barra lateral: filtros (Conjunto, Polo, Categoria, Escola). A navegação entre
páginas fica numa navbar no topo (ver main.py), não mais aqui.

Os multiselects começam vazios (nada pré-selecionado como "pill") e nenhuma
seleção equivale a "todas as opções" — isso evita uma barra lateral gigante
com uma pill por escola/categoria logo de cara, o que é especialmente ruim
no celular, onde a barra ocupa a tela inteira."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data import ordenar_meses


def _selecionados_ou_todos(selecionados: list, opcoes: list) -> list:
    return selecionados if selecionados else opcoes


def barra_lateral(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.subheader("Filtros")

        meses = ordenar_meses(df["Mês"].dropna().unique())
        meses_selecionados = st.multiselect("Mês", meses, placeholder="Todos os meses")
        df_mes = df[df["Mês"].isin(_selecionados_ou_todos(meses_selecionados, meses))]

        conjuntos = sorted(df_mes["Conjunto"].dropna().unique())
        conjuntos_selecionados = st.multiselect(
            "Conjunto de dados", conjuntos, placeholder="Todos os conjuntos"
        )
        df_conjunto = df_mes[df_mes["Conjunto"].isin(_selecionados_ou_todos(conjuntos_selecionados, conjuntos))]

        polos = sorted(df_conjunto["Polo"].dropna().unique())
        polos_selecionados = st.multiselect("Polo", polos, placeholder="Todos os polos")
        df_polo = df_conjunto[df_conjunto["Polo"].isin(_selecionados_ou_todos(polos_selecionados, polos))]

        categorias = sorted(df_polo["Categoria"].dropna().unique())
        categorias_selecionadas = st.multiselect(
            "Categoria", categorias, placeholder="Todas as categorias"
        )
        df_categoria = df_polo[
            df_polo["Categoria"].isin(_selecionados_ou_todos(categorias_selecionadas, categorias))
        ]

        escolas = sorted(df_categoria["Escola"].dropna().unique())
        escolas_selecionadas = st.multiselect(
            "Escola", escolas, placeholder="Todas as escolas"
        )
        df_filtrado = df_categoria[
            df_categoria["Escola"].isin(_selecionados_ou_todos(escolas_selecionadas, escolas))
        ]

    return df_filtrado
