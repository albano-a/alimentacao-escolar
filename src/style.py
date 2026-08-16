"""Paleta de marca (dark mode) e ajustes de acessibilidade (contraste)."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

OURO = "#FCBE26"
BRANCO = "#FFFFFF"
PRETO = "#000000"

FUNDO = "#000000"
FUNDO_CARTAO = "#141414"
BORDA = "#333333"

# Tons pensados para contraste sobre fundo PRETO (WCAG AA), não sobre branco.
OURO_CLARO = "#FFD966"
AMBAR = "#E8A33D"
CINZA_CLARO = "#D9D9D9"
CINZA_MEDIO = "#9E9E9E"
OURO_PALIDO = "#FFF3D0"

PALETA_CATEGORICA = [OURO, BRANCO, OURO_CLARO, CINZA_CLARO, AMBAR, CINZA_MEDIO, OURO_PALIDO]

# Escala sequencial: escuro (funde com o fundo) -> ouro -> branco (destaque máximo).
ESCALA_SEQUENCIAL = [
    [0.0, "#1A1A1A"],
    [0.5, OURO],
    [1.0, BRANCO],
]


def texto_contrastante(cor_hex: str) -> str:
    """Retorna preto ou branco, o que der mais contraste sobre `cor_hex` (WCAG)."""
    cor_hex = cor_hex.lstrip("#")
    r, g, b = (int(cor_hex[i : i + 2], 16) for i in (0, 2, 4))
    luminancia = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return PRETO if luminancia > 140 else BRANCO


def aplicar_tema_grafico(fig: go.Figure) -> go.Figure:
    """Padroniza fundo, fonte e cores dos eixos para contraste consistente no dark mode."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=FUNDO_CARTAO,
        plot_bgcolor=FUNDO_CARTAO,
        font=dict(color=BRANCO, size=13),
        title_font=dict(color=BRANCO, size=17),
        legend=dict(font=dict(color=BRANCO)),
        colorway=PALETA_CATEGORICA,
        margin=dict(t=60),
    )
    fig.update_xaxes(color=BRANCO, gridcolor=BORDA, linecolor=BRANCO, title_font=dict(color=BRANCO))
    fig.update_yaxes(color=BRANCO, gridcolor=BORDA, linecolor=BRANCO, title_font=dict(color=BRANCO))
    return fig


def injetar_css() -> None:
    """CSS global: fundo preto, texto branco e reforço de contraste (dark mode)."""
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"], [data-testid="stHeader"], body {{
            background-color: {FUNDO} !important;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: {BRANCO};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {BRANCO} !important;
            font-weight: 700 !important;
        }}

        /* Streamlit deixa metric labels e captions com opacidade reduzida
           por padrão (~60%), o que falha em contraste sobre fundo escuro. */
        [data-testid="stMetricLabel"] {{
            color: {BRANCO} !important;
            opacity: 1 !important;
            font-weight: 600 !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {OURO} !important;
            font-weight: 700 !important;
        }}
        [data-testid="stCaptionContainer"], .stCaption, small {{
            color: {CINZA_CLARO} !important;
            opacity: 1 !important;
        }}

        /* Cartões (containers com borda) */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border: 1px solid {BORDA} !important;
            border-radius: 10px;
            background-color: {FUNDO_CARTAO};
        }}

        /* Barra lateral: fundo preto com borda dourada */
        [data-testid="stSidebar"] {{
            background-color: {FUNDO_CARTAO};
            border-right: 2px solid {OURO};
        }}
        [data-testid="stSidebar"] * {{
            color: {BRANCO} !important;
        }}

        /* Abas / rádio: texto branco, destaque dourado quando selecionado */
        [data-baseweb="tab"] p, [role="radiogroup"] label p {{
            color: {BRANCO} !important;
            font-weight: 600;
        }}
        [data-baseweb="tab-highlight"] {{
            background-color: {OURO} !important;
        }}
        [aria-selected="true"] p {{
            color: {OURO} !important;
        }}

        /* Chips de multiselect: fundo dourado, texto preto (alto contraste
           independente do tema, evita branco-sobre-dourado ilegível) */
        span[data-baseweb="tag"] {{
            background-color: {OURO} !important;
            color: {PRETO} !important;
            border: 1px solid {PRETO} !important;
        }}
        span[data-baseweb="tag"] * {{
            color: {PRETO} !important;
        }}

        /* Campos de texto e selects */
        [data-baseweb="select"] > div, [data-baseweb="input"] > div {{
            background-color: {FUNDO_CARTAO} !important;
            border-color: {BORDA} !important;
            color: {BRANCO} !important;
        }}

        /* Botões */
        .stButton > button, .stDownloadButton > button {{
            color: {PRETO} !important;
            background-color: {OURO} !important;
            border: 1px solid {OURO} !important;
            font-weight: 600;
        }}

        /* Tabelas */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDA};
        }}

        /* Foco visível para navegação por teclado */
        *:focus-visible {{
            outline: 3px solid {OURO} !important;
            outline-offset: 2px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
