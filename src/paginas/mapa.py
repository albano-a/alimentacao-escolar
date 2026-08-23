"""Página 'Mapa': posicionamento geográfico das escolas do conjunto/filtro atual,
coloridas pela conformidade FNDE (Art. 14) e dimensionadas pelo total de refeições.

As coordenadas vêm do GeoSIG de Niterói (camadas de Ensino Fundamental e UMEIs)
mais um cadastro manual das escolas que não estão lá (majoritariamente centros
comunitários conveniados), casadas com o nome de escola da planilha — ver
localizacao.py para os detalhes do casamento de nomes."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
import localizacao

_UM_DIA = 60 * 60 * 24


@st.cache_data(ttl=_UM_DIA)
def _registros_localizacao() -> list[dict]:
    """Só a chamada de rede ao GeoSIG é cacheada por bastante tempo (a posição
    das escolas não muda de um dia para o outro); o cadastro manual não precisa
    de cache (não faz rede); o casamento de nomes roda de novo a cada filtro,
    mas é barato o suficiente para não precisar de cache."""
    return localizacao.buscar_registros_gis() + localizacao.registros_manuais()


def renderizar(df: pd.DataFrame) -> None:
    if df.empty:
        st.warning("Nenhum registro para os filtros selecionados.")
        return

    try:
        registros = _registros_localizacao()
    except Exception:
        st.error(
            "Não foi possível buscar as coordenadas no GeoSIG de Niterói agora. "
            "Tente novamente em alguns minutos."
        )
        return

    nomes = sorted(df["Escola"].unique())
    localizacoes = localizacao.casar_com_escolas(nomes, registros)

    combinado = df.merge(localizacoes, on="Escola", how="inner")
    if combinado.empty:
        st.warning("Nenhuma escola do filtro atual tem localização encontrada.")
        return

    with st.container(border=True):
        st.plotly_chart(charts.grafico_mapa_escolas(combinado), use_container_width=True)

    sem_local = sorted(set(nomes) - set(localizacoes["Escola"]))
    st.caption(
        f"{len(nomes) - len(sem_local)} de {len(nomes)} escolas do filtro atual "
        "têm localização cadastrada."
    )
    if sem_local:
        with st.expander(f"Ver {len(sem_local)} escola(s) sem localização encontrada"):
            st.dataframe(
                pd.DataFrame({"Escola": sem_local}), use_container_width=True, hide_index=True
            )
