"""Coordenadas geográficas das escolas, buscadas ao vivo no GeoSIG de Niterói
(camadas de Ensino Fundamental e de UMEIs) e casadas com o nome usado na
planilha de alimentação escolar.

O nome de uma mesma escola quase nunca é escrito igual nas duas fontes (a
planilha abrevia diferente do GeoSIG, tem anotações de mês de referência, etc.),
então o casamento é feito em 3 tentativas, da mais para a menos estrita:
nome normalizado idêntico -> um nome é um subconjunto de palavras do outro ->
semelhança aproximada de texto. Escolas sem nenhuma correspondência (algumas
"C.C." — centros comunitários — não estão cadastradas no GeoSIG) ficam de fora
do resultado; quem usa este módulo decide como avisar sobre isso.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata

import pandas as pd
import requests

_FUND_URL = (
    "https://sig.niteroi.rj.gov.br/server/rest/services/"
    "PTG_SME/GESTAO_P_ENSINOFUNDAMENTAL_PUBLICO/FeatureServer/0/query"
)
_UMEI_URL = (
    "https://sig.niteroi.rj.gov.br/server/rest/services/"
    "PTG_SME/GESTAO_P_UMEIS_PUBLICO/FeatureServer/0/query"
)

_STOPWORDS = {"umei", "naei", "cc", "c", "em", "e", "m", "de", "da", "do", "dos", "das", "a", "o"}
_CUTOFF_APROXIMADO = 0.72


def _corrige_mojibake(valor: object) -> object:
    """Parte dos registros do GeoSIG está com o texto duplamente codificado
    (bytes UTF-8 gravados como se fossem Latin-1 há anos, na origem). Reverte
    quando detecta isso; texto já correto simplesmente falha o round-trip e
    é devolvido como veio."""
    if not isinstance(valor, str):
        return valor
    try:
        return valor.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return valor


def _normaliza(nome: str) -> str:
    nome = "".join(ch for ch in nome if unicodedata.category(ch) != "Cf")  # bidi/control
    nome = re.sub(r"\s*\([^)]*\)\s*$", "", nome)  # "(MÊS DE REF.: MAIO)" etc.
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    nome = nome.lower()
    nome = re.sub(r"\bprofessor(a)?\b", "prof", nome)
    nome = re.sub(r"\bdoutor\b", "dr", nome)
    nome = re.sub(r"[^a-z0-9]+", " ", nome).strip()
    return re.sub(r"\s+", " ", nome)


def _buscar_camada(url: str) -> list[dict]:
    params = {
        "where": "1=1",
        "outFields": "tx_escola,tx_endereco,tx_bairro",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "json",
    }
    resposta = requests.get(url, params=params, timeout=30)
    resposta.raise_for_status()
    # O servidor declara charset=UTF-8 no cabeçalho, mas os bytes reais vêm
    # em Latin-1 — decodificar como UTF-8 direto quebra os acentos.
    corpo = json.loads(resposta.content.decode("latin-1"))

    registros = []
    for feature in corpo.get("features", []):
        atributos = {k: _corrige_mojibake(v) for k, v in feature["attributes"].items()}
        geometria = feature.get("geometry") or {}
        if "x" not in geometria or "y" not in geometria:
            continue
        registros.append(
            {
                "nome_gis": atributos.get("tx_escola", ""),
                "endereco": atributos.get("tx_endereco"),
                "bairro": atributos.get("tx_bairro"),
                "latitude": geometria["y"],
                "longitude": geometria["x"],
            }
        )
    return registros


def buscar_registros_gis() -> list[dict]:
    """Busca bruta nas duas camadas do GeoSIG. Não depende dos nomes da
    planilha — só a parte de rede vale a pena cachear por muito tempo; o
    casamento de nomes (barato) fica em `casar_com_escolas`."""
    return _buscar_camada(_FUND_URL) + _buscar_camada(_UMEI_URL)


# Escolas (majoritariamente centros comunitários conveniados) que não estão
# cadastradas no GeoSIG municipal. Endereços informados manualmente e
# geocodificados via Nominatim/OpenStreetMap uma única vez (não é buscado ao
# vivo — são poucas unidades e o endereço delas não muda). As marcadas com "*"
# não têm um resultado no nível do logradouro exato; a geocodificação caiu
# para o centro do bairro, então a posição no mapa é aproximada.
_LOCALIZACOES_MANUAIS: list[dict] = [
    {"nome_gis": "C.C. Alarico de Souza", "endereco": "Estrada Alarico de Souza, 555 - Santa Rosa", "bairro": "Santa Rosa", "latitude": -22.9005939, "longitude": -43.0874818},
    {"nome_gis": "C.C. Amigos do Jacaré", "endereco": "Estrada Frei Orlando, 499 - Jacaré", "bairro": "Jacaré", "latitude": -22.9307243, "longitude": -43.0506751},
    {"nome_gis": "C.C. Anália Franco", "endereco": "Rua Martins Torres, 479 - Santa Rosa", "bairro": "Santa Rosa", "latitude": -22.8995243, "longitude": -43.0965146},
    {"nome_gis": "C.C. Betânia", "endereco": "Avenida Rui Barbosa, 671/679 - São Francisco", "bairro": "São Francisco", "latitude": -22.9125739, "longitude": -43.0795298},
    {"nome_gis": "C.C. Cidade dos Menores", "endereco": "Rua Nossa Senhora das Graças, 474 - Santa Rosa", "bairro": "Santa Rosa", "latitude": -22.8991000, "longitude": -43.0957000},  # *
    {"nome_gis": "C.C. Dom Orione", "endereco": "Avenida Quintino Bocaiuva, s/nº - São Francisco", "bairro": "São Francisco", "latitude": -22.9202005, "longitude": -43.0941350},
    {"nome_gis": "C.C. Eulina Félix", "endereco": "Travessa João Manoel da Silva, 229 A - Cantagalo", "bairro": "Cantagalo", "latitude": -22.9104000, "longitude": -43.0515000},  # *
    {"nome_gis": "C.C. Instituto Doutor March", "endereco": "Rua Desembargador Lima Castro, 235 - Fonseca", "bairro": "Fonseca", "latitude": -22.8866932, "longitude": -43.0862946},
    {"nome_gis": "C.C. Irmã Catarina", "endereco": "Alameda Jandira Froes, 1037 A - São Francisco", "bairro": "São Francisco", "latitude": -22.9133318, "longitude": -43.0979283},
    {"nome_gis": "C.C. Jurujuba", "endereco": "Avenida Carlos Ermelindo Marins, 153 - Jurujuba", "bairro": "Jurujuba", "latitude": -22.9317930, "longitude": -43.1163729},
    {"nome_gis": "C.C. Kairós", "endereco": "Rua 3, lote 18, quadra 59 - Engenho do Mato, Itaipu", "bairro": "Itaipu", "latitude": -22.9524708, "longitude": -43.0235646},
    {"nome_gis": "C.C. Madre Mary Marcellini", "endereco": "Rua Tenente Osório, 30 - Vila Ipiranga, Fonseca", "bairro": "Fonseca", "latitude": -22.8785663, "longitude": -43.0919916},
    {"nome_gis": "C.C. Medalha Milagrosa", "endereco": "Alameda Paris, 56 - Morro do Cavalão, Icaraí", "bairro": "Icaraí", "latitude": -22.9119842, "longitude": -43.1014370},
    {"nome_gis": "C.C. Meimei", "endereco": "Rua das Garças, lote 3, quadra 166 - Piratininga", "bairro": "Piratininga", "latitude": -22.9546613, "longitude": -43.0644997},
    {"nome_gis": "C.C. Minha Querência", "endereco": "Rua Demócrito da Cunha Silveira, lote 14, quadra 64 - Cafubá", "bairro": "Cafubá", "latitude": -22.9336880, "longitude": -43.0758701},
    {"nome_gis": "C.C. Nossa Senhora Aparecida", "endereco": "Rua João Jorge Nemmer, 3 - Ingá", "bairro": "Ingá", "latitude": -22.9032000, "longitude": -43.1221000},  # *
    {"nome_gis": "C.C. Prof. Geraldo C. Albuquerque", "endereco": "Rua General Andrade Neves, 307 - São Domingos", "bairro": "São Domingos", "latitude": -22.9004764, "longitude": -43.1258928},
    {"nome_gis": "C.C. Profª Clélia Rocha", "endereco": "Rua Jean V. Moulliac, 47 - Várzea das Moças", "bairro": "Várzea das Moças", "latitude": -22.9145000, "longitude": -42.9757000},  # *
    {"nome_gis": "C.C. São Vicente de Paulo", "endereco": "Rua Miguel Vieira Ferreira, 147 - Icaraí", "bairro": "Icaraí", "latitude": -22.9072632, "longitude": -43.1055215},
    {"nome_gis": "UMEI Barreto, Therezinha Calil Petrus", "endereco": "Rua Benjamin Constant, 562 - Barreto", "bairro": "Barreto", "latitude": -22.8651080, "longitude": -43.1019297},  # *
    {"nome_gis": "UMEI Jornalista Vilmar Berna", "endereco": "Rua Carlos Ermelindo Martins, 34 - Jurujuba", "bairro": "Jurujuba", "latitude": -22.9338037, "longitude": -43.1198070},  # *
    {"nome_gis": "UMEI Leni dos Santos Oliveira", "endereco": "Ladeira Major Rocha, s/nº - Ponta d'Areia", "bairro": "Ponta d'Areia", "latitude": -22.8806925, "longitude": -43.1233580},
    {"nome_gis": "UMEI São Januário, Edison Rodrigues", "endereco": "Rua São Januário, 318 - Fonseca", "bairro": "Fonseca", "latitude": -22.8762296, "longitude": -43.0867204},
]


def registros_manuais() -> list[dict]:
    """Escolas sem correspondência no GeoSIG, com endereço cadastrado à mão
    (ver `_LOCALIZACOES_MANUAIS`). Não faz nenhuma chamada de rede."""
    return list(_LOCALIZACOES_MANUAIS)


def _casar_nomes(nomes: list[str], registros: list[dict]) -> dict[str, dict]:
    normalizados = [(_normaliza(r["nome_gis"]), r) for r in registros]
    por_norma = dict(normalizados)
    normas_disponiveis = [n for n, _ in normalizados]

    casamentos: dict[str, dict] = {}
    for nome in nomes:
        alvo = _normaliza(nome)
        registro = por_norma.get(alvo)

        if registro is None:
            palavras_alvo = set(alvo.split()) - _STOPWORDS
            if len(palavras_alvo) >= 2:
                for norma, candidato in normalizados:
                    palavras_gis = set(norma.split()) - _STOPWORDS
                    menor, maior = sorted([palavras_alvo, palavras_gis], key=len)
                    if len(menor) >= 2 and menor <= maior:
                        registro = candidato
                        break

        if registro is None:
            proximas = difflib.get_close_matches(
                alvo, normas_disponiveis, n=1, cutoff=_CUTOFF_APROXIMADO
            )
            if proximas:
                registro = por_norma[proximas[0]]

        if registro is not None:
            casamentos[nome] = registro
    return casamentos


def casar_com_escolas(nomes: list[str], registros: list[dict]) -> pd.DataFrame:
    """Casa os nomes de escola da planilha com os registros do GeoSIG.
    Devolve uma linha por escola encontrada (Escola, endereco, bairro,
    latitude, longitude); as sem correspondência simplesmente não aparecem."""
    casamentos = _casar_nomes(nomes, registros)
    linhas = [
        {
            "Escola": nome,
            "endereco": registro["endereco"],
            "bairro": registro["bairro"],
            "latitude": registro["latitude"],
            "longitude": registro["longitude"],
        }
        for nome, registro in casamentos.items()
    ]
    return pd.DataFrame(linhas, columns=["Escola", "endereco", "bairro", "latitude", "longitude"])
