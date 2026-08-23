"""Barra lateral: filtros (Conjunto, Polo, Categoria, Escola) e navegação entre páginas."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from paginas import PAGINAS


def barra_lateral(df: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    with st.sidebar:
        st.subheader("Filtros")

        conjuntos = sorted(df["Conjunto"].dropna().unique())
        conjuntos_selecionados = st.multiselect(
            "Conjunto de dados", conjuntos, default=conjuntos
        )
        df_conjunto = df[df["Conjunto"].isin(conjuntos_selecionados)]

        polos = sorted(df_conjunto["Polo"].dropna().unique())
        polos_selecionados = st.multiselect("Polo", polos, default=polos)
        df_polo = df_conjunto[df_conjunto["Polo"].isin(polos_selecionados)]

        categorias = sorted(df_polo["Categoria"].dropna().unique())
        categorias_selecionadas = st.multiselect(
            "Categoria", categorias, default=categorias, placeholder="Todas as categorias"
        )
        df_categoria = df_polo[df_polo["Categoria"].isin(categorias_selecionadas)]

        escolas = sorted(df_categoria["Escola"].dropna().unique())
        escolas_selecionadas = st.multiselect(
            "Escola", escolas, default=escolas, placeholder="Todas as escolas"
        )
        df_filtrado = df_categoria[df_categoria["Escola"].isin(escolas_selecionadas)]

        st.divider()
        pagina = st.radio("Página", list(PAGINAS.keys()))

    return pagina, df_filtrado
