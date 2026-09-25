"""Página 'Conformidade FNDE': controle da quantidade mínima de refeições exigida
pelo Art. 14 da Resolução CD/FNDE nº 26/2013, Seção II (Da Oferta da Alimentação
nas Escolas).

https://www.gov.br/fnde/pt-br/acesso-a-informacao/legislacao/resolucoes/2013/resolucao-cd-fnde-no-26-de-17-de-junho-de-2013
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
from formatting import formatar

_URL_RESOLUCAO = (
    "https://www.gov.br/fnde/pt-br/acesso-a-informacao/legislacao/resolucoes/2013/"
    "resolucao-cd-fnde-no-26-de-17-de-junho-de-2013"
)


def renderizar(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Nenhum registro para os filtros selecionados.")
        return

    st.info(
        "**O que é verificado:** o Art. 14 da "
        f"[Resolução CD/FNDE nº 26/2013]({_URL_RESOLUCAO}) exige um número mínimo de "
        "refeições conforme a categoria/regime da turma: creche em tempo integral ou "
        "tempo integral (Mais Educação) → **mínimo 3 refeições** (cobrindo 70% das "
        "necessidades nutricionais diárias); creche em período parcial → **mínimo 2** "
        "(30%). Para educação básica em período parcial fora de creche, a resolução "
        "não fixa uma quantidade mínima — 1 refeição já atende a 20% e 2 ou mais "
        "atende a 30% — por isso essas turmas aparecem como **não avaliáveis** aqui.\n\n"
        "**O que NÃO é verificado:** os percentuais de necessidades nutricionais "
        "diárias, os limites de sódio/açúcar/gordura (Art. 16) e os testes de "
        "aceitabilidade (Art. 17) exigem dados de composição nutricional que esta "
        "planilha não registra — só é possível conferir a *quantidade* de refeições."
    )

    avaliaveis = df["Conforme FNDE (Art. 14)"].notna().sum()
    conformes = (df["Conforme FNDE (Art. 14)"] == True).sum()  # noqa: E712
    nao_conformes = (df["Conforme FNDE (Art. 14)"] == False).sum()  # noqa: E712
    pct_conforme = (conformes / avaliaveis * 100) if avaliaveis else float("nan")

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Turmas avaliáveis", formatar(avaliaveis))
        col2.metric("Conformes", formatar(conformes))
        col3.metric("Não conformes", formatar(nao_conformes))
        col4.metric("% de conformidade", formatar(pct_conforme, 1) + "%" if avaliaveis else "—")

    with st.container(border=True):
        st.plotly_chart(charts.grafico_conformidade_fnde(df), use_container_width=True)

    nao_conformes_df = df.loc[df["Conforme FNDE (Art. 14)"] == False]  # noqa: E712
    if not nao_conformes_df.empty:
        with st.container(border=True):
            st.warning(f"⚠️ {len(nao_conformes_df)} turma(s) abaixo do mínimo exigido.")
            colunas = [
                "Mês", "Conjunto", "Polo", "Escola", "Categoria", "Regime",
                "Matriculados",
                *[c for c in charts.REFEICOES if c in nao_conformes_df.columns],
                "Refeições servidas", "Mínimo FNDE (Art. 14)",
            ]
            st.dataframe(
                nao_conformes_df[colunas].sort_values(["Regime", "Refeições servidas"]),
                use_container_width=True,
                hide_index=True,
            )

    with st.expander("Ver todas as turmas não avaliáveis (sem piso fixo na resolução)"):
        colunas = ["Mês", "Conjunto", "Polo", "Escola", "Categoria", "Regime", "Refeições servidas"]
        st.dataframe(
            df.loc[df["Conforme FNDE (Art. 14)"].isna(), colunas],
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Ver todos os dados de conformidade"):
        colunas = [
            "Mês", "Conjunto", "Polo", "Escola", "Categoria", "Regime",
            "Refeições servidas", "Mínimo FNDE (Art. 14)", "Conforme FNDE (Art. 14)",
        ]
        st.dataframe(df[colunas], use_container_width=True, hide_index=True)
