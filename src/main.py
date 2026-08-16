"""Dashboard interativa de alimentação escolar (Streamlit)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
import data

st.set_page_config(
    page_title="Alimentação Escolar",
    page_icon="🍽️",
    layout="wide",
)


@st.cache_data
def carregar_dados() -> dict[str, pd.DataFrame]:
    return data.carregar_todos()


def formatar(valor: float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def barra_lateral(datasets: dict[str, pd.DataFrame]) -> tuple[str, pd.DataFrame, str]:
    with st.sidebar:
        st.subheader("Filtros")
        conjunto = st.selectbox("Conjunto de dados", list(datasets.keys()))
        df = datasets[conjunto]

        polos = sorted(df["Polo"].dropna().unique())
        polos_selecionados = st.multiselect("Polo", polos, default=polos)
        df_polo = df[df["Polo"].isin(polos_selecionados)]

        escolas = sorted(df_polo["Escola"].dropna().unique())
        escolas_selecionadas = st.multiselect(
            "Escola", escolas, default=escolas, placeholder="Todas as escolas"
        )
        df_filtrado = df_polo[df_polo["Escola"].isin(escolas_selecionadas)]

        st.divider()
        pagina = st.radio("Página", ["Visão geral", "Resumo por escola"])

    return pagina, df_filtrado, conjunto


def cartao_kpis(df: pd.DataFrame) -> None:
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Escolas/Unidades", formatar(df["Escola"].nunique()))
        col2.metric("Total de refeições", formatar(df["Total de refeições"].sum()))
        col3.metric("Média/dia (total)", formatar(df["Média/dia - Total"].mean(), 1))
        col4.metric("Polos", df["Polo"].nunique())


def pagina_visao_geral(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Nenhum registro para os filtros selecionados.")
        return

    cartao_kpis(df)

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


def pagina_resumo_escola(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Nenhum registro para os filtros selecionados.")
        return

    escolas = sorted(df["Escola"].unique())
    escola_selecionada = st.selectbox("Escolha a escola", escolas)
    linha = df.loc[df["Escola"] == escola_selecionada].iloc[0]

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Polo", linha["Polo"])
        col2.metric("Dias letivos", int(linha["Dias letivos"]))
        col3.metric("Total de refeições", formatar(linha["Total de refeições"]))
        col4.metric("Média/dia (total)", formatar(linha["Média/dia - Total"], 1))

    col_esq, col_dir = st.columns([1, 1.4])
    with col_esq:
        with st.container(border=True):
            st.plotly_chart(charts.grafico_perfil_escola(linha), use_container_width=True)
    with col_dir:
        with st.container(border=True):
            st.plotly_chart(
                charts.grafico_comparacao_escola(linha, df), use_container_width=True
            )

    media_geral = df["Média/dia - Total"].mean()
    diferenca = linha["Média/dia - Total"] - media_geral
    sinal = "acima" if diferenca >= 0 else "abaixo"
    st.caption(
        f"A média/dia total desta escola está {abs(diferenca):.1f} refeições "
        f"{sinal} da média geral do conjunto ({media_geral:.1f})."
    )

    with st.expander("Ver linha completa de dados"):
        st.dataframe(linha.to_frame().T, use_container_width=True, hide_index=True)


def main() -> None:
    st.title("🍽️ Alimentação Escolar — Dashboard")
    st.caption("Visão interativa da demanda de refeições por escola, tipo e polo.")

    datasets = carregar_dados()
    pagina, df_filtrado, conjunto = barra_lateral(datasets)

    st.subheader(f"{conjunto} · {pagina}")

    if pagina == "Visão geral":
        pagina_visao_geral(df_filtrado)
    else:
        pagina_resumo_escola(df_filtrado)


if __name__ == "__main__":
    main()
