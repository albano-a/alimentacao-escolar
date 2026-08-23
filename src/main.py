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

    pagina, df_filtrado = filters.barra_lateral(df)

    st.subheader(pagina)
    paginas.PAGINAS[pagina](df_filtrado)


if __name__ == "__main__":
    main()
