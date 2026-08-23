"""Funções de construção de gráficos (Plotly) reutilizadas pela dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

REFEICOES = ["Desjejum", "Lanche", "Almoço", "Janta"]
CORES_REFEICOES = {
    "Desjejum": "#4C78A8",
    "Lanche": "#F58518",
    "Almoço": "#54A24B",
    "Janta": "#E45756",
}


def _agrupar_por_escola(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Soma as colunas informadas por escola, evitando que uma escola com mais de
    uma modalidade/turma cadastrada (ex.: E.F. e E.J.A. na mesma escola) apareça
    duplicada nos gráficos."""
    chave = [c for c in ["Polo", "Escola"] if c in df.columns]
    return df.groupby(chave, as_index=False)[colunas].sum()


def grafico_total_por_escola(df: pd.DataFrame, top_n: int | None = None) -> go.Figure:
    """Ranking horizontal do total de refeições por escola."""
    dados = _agrupar_por_escola(df, ["Total de refeições"])
    dados = dados.sort_values("Total de refeições", ascending=True)
    if top_n:
        dados = dados.tail(top_n)
    fig = px.bar(
        dados,
        x="Total de refeições",
        y="Escola",
        orientation="h",
        color="Polo" if "Polo" in dados.columns else None,
        title="Total de refeições por escola",
    )
    fig.update_layout(yaxis_title="", height=max(400, 22 * len(dados)))
    return fig


def grafico_total_por_tipo(df: pd.DataFrame) -> go.Figure:
    """Soma geral de refeições servidas por tipo (desjejum, lanche, almoço, janta)."""
    cols = [c for c in REFEICOES if c in df.columns]
    totais = df[cols].sum().reset_index()
    totais.columns = ["Refeição", "Quantidade"]
    fig = px.bar(
        totais, x="Refeição", y="Quantidade", color="Refeição",
        color_discrete_map=CORES_REFEICOES,
        title="Total de refeições por tipo",
    )
    fig.update_layout(showlegend=False, xaxis_title="")
    return fig


def grafico_composicao_percentual(df: pd.DataFrame) -> go.Figure:
    """Participação percentual de cada tipo de refeição por escola (100% empilhado)."""
    cols = [c for c in REFEICOES if c in df.columns]
    pct = _agrupar_por_escola(df, cols)
    total_linha = pct[cols].sum(axis=1)
    pct[cols] = pct[cols].div(total_linha, axis=0) * 100
    pct = pct.assign(_total=total_linha).sort_values("_total", ascending=False).drop(columns="_total")
    fig = px.bar(
        pct, x="Escola", y=cols, title="Composição percentual das refeições por escola",
        color_discrete_map=CORES_REFEICOES,
    )
    fig.update_layout(
        xaxis_title="", yaxis_title="Participação (%)",
        legend_title="Refeição", xaxis_tickangle=-45, barmode="stack",
    )
    return fig


def grafico_por_polo(df: pd.DataFrame) -> go.Figure:
    """Total de refeições agregado por polo."""
    agregado = df.groupby("Polo", as_index=False)["Total de refeições"].sum()
    agregado = agregado.sort_values("Total de refeições", ascending=False)
    fig = px.bar(
        agregado, x="Polo", y="Total de refeições", color="Polo",
        title="Total de refeições por polo",
    )
    fig.update_layout(xaxis_title="", showlegend=False)
    return fig


def heatmap_media_diaria(df: pd.DataFrame) -> go.Figure:
    """Mapa de calor da média diária de refeições por escola e tipo."""
    cols = [f"Média/dia - {c}" for c in REFEICOES if f"Média/dia - {c}" in df.columns]
    agregado = _agrupar_por_escola(df, cols)
    heat = agregado.set_index("Escola")[cols].fillna(0)
    heat.columns = [c.replace("Média/dia - ", "") for c in heat.columns]
    fig = px.imshow(
        heat,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels=dict(x="Tipo de refeição", y="Escola", color="Refeições/dia"),
        title="Média diária de refeições por escola",
    )
    fig.update_layout(height=max(400, 22 * len(heat)))
    return fig


def grafico_dias_letivos_vs_total(df: pd.DataFrame) -> go.Figure:
    """Dispersão entre dias letivos e total de refeições, evidenciando outliers."""
    fig = px.scatter(
        df, x="Dias letivos", y="Total de refeições",
        color="Polo" if "Polo" in df.columns else None,
        hover_name="Escola", size="Total de refeições",
        title="Dias letivos x Total de refeições",
    )
    return fig


_CORES_CONFORMIDADE = {
    "Conforme": "#54A24B",
    "Não conforme": "#E45756",
    "Não avaliável": "#B0B0B0",
}


def grafico_conformidade_fnde(df: pd.DataFrame) -> go.Figure:
    """Quantidade de turmas conformes/não conformes/não avaliáveis por categoria,
    segundo o mínimo de refeições do Art. 14 da Resolução CD/FNDE nº 26/2013."""
    rotulo = df["Conforme FNDE (Art. 14)"].map(
        {True: "Conforme", False: "Não conforme"}
    ).fillna("Não avaliável")
    contagem = (
        df.assign(Status=rotulo)
        .groupby(["Categoria", "Status"], as_index=False)
        .size()
        .rename(columns={"size": "Turmas"})
    )
    fig = px.bar(
        contagem, x="Categoria", y="Turmas", color="Status",
        color_discrete_map=_CORES_CONFORMIDADE,
        category_orders={"Status": list(_CORES_CONFORMIDADE.keys())},
        title="Conformidade FNDE (Art. 14) por categoria",
    )
    fig.update_layout(xaxis_title="", xaxis_tickangle=-30)
    return fig


def grafico_dados_faltantes(df: pd.DataFrame) -> go.Figure:
    """Quantidade de valores ausentes por coluna de refeição (indica meses/tipos sem oferta)."""
    cols = [c for c in REFEICOES if c in df.columns]
    faltantes = df[cols].isna().sum().reset_index()
    faltantes.columns = ["Refeição", "Escolas sem registro"]
    fig = px.bar(
        faltantes, x="Refeição", y="Escolas sem registro", color="Refeição",
        color_discrete_map=CORES_REFEICOES,
        title="Escolas sem registro por tipo de refeição",
    )
    fig.update_layout(showlegend=False, xaxis_title="")
    return fig


def grafico_perfil_escola(linha: pd.Series) -> go.Figure:
    """Composição das refeições de uma única escola (donut)."""
    cols = [c for c in REFEICOES if c in linha.index and pd.notna(linha[c])]
    fig = px.pie(
        names=cols, values=[linha[c] for c in cols],
        color=cols, color_discrete_map=CORES_REFEICOES,
        hole=0.55, title="Composição de refeições da escola",
    )
    fig.update_traces(textinfo="percent+label")
    return fig


def grafico_comparacao_escola(linha: pd.Series, df: pd.DataFrame) -> go.Figure:
    """Compara a média/dia da escola com a média do polo e a média geral do conjunto."""
    polo = linha.get("Polo")
    media_cols = [f"Média/dia - {c}" for c in REFEICOES if f"Média/dia - {c}" in df.columns]
    escola_vals = [linha.get(c) for c in media_cols]
    polo_vals = df.loc[df["Polo"] == polo, media_cols].mean()
    geral_vals = df[media_cols].mean()

    rotulos = [c.replace("Média/dia - ", "") for c in media_cols]
    comparacao = pd.DataFrame(
        {
            "Refeição": rotulos * 3,
            "Média/dia": list(escola_vals) + list(polo_vals) + list(geral_vals),
            "Referência": (
                [linha.get("Escola", "Escola")] * len(rotulos)
                + [f"Média do {polo}"] * len(rotulos)
                + ["Média geral"] * len(rotulos)
            ),
        }
    )
    fig = px.bar(
        comparacao, x="Refeição", y="Média/dia", color="Referência",
        barmode="group", title="Escola x média do polo x média geral (refeições/dia)",
    )
    fig.update_layout(xaxis_title="")
    return fig
