"""Cartões de indicadores (KPIs) exibidos no topo da Visão geral."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data import GRUPOS_ORDEM, REFEICOES, total_matriculados
from formatting import formatar


def renderizar(df: pd.DataFrame) -> None:
    grupos_presentes = df["Grupo categoria"].dropna().unique()
    matriculados = total_matriculados(df)
    total_refeicoes = df["Total de refeições"].sum()
    per_capita = total_refeicoes / matriculados if matriculados else float("nan")

    with st.container(border=True):
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Escolas/Unidades", formatar(df["Escola"].nunique()))
        col2.metric("Matriculados", formatar(matriculados))
        col3.metric(
            "Total de refeições",
            formatar(total_refeicoes),
            help=f"Refeições por matriculado no filtro atual: {formatar(per_capita, 1)}.",
        )
        if len(grupos_presentes) > 1:
            col4.metric(
                "Média/dia (total)",
                "—",
                help=(
                    "Com mais de um grupo de categoria selecionado (Creche e pré-escola "
                    "e E.F. e E.J.A. têm escalas muito diferentes), uma média única não é "
                    "representativa. Veja a média/dia por categoria abaixo."
                ),
            )
        else:
            col4.metric("Média/dia (total)", formatar(df["Média/dia - Total"].mean(), 1))
        col5.metric("Polos", df["Polo"].nunique())
        nao_conformes = (df["Conforme FNDE (Art. 14)"] == False).sum()  # noqa: E712 (comparação com <NA> precisa ser explícita)
        col6.metric(
            "Fora do mínimo FNDE",
            formatar(nao_conformes),
            help=(
                "Turmas servindo menos refeições do que o mínimo do Art. 14 da "
                "Resolução CD/FNDE nº 26/2013 (creche/tempo integral: 3; creche "
                "parcial: 2). Ver a página 'Conformidade FNDE' para detalhes."
            ),
        )

    _renderizar_por_tipo(df)
    _renderizar_por_categoria(df, grupos_presentes)


def _renderizar_por_tipo(df: pd.DataFrame) -> None:
    with st.container(border=True):
        st.caption("Somatório por tipo de refeição")
        cols = st.columns(len(REFEICOES))
        for col, tipo in zip(cols, REFEICOES):
            col.metric(tipo, formatar(df[tipo].sum()))


def _renderizar_por_categoria(df: pd.DataFrame, grupos_presentes) -> None:
    grupos = [g for g in GRUPOS_ORDEM if g in grupos_presentes]
    if len(grupos) < 2:
        return

    with st.container(border=True):
        st.caption("Medidores por categoria")
        cols = st.columns(len(grupos))
        for col, grupo in zip(cols, grupos):
            sub = df[df["Grupo categoria"] == grupo]
            with col:
                st.markdown(f"**{grupo}**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Escolas", formatar(sub["Escola"].nunique()))
                c2.metric("Total", formatar(sub["Total de refeições"].sum()))
                c3.metric("Média/dia", formatar(sub["Média/dia - Total"].mean(), 1))
