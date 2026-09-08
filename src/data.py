"""Leitura e limpeza dos dados de alimentação escolar.

Os dados vêm ao vivo de uma planilha do Google Sheets ("Mapa de controle da
Alimentação Escolar"), uma aba por conjunto. Qualquer edição feita nela aparece
na dashboard na próxima atualização (ver o `ttl` do cache em `main.py`).

A planilha usa um layout de relatório, não uma tabela simples: cada aba tem uma
linha "POLO N" separando os grupos de escolas (em vez de uma coluna Polo), e a
1ª linha real de dados vem colada ao cabeçalho decorativo do Sheets. Além disso,
cada aba concatena um bloco de relatório inteiro por mês (Junho, Julho, ...),
cada um com sua própria linha "Mês de referência: <Mês> - <Ano>" e seus próprios
marcadores de POLO/TOTAL. `_carregar_aba` reconstrói a partir disso uma tabela
normal com Mês e Polo como colunas — novos meses aparecem automaticamente, sem
precisar mexer no código, desde que sigam o mesmo padrão de linha marcadora.
"""

from __future__ import annotations

import re
import urllib.parse

import pandas as pd

REFEICOES = ["Desjejum", "Lanche", "Almoço", "Janta"]

PLANILHA_ID = "1nnJbOgg5OGli_5m-cm90A3qKT2xgZynV-0nwWtbV2iI"

# Nome exibido na dashboard -> nome da aba na planilha.
ABAS = {
    "Unidades Integrais - Ensino Fundamental": "Integrais",
    "Unidades Municipais de Educação Infantil (UMEI) - Integrais": "Base UMEI",
    "Unidades Escolar - Parcial - Ensino Fundamental": "Base Parcial",
}

# Regime de atendimento de cada conjunto (usado para aplicar a Resolução FNDE abaixo).
REGIME_POR_CONJUNTO = {
    "Unidades Integrais - Ensino Fundamental": "Integral",
    "Unidades Municipais de Educação Infantil (UMEI) - Integrais": "Integral",
    "Unidades Escolar - Parcial - Ensino Fundamental": "Parcial",
}

# Quantidade mínima de refeições por categoria/regime, conforme o Art. 14 da
# Resolução CD/FNDE nº 26/2013, Seção II (Da Oferta da Alimentação nas Escolas):
# https://www.gov.br/fnde/pt-br/acesso-a-informacao/legislacao/resolucoes/2013/resolucao-cd-fnde-no-26-de-17-de-junho-de-2013
#   - Creche em tempo integral / tempo integral (Mais Educação): >=3 refeições
#     (cobrindo 70% das necessidades nutricionais diárias).
#   - Creche em período parcial: >=2 refeições (30%).
#   - Educação básica em período parcial (pré-escolar/E.F./E.J.A. fora de creche):
#     a resolução não fixa uma quantidade mínima — 1 refeição já atende a 20% das
#     necessidades, 2 ou mais atende a 30%. Por isso não dá para marcar "abaixo do
#     mínimo" só pela contagem nesse caso (fica como não avaliável).
# IMPORTANTE: isso verifica só a QUANTIDADE de refeições. A resolução também exige
# que elas cubram esses percentuais de necessidades nutricionais diárias, o que não
# dá para conferir com esta planilha (não há dados de calorias/nutrientes).
def _minimo_fnde(categoria: str, regime: str) -> int | None:
    eh_creche = categoria.startswith("Creche")
    if regime == "Integral":
        return 3
    if eh_creche:
        return 2
    return None

# A planilha registra a categoria de cada turma numa coluna própria ("Modalidade"),
# ex.: "(E.F. - 1º e 2º ciclo)", "(Creche)/(1~3 anos)". Cada marcador abaixo é um
# trecho único o suficiente para identificar a categoria mesmo com variações de
# abreviação encontradas na planilha.
_MARCADORES_CATEGORIA = [
    ("0~11", "Creche - 0~11 meses"),
    ("1~3", "Creche - 1~3 anos"),
    ("Pré-escola", "Pré-escolar"),
    ("E.J.A", "E.J.A."),
    ("1º e 2º ciclo", "E.F. - 1º e 2º ciclo"),
    ("3º e 4º ciclo", "E.F. - 3º e 4º ciclo"),
]

# Agrupamento usado nos medidores da dashboard: as categorias de creche/pré-escola
# têm escala bem diferente das de ensino fundamental/EJA, então são exibidas separadas.
GRUPOS_CATEGORIA = {
    "Creche - 0~11 meses": "Creche e pré-escola",
    "Creche - 1~3 anos": "Creche e pré-escola",
    "Pré-escolar": "Creche e pré-escola",
    "E.F. - 1º e 2º ciclo": "E.F. e E.J.A.",
    "E.F. - 3º e 4º ciclo": "E.F. e E.J.A.",
    "E.J.A.": "E.F. e E.J.A.",
}

# Ordem de exibição dos grupos na dashboard, derivada de GRUPOS_CATEGORIA para
# nunca ficar dessincronizada se um grupo novo for adicionado lá.
GRUPOS_ORDEM = list(dict.fromkeys(GRUPOS_CATEGORIA.values()))

_PADRAO_MARCADOR_POLO = re.compile(r"^POLO\s*\d+$", re.IGNORECASE)
_PADRAO_POLO_QUALQUER = re.compile(r"POLO\s*\d+", re.IGNORECASE)
_PADRAO_MES = re.compile(r"Mês de refer[eê]ncia:\s*([A-Za-zÀ-ÿçÇ]+)\s*-\s*(\d{4})", re.IGNORECASE)

# Só para ordenar o filtro de Mês cronologicamente (a ordem alfabética erra:
# "Julho" vem antes de "Junho"). Cobre os 12 meses, então funciona para
# qualquer mês novo que a planilha passar a incluir.
_MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def _extrai_categoria(modalidade: str) -> str:
    """Extrai a categoria (Creche, Pré-escolar, E.F., E.J.A.) do texto de Modalidade."""
    for marcador, categoria in _MARCADORES_CATEGORIA:
        if marcador in modalidade:
            return categoria
    return "Não informado"


def _normaliza_polo(valor: str) -> str:
    valor = str(valor).strip()
    return valor if valor.upper().startswith("POLO") else f"POLO {valor}"


def _para_numero(serie: pd.Series) -> pd.Series:
    """Converte texto vindo da planilha (ex.: '158,47', '-', vazio) para float."""
    limpo = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(limpo, errors="coerce")


def _url_aba(nome_aba: str) -> str:
    """URL de exportação CSV (gviz) de uma aba específica da planilha pública."""
    query = urllib.parse.quote(nome_aba)
    return f"https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/gviz/tq?tqx=out:csv&sheet={query}"


def _extrai_polo_inicial(celula_cabecalho: object) -> str:
    """A 1ª linha da planilha é um cabeçalho decorativo que o Sheets funde com o
    marcador do primeiro polo (ex.: '...Mês de referência: Junho - 2026 POLO 1')."""
    encontrado = _PADRAO_POLO_QUALQUER.search(str(celula_cabecalho))
    return _normaliza_polo(encontrado.group()) if encontrado else "POLO 1"


def _extrai_mes(texto: object) -> str | None:
    """Extrai 'Junho/2026' de uma célula com 'Mês de referência: Junho - 2026'
    (a decorativa da 1ª linha ou a que separa cada bloco de mês). None se não achar."""
    encontrado = _PADRAO_MES.search(str(texto))
    if not encontrado:
        return None
    nome, ano = encontrado.groups()
    return f"{nome.strip().capitalize()}/{ano}"


def ordenar_meses(meses: list[str]) -> list[str]:
    """Ordena valores de Mês (\"Junho/2026\") cronologicamente, não por ordem
    alfabética do nome do mês."""

    def chave(mes: str) -> tuple[int, int]:
        nome, _, ano = mes.rpartition("/")
        return (int(ano) if ano.isdigit() else 0, _MESES_PT.get(nome.strip().lower(), 0))

    return sorted(meses, key=chave)


def _carregar_aba(nome_aba: str) -> pd.DataFrame:
    """Lê uma aba no formato 'mapa de controle' e devolve uma tabela normal,
    com Polo como coluna e Total/Média recalculados a partir dos dados brutos."""
    bruto = pd.read_csv(_url_aba(nome_aba), header=None, dtype=str)

    polo_atual = _extrai_polo_inicial(bruto.iat[0, 1])
    mes_atual = _extrai_mes(bruto.iat[0, 1]) or "Sem mês"
    linhas = []
    for _, linha in bruto.iloc[1:].iterrows():
        escola = linha[1]
        modalidade = linha[2]
        if pd.isna(escola):
            continue
        escola = str(escola).strip()
        if not escola:
            continue
        mes_encontrado = _extrai_mes(escola)
        if mes_encontrado:
            # Início de um novo bloco de mês (ex.: "Mês de referência: Julho - 2026").
            # O polo é reatribuído logo em seguida por um marcador "POLO 1" próprio.
            mes_atual = mes_encontrado
            continue
        if escola.upper().startswith("TOTAL"):
            continue
        if pd.isna(modalidade) and _PADRAO_MARCADOR_POLO.match(escola):
            polo_atual = _normaliza_polo(escola)
            continue

        linhas.append(
            {
                "Mês": mes_atual,
                "Polo": polo_atual,
                "Escola": escola,
                "Categoria": _extrai_categoria(str(modalidade)),
                "Dias letivos": linha[3],
                "Desjejum": linha[4],
                "Lanche": linha[5],
                "Almoço": linha[6],
                "Janta": linha[7],
            }
        )

    df = pd.DataFrame(linhas)
    df["Grupo categoria"] = df["Categoria"].map(lambda c: GRUPOS_CATEGORIA.get(c, "Não informado"))
    df["Dias letivos"] = _para_numero(df["Dias letivos"])
    for col in REFEICOES:
        df[col] = _para_numero(df[col])

    df["Total de refeições"] = df[REFEICOES].sum(axis=1, min_count=1)
    for col in REFEICOES:
        df[f"Média/dia - {col}"] = (df[col] / df["Dias letivos"]).round(1)
    df["Média/dia - Total"] = (df["Total de refeições"] / df["Dias letivos"]).round(1)
    return df


def carregar_combinado() -> pd.DataFrame:
    """Concatena os 3 conjuntos numa única tabela, já com Conjunto/Regime e a
    conformidade com a quantidade mínima de refeições do Art. 14 da Res. FNDE 26/2013."""
    partes = []
    for nome_exibido, nome_aba in ABAS.items():
        parte = _carregar_aba(nome_aba)
        parte.insert(0, "Conjunto", nome_exibido)
        parte.insert(1, "Regime", REGIME_POR_CONJUNTO[nome_exibido])
        partes.append(parte)

    df = pd.concat(partes, ignore_index=True)
    df["Refeições servidas"] = df[REFEICOES].notna().sum(axis=1)
    df["Mínimo FNDE (Art. 14)"] = pd.array(
        [_minimo_fnde(cat, reg) for cat, reg in zip(df["Categoria"], df["Regime"])],
        dtype="Int64",
    )
    df["Conforme FNDE (Art. 14)"] = (
        df["Refeições servidas"] >= df["Mínimo FNDE (Art. 14)"]
    ).astype("boolean")
    return df
