"""Página 'Resumo por escola': detalhe de uma única escola do conjunto/filtro atual."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
from data import FLAGS
from formatting import formatar

_COLUNAS_SOMADAS = [
    *charts.REFEICOES,
    "Total de refeições",
]


def _dias_totais(linhas: pd.DataFrame):
    """Dias letivos no período: soma dos dias de cada mês (máximo entre as
    turmas do mesmo escola/mês — são sempre iguais). Usar só o máximo
    subconta quando há vários meses filtrados."""
    if "Mês" in linhas.columns:
        return linhas.groupby("Mês")["Dias letivos"].max().sum()
    return linhas["Dias letivos"].max()


def _resumo_escola(linhas: pd.DataFrame) -> pd.Series:
    """Uma escola pode ter mais de uma linha (uma por modalidade/turma, ex.: E.F.
    e E.J.A. na mesma escola). Isso soma os números para dar um resumo da escola
    inteira, em vez de mostrar só a primeira modalidade encontrada."""
    if len(linhas) == 1:
        return linhas.iloc[0]

    resumo = linhas.iloc[0].copy()
    resumo[_COLUNAS_SOMADAS] = linhas[_COLUNAS_SOMADAS].sum(min_count=1)
    resumo["Categoria"] = " / ".join(sorted(linhas["Categoria"].unique()))
    dias = _dias_totais(linhas)
    resumo["Dias letivos"] = dias
    for c in charts.REFEICOES:
        total_c = resumo.get(c)
        resumo[f"Média/dia - {c}"] = round(float(total_c) / float(dias), 1) if pd.notna(total_c) and pd.notna(dias) and dias else pd.NA
    total_geral = resumo.get("Total de refeições")
    resumo["Média/dia - Total"] = round(float(total_geral) / float(dias), 1) if pd.notna(total_geral) and pd.notna(dias) and dias else pd.NA
    # Matriculados se repete por turma (é o total da escola), então usa o máximo.
    if "Matriculados" in linhas.columns:
        resumo["Matriculados"] = linhas["Matriculados"].max()
    # Flags: basta uma turma com TRUE para marcar a escola.
    for flag in FLAGS:
        if flag in linhas.columns:
            valores = linhas[flag].dropna()
            resumo[flag] = bool(valores.any()) if not valores.empty else pd.NA
    return resumo


def renderizar(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Nenhum registro para os filtros selecionados.")
        return

    escolas = sorted(df["Escola"].unique())
    escola_selecionada = st.selectbox("Escolha a escola", escolas)
    linhas = df.loc[df["Escola"] == escola_selecionada]
    linha = _resumo_escola(linhas)

    legenda_categoria = f"Categoria: {linha['Categoria']}"
    if len(linhas) > 1:
        legenda_categoria += f" ({len(linhas)} turmas somadas)"
    st.caption(legenda_categoria)

    if (linhas["Conforme FNDE (Art. 14)"] == False).any():  # noqa: E712
        st.warning(
            "⚠️ Uma ou mais turmas desta escola estão abaixo do mínimo de refeições "
            "do Art. 14 da Resolução CD/FNDE nº 26/2013 — ver a página "
            "**Conformidade FNDE** para detalhes."
        )

    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Polo", linha["Polo"])
        col2.metric("Matriculados", formatar(linha.get("Matriculados")))
        col3.metric("Dias letivos", formatar(linha["Dias letivos"]))
        col4.metric("Total de refeições", formatar(linha["Total de refeições"]))
        col5.metric("Média/dia (total)", formatar(linha["Média/dia - Total"], 1))

    matriculados = linha.get("Matriculados")
    if matriculados and matriculados > 0:
        st.caption(
            f"Refeições por matriculado: {linha['Total de refeições'] / matriculados:.1f} "
            f"no período ({formatar(linha['Total de refeições'])} refeições / "
            f"{formatar(matriculados)} matriculados)."
        )

    flags_marcadas = [f for f in FLAGS if f in linhas.columns and bool(linhas[f].eq(True).any())]
    if flags_marcadas:
        st.info(f"📌 Acompanhamento registrado: {', '.join(flags_marcadas)}.")

    col_esq, col_dir = st.columns([1, 1.4])
    with col_esq:
        with st.container(border=True):
            st.plotly_chart(charts.grafico_perfil_escola(linha), use_container_width=True)
    with col_dir:
        with st.container(border=True):
            st.plotly_chart(
                charts.grafico_comparacao_escola(linhas, df), use_container_width=True
            )

    regime = linhas["Regime"].iloc[0] if "Regime" in linhas.columns else None
    base = charts._media_diaria_por_escola_mes(
        df.loc[df["Regime"] == regime] if regime is not None and "Regime" in df.columns else df
    )
    media_escola = base.loc[base["Escola"] == escola_selecionada, "Média/dia - Total"].mean()
    media_geral = base["Média/dia - Total"].mean()
    diferenca = media_escola - media_geral
    sinal = "acima" if diferenca >= 0 else "abaixo"
    rotulo_regime = f" do regime {regime}" if pd.notna(regime) else ""
    st.caption(
        f"Média/dia total desta escola (média mensal por escola): {media_escola:.1f} — "
        f"{abs(diferenca):.1f} refeições {sinal} da média geral{rotulo_regime} "
        f"por escola/mês ({media_geral:.1f})."
    )

    with st.expander("Ver linhas completas de dados"):
        st.dataframe(linhas, use_container_width=True, hide_index=True)
