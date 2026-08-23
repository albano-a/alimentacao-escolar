"""Dashboard interativa de alimentação escolar (Streamlit).

Ponto de entrada do app: só orquestra os módulos abaixo, sem lógica própria.
    data.py      -> leitura e limpeza dos dados (planilha do Google Sheets)
    charts.py    -> construção dos gráficos (Plotly)
    formatting.py-> formatação de números para exibição
    filters.py   -> barra lateral (conjunto, filtros, navegação)
    kpis.py      -> cartões de indicadores da Visão geral
    paginas/     -> uma página por arquivo
"""

from __future__ import annotations

import functools
import unicodedata

import pandas as pd
import streamlit as st

import data
import filters
import paginas

st.set_page_config(
    page_title="Alimentação Escolar",
    page_icon="🍽️",
    layout="wide",
)

# Ajustes só de espaçamento/tamanho para telas estreitas (sem mexer em cor/tema):
# menos preenchimento nas laterais e métricas menores, para caber os cartões de
# KPI (que ficam em colunas aninhadas) sem apertar demais os números.
st.markdown(
    """
    <style>
    @media (max-width: 640px) {
        .block-container { padding: 1rem 0.75rem; }
        [data-testid="stMetricValue"] { font-size: 1.3rem; }
        [data-testid="stMetricLabel"] { font-size: 0.75rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60)
def carregar_dados() -> pd.DataFrame:
    """Recarrega da planilha do Google Sheets a cada 60s, para refletir edições feitas nela."""
    return data.carregar_combinado()


def main() -> None:
    st.title("🍽️ Alimentação Escolar — Dashboard")
    st.caption("Visão interativa da demanda de refeições por escola, tipo e polo.")

    try:
        df = carregar_dados()
    except Exception:
        st.error(
            "Não foi possível carregar os dados da planilha do Google Sheets. "
            "Verifique se ela ainda está compartilhada como 'qualquer pessoa com "
            "o link pode visualizar' e se as abas mantêm os nomes esperados "
            "(Integrais, Base UMEI, Base Parcial)."
        )
        st.stop()

    df_filtrado = filters.barra_lateral(df)

    def _slug(nome: str) -> str:
        sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
        return sem_acento.lower().replace(" ", "-")

    paginas_navegacao = [
        st.Page(functools.partial(renderizar, df_filtrado), title=nome, url_path=_slug(nome))
        for nome, renderizar in paginas.PAGINAS.items()
    ]
    navegacao = st.navigation(paginas_navegacao, position="top")
    navegacao.run()


if __name__ == "__main__":
    main()
