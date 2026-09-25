"""Página 'Visão geral': KPIs e gráficos agregados para o conjunto/filtro atual."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
import kpis
from data import FLAGS
from formatting import formatar


def renderizar(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Nenhum registro para os filtros selecionados.")
        return

    kpis.renderizar(df)
    _alertas_minimo(df)
    _acompanhamento(df)

    col_esq, col_dir = st.columns(2)
    with col_esq:
        with st.container(border=True):
            st.plotly_chart(charts.grafico_por_polo(df), use_container_width=True)
    with col_dir:
        with st.container(border=True):
            st.plotly_chart(charts.grafico_total_por_tipo(df), use_container_width=True)

    with st.container(border=True):
        top_n = st.slider(
            "Quantidade de escolas no ranking", 5, max(5, len(df)), min(20, len(df))
        )
        st.plotly_chart(
            charts.grafico_total_por_escola(df, top_n=top_n), use_container_width=True
        )

    col_esq, col_dir = st.columns(2)
    with col_esq:
        with st.container(border=True):
            st.plotly_chart(charts.grafico_composicao_percentual(df), use_container_width=True)
    with col_dir:
        with st.container(border=True):
            st.plotly_chart(charts.grafico_dias_letivos_vs_total(df), use_container_width=True)

    if df[charts.REFEICOES].isna().any().any():
        with st.container(border=True):
            st.plotly_chart(charts.grafico_dados_faltantes(df), use_container_width=True)

    with st.expander("Mapa de calor: média diária por escola"):
        st.plotly_chart(charts.heatmap_media_diaria(df), use_container_width=True)

    with st.expander("Ver dados"):
        st.dataframe(df, use_container_width=True, hide_index=True)


def _alertas_minimo(df: pd.DataFrame) -> None:
    """Aviso curto quando há turmas fora do mínimo do Art. 14 da Res. FNDE 26/2013
    — o detalhe completo mora na página 'Conformidade FNDE'."""
    nao_conformes = df.loc[df["Conforme FNDE (Art. 14)"] == False]  # noqa: E712
    if nao_conformes.empty:
        return

    st.warning(
        f"⚠️ {len(nao_conformes)} turma(s) abaixo do mínimo de refeições do Art. 14 "
        "da Resolução CD/FNDE nº 26/2013. Veja a página **Conformidade FNDE** na "
        "barra lateral para o detalhe."
    )


def _acompanhamento(df: pd.DataFrame) -> None:
    """Resumo das flags de acompanhamento da planilha (visita/checklist/reunião/denúncia)."""
    flags_presentes = [c for c in FLAGS if c in df.columns]
    if not flags_presentes:
        return
    tem_flag = df[flags_presentes].eq(True).any(axis=1)
    if not tem_flag.any():
        return

    denominadas = df.loc[df["Denúncia"].eq(True)] if "Denúncia" in df.columns else df.iloc[0:0]
    if not denominadas.empty:
        st.warning(f"🚨 {len(denominadas)} turma(s) com denúncia registrada no filtro atual.")

    with st.container(border=True):
        st.caption("Acompanhamento (turmas com registro na planilha)")
        cols = st.columns(len(flags_presentes))
        for col, flag in zip(cols, flags_presentes):
            col.metric(flag, formatar(df[flag].eq(True).sum()))
        with st.expander("Ver turmas com acompanhamento"):
            colunas = ["Mês", "Polo", "Escola", "Categoria", *flags_presentes]
            st.dataframe(
                df.loc[tem_flag, colunas].sort_values(["Mês", "Escola"]),
                use_container_width=True,
                hide_index=True,
            )
