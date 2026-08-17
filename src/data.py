"""Construção e limpeza dos 3 conjuntos de dados de alimentação escolar."""

from __future__ import annotations

import numpy as np
import pandas as pd

REFEICOES = ["Desjejum", "Lanche", "Almoço", "Janta"]


def _normaliza_polo(valor: str) -> str:
    valor = str(valor).strip()
    return valor if valor.upper().startswith("POLO") else f"POLO {valor}"


def _completa_medias(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que Total de refeições e Média/dia existam, calculando quando faltarem."""
    df = df.copy()
    if "Total de refeições" not in df.columns:
        df["Total de refeições"] = df[REFEICOES].sum(axis=1, min_count=1)
    for col in REFEICOES:
        media_col = f"Média/dia - {col}"
        if media_col not in df.columns:
            df[media_col] = df[col] / df["Dias letivos"]
    if "Média/dia - Total" not in df.columns:
        df["Média/dia - Total"] = df["Total de refeições"] / df["Dias letivos"]
    return df


def carregar_escolas_regulares() -> pd.DataFrame:
    """Conjunto 1: escolas municipais (E.M.) com série completa de refeições."""
    df = pd.DataFrame(
        [
            ["1", "E.M. Ayrton Senna", 17, 2694, 2696, 2697, 2565, 10652, 158.47, 158.59, 158.65, 150.88, 626.59],
            ["2", "E.M. Djalma Coutinho de Oliveira", 18, 2187, 3980, 3980, 3980, 14127, 121.50, 221.11, 221.11, 221.11, 784.83],
            ["2", "E.M. Dom José Pereira Alves", 18, 2140, 2140, 2140, 2140, 8560, 118.89, 118.89, 118.89, 118.89, 475.56],
            ["3", "E.M. Antineia Silveira Miranda", 20, 1557, 3389, 3467, 1764, 10177, 77.85, 169.45, 173.35, 88.20, 508.85],
            ["3", "E.M. Demenciano Antônio de Moura (Pré-escolar)", 20, 484, 491, 479, 479, 1933, 24.20, 24.55, 23.95, 23.95, 96.65],
            ["3", "E.M. Demenciano Antônio de Moura (E.F. - 1º e 2º ciclo)", 20, 2817, 2829, 2825, 2818, 11289, 140.85, 141.45, 141.25, 140.90, 564.45],
            ["4", "E.M. Prof. Bolíva de Lima Gaêtho", 19, 1526, 1569, 2727, 1069, 6891, 80.32, 82.58, 143.53, 56.26, 362.68],
            ["5", "E.M. Profᵃ. Maria Felisberta Baptisa da Trindade", 19, 5170, 5210, 5210, 5210, 20800, 272.11, 274.21, 274.21, 274.21, 1094.74],
            ["6", "E.M. Profᵃ. Elvira Lúcia Esteves de Vaconcelos", 17, 2713, 2402, 2567, 2260, 9942, 159.59, 141.29, 151.00, 132.94, 584.82],
        ],
        columns=[
            "Polo", "Escola", "Dias letivos", "Desjejum", "Lanche", "Almoço", "Janta",
            "Total de refeições", "Média/dia - Desjejum", "Média/dia - Lanche",
            "Média/dia - Almoço", "Média/dia - Janta", "Média/dia - Total",
        ],
    )
    df["Polo"] = df["Polo"].map(_normaliza_polo)
    return df


def carregar_umei_creches() -> pd.DataFrame:
    """Conjunto 2: UMEIs, creches e centros comunitários (sem Janta na maioria)."""
    dados = [
        # POLO 1
        ["POLO 1", "UMEI Maria Vitória Ayres Neves (Creche)/(1~3 anos)", 19, 538, 538, 750, 585],
        ["POLO 1", "UMEI Maria Vitória Ayres Neves (Pré-escolar)", 19, 538, 538, 760, 605],
        ["POLO 1", "UMEI Professor Irio Molinari (Creche)/(1~3 anos)", 19, 687, 687, 687, 548],
        ["POLO 1", "UMEI Professor Irio Molinari (Pré-escolar)", 19, 1067, 1067, 1067, 865],
        ["POLO 1", "UMEI Alberto de Oliveira (Creche)/(1~3 anos)", 19, 194, 187, 194, 187],
        ["POLO 1", "UMEI Alberto de Oliveira (Pré-escolar)", 19, 872, 852, 872, 852],
        ["POLO 1", "UMEI Antônio Vieira da Rocha (Creche)/(0~11 meses)", 18, 125, 125, 125, 105],
        ["POLO 1", "UMEI Antônio Vieira da Rocha (Creche)/(1~3 anos)", 18, 1361, 1346, 1365, 1124],
        ["POLO 1", "UMEI Antônio Vieira da Rocha (Pré-escolar)", 18, 1010, 1010, 1013, 838],
        ["POLO 1", "UMEI Hilka de Araújo Peçanha (Creche)/(1~3 anos)", 19, 419, 448, 645, 348],
        ["POLO 1", "UMEI Hilka de Araújo Peçanha (Pré-escolar)", 19, 872, 820, 1288, 726],
        ["POLO 1", "UMEI Rosalda Paim (Creche)/(1~3 anos)", 19, 703, 703, 703, 592],
        ["POLO 1", "UMEI Rosalda Paim (Pré-escolar)", 19, 759, 759, 759, 635],
        ["POLO 1", "UMEI Profª. Denise Mendes Cardia (Creche)/(1~3 anos)", 18, 1236, 1236, 1266, 1054],
        ["POLO 1", "UMEI Profª. Denise Mendes Cardia (Pré-escolar)", 18, 1456, 1460, 1426, 1226],
        ["POLO 1", "UMEI Portugal Pequeno (Pré-escolar)", 19, 2037, 1965, 1969, 1643],
        ["POLO 1", "C.C. Nossa Senhora Aparecida (Creche)/(1~3 anos)", 20, 1157, 1214, 1220, 1196],
        ["POLO 1", "C.C. Nossa Senhora Aparecida (Pré-escolar)", 20, 1652, 1741, 1724, 1732],
        ["POLO 1", "C.C. Prof. Geraldo C. Albuquerque (APADA) (Creche)/(0~11 meses)", 19, 118, 111, 111, 102],
        ["POLO 1", "C.C. Prof. Geraldo C. Albuquerque (APADA) (Creche)/(1~3 anos)", 19, 924, 873, 873, 776],
        ["POLO 1", "C.C. Prof. Geraldo C. Albuquerque (APADA) (Pré-escolar)", 19, 332, 315, 630, 562],
        ["POLO 1", "UMEI Leni dos Santos Oliveira (Creche)/(1~3 anos)", 18, 1109, 1128, 1542, 920],
        # POLO 2
        ["POLO 2", "UMEI Profª. Regina Leite Garcia (Creche)/(1~3 anos)", 20, 1285, 1403, 1874, 1703],
        ["POLO 2", "UMEI Profª. Regina Leite Garcia (Pré-escolar)", 20, 1229, 1525, 2165, 1790],
        ["POLO 2", "UMEI Profª. Marilza da Conceição Rocha Medina (Creche)/(0~11 m.)", 19, 81, 81, 81, 68],
        ["POLO 2", "UMEI Profª. Marilza da Conceição Rocha Medina (Creche)/(1~3 a.)", 19, 543, 543, 543, 456],
        ["POLO 2", "UMEI Profª. Marilza da Conceição Rocha Medina (Pré-escolar)", 19, 643, 643, 643, 533],
        ["POLO 2", "UMEI Renata Gonçalves Magaldi (Creche)/(1~3 anos)", 19, 770, 773, 1241, 1189],
        ["POLO 2", "UMEI Renata Gonçalves Magaldi (Pré-escolar)", 19, 691, 688, 1252, 1178],
        ["POLO 2", "NAEI Vila Ipiranga (Creche)/(0~11 meses)", 19, 89, 89, 89, 89],
        ["POLO 2", "NAEI Vila Ipiranga (Creche)/(1~3 anos)", 19, 1403, 1489, 1747, 1501],
        ["POLO 2", "NAEI Vila Ipiranga (Pré-escolar)", 19, 1608, 1683, 2263, 1697],
        ["POLO 2", "UMEI Hermógenes Reis (Creche)/(1~3 anos)", 20, 390, 452, 579, 344],
        ["POLO 2", "UMEI Hermógenes Reis (Pré-escolar)", 20, 4006, 3753, 4353, 2952],
        ["POLO 2", "UMEI Marly Sarney (Creche)/(0~11 meses)", 19, 194, 194, 194, 194],
        ["POLO 2", "UMEI Marly Sarney (Creche)/(1~3 anos)", 19, 1408, 1408, 1408, 1408],
        ["POLO 2", "UMEI Marly Sarney (Pré-escolar)", 19, 710, 710, 1172, 710],
        ["POLO 2", "C.C. Instituto Doutor March (Creche)/(1~3 anos)", 19, 1417, 1486, 1839, 1523],
        ["POLO 2", "C.C. Instituto Doutor March (Pré-escolar)", 19, 1296, 1381, 1906, 1556],
        ["POLO 2", "C.C. Madre Mary Marcellini (Creche)/(1~3 anos)", 19, 1109, 1569, 1741, 1542],
        ["POLO 2", "C.C. Madre Mary Marcellini (Pré-escolar)", 19, 1050, 1432, 1603, 1446],
        ["POLO 2", "UMEI São Januário - Edison Rodrigues (Creche)/(1~3 anos)", 19, 1732, 1732, 1732, 1382],
        ["POLO 2", "UMEI São Januário - Edison Rodrigues (Pré-escolar)", 19, 210, 210, 210, 210],
        # POLO 3
        ["POLO 3", "UMEI Zilda Arns (Creche)/(0~11 meses)", 20, 88, 97, 196, 184],
        ["POLO 3", "UMEI Zilda Arns (Creche)/(1~3 anos)", 20, 1398, 1500, 3552, 3377],
        ["POLO 3", "UMEI Zilda Arns (Pré-escolar)", 20, 973, 1052, 2582, 2454],
        ["POLO 3", "NAEI Sebastião Luiz Tatagiba (Pré-escolar)", 18, 1373, 1325, 1374, 1024],
        ["POLO 3", "UMEI Alberto Brandão (Creche)/(1~3 anos)", 18, 1083, 1099, 1102, 1109],
        ["POLO 3", "UMEI Alberto Brandão (Pré-escolar)", 18, 1606, 1647, 1660, 1675],
        ["POLO 3", "UMEI Prof. Nilo Neves (Creche)/(1~3 anos)", 18, 1959, 1960, 2064, 1707],
        ["POLO 3", "UMEI Prof. Nilo Neves (Pré-escolar)", 18, 1985, 1981, 2157, 1797],
        ["POLO 3", "UMEI Profª. Maria José Mansur Barbosa (Creche)/(1~3 anos)", 19, 129, 129, 129, 129],
        ["POLO 3", "UMEI Profª. Maria José Mansur Barbosa (Pré-escolar)", 19, 491, 491, 491, 491],
        ["POLO 3", "UMEI Jorge Nassim Vieira Najjar (Creche)/(1~3 anos)", 20, 261, 233, 461, 188],
        ["POLO 3", "UMEI Jorge Nassim Vieira Najjar (Pré-escolar)", 20, 1374, 1064, 2206, 1104],
        ["POLO 3", "UMEI Vice-Prefeito Luiz Eduardo Travassos do Carmo (Creche)/(0~11 m.)", 18, 69, 81, 76, 48],
        ["POLO 3", "UMEI Vice-Prefeito Luiz Eduardo Travassos do Carmo (Creche)/(1~3 a.)", 18, 918, 879, 1380, 941],
        ["POLO 3", "UMEI Vice-Prefeito Luiz Eduardo Travassos do Carmo (Pré-escolar)", 18, 1268, 1133, 1626, 1097],
        ["POLO 3", "C.C. São Vicente de Paulo (Creche)/(1~3 anos)", 18, 418, 525, 684, 500],
        ["POLO 3", "C.C. São Vicente de Paulo (Pré-escolar)", 18, 628, 1022, 1330, 978],
        ["POLO 3", "C.C. Irmã Catarina (Creche)/(1~3 anos)/(MÊS DE REF.: ABRIL)", 19, 320, 566, 741, 655],
        ["POLO 3", "C.C. Irmã Catarina (Pré-escolar)/(MÊS DE REF.: ABRIL)", 19, 482, 815, 1129, 1032],
        ["POLO 3", "C.C. Medalha Milagrosa (Creche)/(1~3 anos)", 20, 366, 560, 1028, 992],
        ["POLO 3", "C.C. Medalha Milagrosa (Pré-escolar)", 20, 382, 563, 1084, 1048],
        # POLO 4
        ["POLO 4", "UMEI Elenir Ramos Meireles (Creche)/(1~3 anos)/(MÊS DE REF.: SET/25)", 23, 514, 514, 514, 415],
        ["POLO 4", "UMEI Elenir Ramos Meireles (Pré-escolar)", 23, 723, 723, 723, 588],
        ["POLO 4", "UMEI Gabriela Mistral (Creche)/(0~11 meses)", 19, 479, 479, 479, 479],
        ["POLO 4", "UMEI Gabriela Mistral (Creche)/(1~3 anos)", 19, 1368, 1368, 1368, 1368],
        ["POLO 4", "UMEI Gabriela Mistral (Pré-escolar)", 19, 813, 813, 813, 813],
        ["POLO 4", "UMEI Profª. Lisaura Machado Ruas (Creche)/(0~11 meses)", 20, 61, 61, 61, 56],
        ["POLO 4", "UMEI Profª. Lisaura Machado Ruas (Creche)/(1~3 anos)", 20, 664, 604, 786, 669],
        ["POLO 4", "UMEI Profª. Lisaura Machado Ruas (Pré-escolar)", 20, 590, 542, 654, 555],
        ["POLO 4", "UMEI Almir Garcia da Silva (Creche)/(1~3 anos)", 18, 166, 155, 218, 280],
        ["POLO 4", "UMEI Almir Garcia da Silva (Pré-escolar)", 18, 750, 707, 1192, 1161],
        ["POLO 4", "UMEI Governador Eduardo Campos (Creche)/(1~3 anos)/(REF.: MAIO)", 21, 1308, 1308, 1328, 1308],
        ["POLO 4", "UMEI Governador Eduardo Campos (Pré-escolar)/(MÊS DE REF.: MAIO)", 21, 1600, 1600, 1620, 1600],
        ["POLO 4", "UMEI Vinícius de Moraes (Creche)/(1~3 anos)", 19, 1807, 1357, 1825, 1357],
        ["POLO 4", "UMEI Vinícius de Moraes (Pré-escolar)", 19, 1745, 1277, 1763, 1277],
        ["POLO 4", "C.C. Profª. Clélia Rocha (Creche)/(1~3 anos)", 20, 571, 571, 806, 571],
        ["POLO 4", "C.C. Profª. Clélia Rocha (Pré-escolar)", 20, 718, 718, 958, 818],
        ["POLO 4", "C.C. Eulina Félix (Creche)/(1~3 anos)", 20, 499, 571, 338, 522],
        ["POLO 4", "C.C. Eulina Félix (Pré-escolar)", 20, 480, 528, 616, 477],
        ["POLO 4", "C.C. Eulina Félix (E.F. - 1º e 2º ciclo)", 20, None, None, 263, None],
        # POLO 5
        ["POLO 5", "UMEI Jacy Pacheco (Creche)/(1~3 anos)", 20, 950, 950, 950, 950],
        ["POLO 5", "UMEI Jacy Pacheco (Pré-escolar)", 20, 1564, 1564, 1564, 1564],
        ["POLO 5", "UMEI Jacy Pacheco (E.F. - 1º e 2º ciclo)", 20, 2956, 2951, 3659, 1963],
        ["POLO 5", "UMEI Neuza Brizola (Creche)/(1~3 anos)", 19, 838, 838, 838, 692],
        ["POLO 5", "UMEI Neuza Brizola (Pré-escolar)", 19, 951, 951, 951, 784],
        ["POLO 5", "UMEI Prof. Iguatemi Coquinot de Alcântara Nunes (Creche)/(0~11 meses)", 19, 103, 103, 103, 103],
        ["POLO 5", "UMEI Prof. Iguatemi Coquinot de Alcântara Nunes (Creche)/(1~3 anos)", 19, 1039, 1039, 1039, 1039],
        ["POLO 5", "UMEI Prof. Iguatemi Coquinot de Alcântara Nunes (Pré-escolar)", 19, 694, 694, 694, 694],
        ["POLO 5", "C.C. Anália Franco (Creche)/(0~11 meses)", 19, 248, 248, 248, 248],
        ["POLO 5", "C.C. Anália Franco (Creche)/(1~3 anos)", 19, 1016, 1042, 1016, 1042],
        ["POLO 5", "C.C. Anália Franco (Pré-escolar)", 19, 711, 738, 711, 738],
        ["POLO 5", "C.C. Alarico de Souza (Creche)/(1~3 anos)", 15, 439, 520, 520, 439],
        ["POLO 5", "C.C. Alarico de Souza (Pré-escolar)", 15, 432, 509, 509, 432],
        ["POLO 5", "C.C. Meimei (Creche)/(1~3 anos)", 19, 553, 535, 553, 605],
        ["POLO 5", "C.C. Meimei (Pré-escolar)", 19, 776, 742, 1348, 762],
        ["POLO 5", "C.C. Minha Querência (Creche)/(1~3 anos)", 18, 1158, 1229, 1160, 1155],
        ["POLO 5", "C.C. Minha Querência (Pré-escolar)", 18, 1393, 1466, 1392, 1390],
        ["POLO 5", "UMEI Barreto - Therezinha Calil (Creche)/(1~3 anos)", 18, 2037, 2037, 1703, 2037],
        ["POLO 5", "UMEI Barreto - Therezinha Calil (Pré-escolar)", 18, 424, 424, 365, 424],
        # POLO 6
        ["POLO 6", "UMEI Geraldo Montedônio Bezerra de Menezes (Creche)/(1~3 anos)/(Ref.: Maio)", 19, 1137, 1122, 1122, 1122],
        ["POLO 6", "UMEI Geraldo Montedônio Bezerra de Menezes (Pré-escolar)/(Ref.: Maio)", 19, 1170, 1241, 1183, 1183],
        ["POLO 6", "UMEI Senador Vasconcelos Torres (Creche)/(1~3 anos)", 20, 586, 99, 586, 487],
        ["POLO 6", "UMEI Senador Vasconcelos Torres (Pré-escolar)", 20, 1072, 191, 1072, 881],
        ["POLO 6", "UMEI Darcy Ribeiro (Creche)/(1~3 anos)", 20, 2321, 2321, 2321, 2321],
        ["POLO 6", "UMEI Darcy Ribeiro (Pré-escolar)", 20, 2732, 2732, 2732, 2732],
        ["POLO 6", "UMEI Darcy Ribeiro (E.F. - 1º e 2º ciclo)", 20, 1024, 1052, 1279, 1052],
        ["POLO 6", "UMEI Maria Luiza da Cunha Sampaio (Creche)/(1~3 anos)", 20, 108, 95, 190, 139],
        ["POLO 6", "UMEI Maria Luiza da Cunha Sampaio (Pré-escolar)", 20, 823, 795, 1334, 958],
        ["POLO 6", "UMEI Profª. Margareth Flores (Creche)/(0~11 meses)", 19, 153, 153, 153, 153],
        ["POLO 6", "UMEI Profª. Margareth Flores (Creche)/(1~3 anos)", 19, 2096, 2096, 2096, 2096],
        ["POLO 6", "UMEI Profª. Margareth Flores (Pré-escolar)", 19, 1312, 1312, 1312, 1312],
        ["POLO 6", "C.C. Betânia (Creche)/(1~3 anos)", 30, 862, 1579, 1564, 1561],
        ["POLO 6", "C.C. Betânia (Pré-escolar)", 30, 1759, 1873, 1860, 1847],
        ["POLO 6", "C.C. Betânia (E.F. - 1º e 2º ciclo)", 19, 823, None, None, None],
        ["POLO 6", "C.C. Cidade dos Menores (Creche)/(1~3 anos)", 20, 689, 689, 689, 689],
        ["POLO 6", "C.C. Cidade dos Menores (Pré-escolar)", 20, 1073, 1073, 1073, 1073],
        ["POLO 6", "C.C. Dom Orione (Creche)/(1~3 anos)", 18, 1841, 1525, 1905, 1555],
        ["POLO 6", "C.C. Dom Orione (Pré-escolar)", 18, 2750, 2278, 2798, 2303],
        ["POLO 6", "C.C. Jurujuba (Creche)/(1~3 anos)", 20, 483, 558, 851, 469],
        ["POLO 6", "C.C. Jurujuba (Pré-escolar)", 20, 420, 508, 807, 408],
        ["POLO 6", "UMEI Jornalista Vilmar Berna (Creche)/(1~3 anos)", 19, 1774, 1559, 1940, 1732],
        ["POLO 6", "UMEI Jornalista Vilmar Berna (Pré-escolar)", 19, 254, 208, 284, 233],
        # POLO 7
        ["POLO 7", "UMEI Lizete Fernandes Maciel (Creche)/(1~3 anos)", 19, 820, 820, 820, 820],
        ["POLO 7", "UMEI Lizete Fernandes Maciel (Pré-escolar)", 19, 941, 941, 941, 941],
        ["POLO 7", "UMEI Olga Benário Prestes (Creche)/(1~3 anos)", 19, 1179, 1179, 1179, 992],
        ["POLO 7", "UMEI Olga Benário Prestes (Pré-escolar)", 19, 1109, 1109, 1109, 929],
        ["POLO 7", "UMEI Profª. Áurea Trindade Pimentel de Menezes (Creche)/(1~3 anos)", 19, 287, 287, 467, 226],
        ["POLO 7", "UMEI Profª. Áurea Trindade Pimentel de Menezes (Pré-escola)/(Ref.: Abril)", 19, 862, 862, 1521, 633],
        ["POLO 7", "UMEI Profª. Nina Rita Torres (Creche)/(1~3 anos)", 18, 557, 557, 557, 557],
        ["POLO 7", "UMEI Profª. Nina Rita Torres (Pré-escolar)", 18, 598, 598, 598, 598],
        ["POLO 7", "UMEI Profª. Odete Rosa da Mota (Creche)/(0~11 meses)", 18, 181, 179, 181, 151],
        ["POLO 7", "UMEI Profª. Odete Rosa da Mota (Creche)/(1~3 anos)", 18, 1681, 1689, 1689, 1396],
        ["POLO 7", "UMEI Profª. Odete Rosa da Mota (Pré-escolar)", 18, 658, 658, 658, 545],
        ["POLO 7", "UMEI Doutor Paulo César Pimentel (Creche)/(1~3 anos)", 18, 1298, 1118, 1388, 974],
        ["POLO 7", "UMEI Doutor Paulo César Pimentel (Pré-escolar)", 18, 1382, 1112, 2192, 1382],
        ["POLO 7", "NAEI Ângela Fernandes (Creche)/(1~3 anos)", 18, 637, 619, 637, 532],
        ["POLO 7", "NAEI Ângela Fernandes (Pré-escolar)", 18, 462, 445, 462, 385],
        ["POLO 7", "C.C. Amigos do Jacaré (Creche)/(1~3 anos)", 20, 395, 395, 935, 790],
        ["POLO 7", "C.C. Amigos do Jacaré (Pré-escolar)", 20, 377, 377, 918, 748],
        ["POLO 7", "C.C. Kairós (Creche)/(1~3 anos)", 19, 448, 382, 1213, 831],
        ["POLO 7", "C.C. Kairós (Pré-escolar)", 19, 489, 415, 1239, 862],
    ]
    df = pd.DataFrame(dados, columns=["Polo", "Escola", "Dias letivos", *REFEICOES])
    df["Polo"] = df["Polo"].map(_normaliza_polo)
    return _completa_medias(df)


def carregar_ensino_fundamental() -> pd.DataFrame:
    """Conjunto 3: escolas de ensino fundamental/E.J.A. por polo, com dados faltantes."""
    df = pd.DataFrame(
        [
            ["POLO 1", "E. M. Dr. Alberto Francisco Torres (E.F. - 1º e 2º ciclo)", 18, np.nan, 3806, 3813, np.nan, 7619, np.nan, 211.44, 211.83, np.nan, 423.28],
            ["POLO 1", "E. M. Dr. Alberto Francisco Torres (E.F. - 3º e 4º ciclo)", 18, 2695, 2716, 2722, np.nan, 8133, 149.72, 150.89, 151.22, np.nan, 451.83],
            ["POLO 1", "E. M. Dr. Alberto Francisco Torres (E.J.A.)", 18, np.nan, 1843, np.nan, 1821, 3664, np.nan, 102.39, np.nan, 101.17, 203.56],
            ["POLO 1", "E.M. Maestro Heitor Villa-Lobos (E.F. - 1º e 2º ciclo)", 20, 150, 3390, 2720, np.nan, 6260, 7.50, 169.50, 136.00, np.nan, 313.00],
            ["POLO 1", "E.M. Maestro Heitor Villa-Lobos (E.F. - 3º e 4º ciclo)", 20, 1685, np.nan, 2515, np.nan, 4200, 84.25, np.nan, 125.75, np.nan, 210.00],
            ["POLO 1", "E.M. Maestro Heitor Villa-Lobos (E.J.A.)", 20, 10, 268, np.nan, 268, 546, 0.50, 13.40, np.nan, 13.40, 27.30],
            ["POLO 1", "E.M. Nossa Senhora da Penha (E.F. - 1º e 2º ciclo)", 19, 2230, 2629, 3937, np.nan, 8796, 117.37, 138.37, 207.21, np.nan, 462.95],
            ["POLO 1", "E.M. Santos Dumont (E.F. - 1º e 2º ciclo) (MÊS DE REF.: MAIO)", 21, np.nan, 3155, 3285, np.nan, 6440, np.nan, 150.24, 156.43, np.nan, 306.67],
            ["POLO 1", "E.M. Santos Dumont (E.F. - 3º e 4º ciclo) (MÊS DE REF.: MAIO)", 21, 2970, np.nan, 3145, np.nan, 6115, 141.43, np.nan, 149.76, np.nan, 291.19],
            ["POLO 2", "E.M. Ernani Moreira Franco (Creche)/(1~3 anos)", 19, 62, 114, 168, np.nan, 344, 3.26, 6.00, 8.84, np.nan, 18.11],
            ["POLO 2", "E.M. Ernani Moreira Franco (Pré-escolar)", 19, 247, 367, 614, np.nan, 1228, 13.00, 19.32, 32.32, np.nan, 64.63],
            ["POLO 2", "E.M. Ernani Moreira Franco (E.F. - 1º e 2º ciclo)", 19, 3050, 3433, 7443, np.nan, 13926, 160.53, 180.68, 391.74, np.nan, 732.95],
            ["POLO 2", "E.M. Jacinta Medela (E.F. - 1º e 2º ciclo)", 19, 2892, 2783, 5700, np.nan, 11375, 152.21, 146.47, 300.00, np.nan, 598.68],
            ["POLO 2", "E.M. Dr. Antônio Coutinho de Azevedo (E.F.- 1º e 2º ciclo)", 19, 3061, 3524, 7551, np.nan, 14136, 161.11, 185.47, 397.42, np.nan, 744.00],
            ["POLO 2", "E. M. Noronha Santos (Creche)/(1~3 anos)", 19, 447, 447, 447, 447, 1788, 23.53, 23.53, 23.53, 23.53, 94.11],
            ["POLO 2", "E. M. Noronha Santos (Pré-escolar)", 19, 751, 751, 751, 751, 3004, 39.53, 39.53, 39.53, 39.53, 158.11],
            ["POLO 2", "E. M. Noronha Santos (E.F. - 1º e 2º ciclo)", 19, 1281, 884, 2165, np.nan, 4330, 67.42, 46.53, 113.95, np.nan, 227.89],
            ["POLO 2", "E.M. Rachide da Glória Salim Saker (E.F. - 3º e 4º ciclo)", 19, 4088, 4088, 7583, np.nan, 15759, 215.16, 215.16, 399.11, np.nan, 829.42],
            ["POLO 2", "UMEI Julieta Botelho (Creche)/(1~3 anos)", 17, 273, 503, 776, np.nan, 1552, 16.06, 29.59, 45.65, np.nan, 91.29],
            ["POLO 2", "UMEI Julieta Botelho (Pré-escolar)", 17, 431, 519, 950, np.nan, 1900, 25.35, 30.53, 55.88, np.nan, 111.76],
            ["POLO 3", "E.M. Paulo Freire (E.F. - 1º e 2º ciclo)", 21, np.nan, 6871, 7142, np.nan, 14013, np.nan, 327.19, 340.10, np.nan, 667.29],
            ["POLO 3", "E.M. Paulo Freire (E.F. - 3º e 4º ciclo)", 21, 10273, np.nan, 11217, np.nan, 21490, 489.19, np.nan, 534.14, np.nan, 1023.33],
            ["POLO 3", "E.M. Sebastiana Gonçalves Pinho (E.F. - 1º e 2º ciclo)", 16, 2026, 2025, 3643, np.nan, 7694, 126.63, 126.56, 227.69, np.nan, 480.88],
            ["POLO 3", "E.M. Vila Costa Monteiro (Creche)/(1~3 anos)", 20, np.nan, 251, np.nan, np.nan, 251, np.nan, 12.55, np.nan, np.nan, 12.55],
            ["POLO 3", "E.M. Vila Costa Monteiro (Pré-escolar)", 20, 585, 1007, 1685, np.nan, 3277, 29.25, 50.35, 84.25, np.nan, 163.85],
            ["POLO 3", "E.M. Vila Costa Monteiro (E.F. - 1º e 2º ciclo)", 20, 1180, 861, 3384, np.nan, 5425, 59.00, 43.05, 169.20, np.nan, 271.25],
            ["POLO 3", "E.M. José de Anchieta (E.F. - 1º e 2º ciclo)", 19, 1121, 3605, 4205, np.nan, 8931, 59.00, 189.74, 221.32, np.nan, 470.05],
            ["POLO 3", "E.M. José de Anchieta (E.F. - 3º e 4º ciclo)", 19, 1937, np.nan, 2141, np.nan, 4078, 101.95, np.nan, 112.68, np.nan, 214.63],
            ["POLO 3", "E.M. Prof. Maria de Lourdes Barbosa Santos (E.F. - 1º e 2º ciclo)", 19, 1005, 1954, 3777, np.nan, 6736, 52.89, 102.84, 198.79, np.nan, 354.53],
            ["POLO 4", "E.M. Diógenes Ribeiro de Mendonça (Pré-escolar)", 19, 97, 101, 178, np.nan, 376, 5.11, 5.32, 9.37, np.nan, 19.79],
            ["POLO 4", "E.M. Diógenes Ribeiro de Mendonça (E.F. - 1º e 2º ciclo)", 19, 815, 993, 1471, np.nan, 3279, 42.89, 52.26, 77.42, np.nan, 172.58],
            ["POLO 4", "E.M. Felisberto de Carvalho (E.F. - 1º e 2º ciclo)", 18, 2251, 2344, 4650, np.nan, 9245, 125.06, 130.22, 258.33, np.nan, 513.61],
            ["POLO 4", "E.M. Honorina de Carvalho (E.F. - 3º e 4º ciclo)", 18, 2480, 2700, 3480, np.nan, 8660, 137.78, 150.00, 193.33, np.nan, 481.11],
            ["POLO 4", "E.M. Prof. Horácio Pacheco (E.F. - 1º e 2º ciclo)", 18, 2250, 4645, 4595, np.nan, 11490, 125.00, 258.06, 255.28, np.nan, 638.33],
            ["POLO 4", "E.M. Sítio do Ipê (E.F. - 1º e 2º ciclo)", 18, 1882, 1892, 3531, np.nan, 7305, 104.56, 105.11, 196.17, np.nan, 405.83],
            ["POLO 4", "E.M. Vera Lúcia Machado (E.F. - 1º e 2º ciclo)", 18, 4600, 5060, 8450, np.nan, 18110, 255.56, 281.11, 469.44, np.nan, 1006.11],
            ["POLO 4", "E.M. Levi Carneiro (E.F. - 1º e 2º ciclo)", 24, np.nan, 6142, 5744, np.nan, 11886, np.nan, 255.92, 239.33, np.nan, 495.25],
            ["POLO 4", "E.M. Levi Carneiro (E.F. - 3º e 4º ciclo)", 24, 6068, np.nan, 6567, np.nan, 12635, 252.83, np.nan, 273.63, np.nan, 526.46],
            ["POLO 5", "E.M. Adelino Magalhães (Creche)/(1~3 anos)/(MÊS DE REF.: MAIO)", 21, 576, 532, 587, np.nan, 1695, 27.43, 25.33, 27.95, np.nan, 80.71],
            ["POLO 5", "E.M. Adelino Magalhães (Pré-escolar)/(MÊS DE REF.: MAIO)", 21, 684, 602, 687, np.nan, 1973, 32.57, 28.67, 32.71, np.nan, 93.95],
            ["POLO 5", "E.M. Adelino Magalhães (E.F. - 1º e 2º ciclo)/(MÊS DE REF.: MAIO)", 21, 5286, 5467, 5153, np.nan, 15906, 251.71, 260.33, 245.38, np.nan, 757.43],
            ["POLO 5", "E.M. Altivo César (E.F. - 3º e 4º ciclo)", 19, 4220, 4475, 7430, np.nan, 16125, 222.11, 235.53, 391.05, np.nan, 848.68],
            ["POLO 5", "E.M. Altivo César (E.J.A.)", 19, np.nan, 460, np.nan, 965, 1425, np.nan, 24.21, np.nan, 50.79, 75.00],
            ["POLO 5", "E.M. Mestra Fininha (E.F. - 1º e 2º ciclo)", 19, 1200, 8990, 7690, np.nan, 17880, 63.16, 473.16, 404.74, np.nan, 941.05],
            ["POLO 5", "E.M. Prof. André Trouche (E.F. - 1º e 2º ciclo)", 19, 2595, 3165, 5166, np.nan, 10926, 136.58, 166.58, 271.89, np.nan, 575.05],
            ["POLO 5", "E.M. João Brazil (E.F. - 1º e 2º ciclo)", 20, np.nan, 5544, 5544, np.nan, 11088, np.nan, 277.20, 277.20, np.nan, 554.40],
            ["POLO 5", "E.M. João Brazil (E.F. - 3º e 4º ciclo)", 20, 7452, np.nan, 7452, np.nan, 14904, 372.60, np.nan, 372.60, np.nan, 745.20],
            ["POLO 5", "E.M. João Brazil (E.J.A.)", 20, np.nan, np.nan, np.nan, 171, 171, np.nan, np.nan, np.nan, 8.55, 8.55],
            ["POLO 5", "E.M. Governador Roberto Silveira (E.F. - 1º e 2º ciclo)", 18, 2052, 2124, 4176, np.nan, 8352, 114.00, 118.00, 232.00, np.nan, 464.00],
            ["POLO 5", "E.M. Tiradentes (Pré-escolar)", 19, 389, 885, 1274, np.nan, 2548, 20.47, 46.58, 67.05, np.nan, 134.11],
            ["POLO 5", "E.M. Tiradentes (E.F. - 1º e 2º ciclo)", 19, 2626, 2726, 5355, np.nan, 10707, 138.21, 143.47, 281.84, np.nan, 563.53],
            ["POLO 5", "UMEI Rosalina de Araújo Costa (Creche)/(1~3 anos)", 19, 244, 260, 561, np.nan, 1065, 12.84, 13.68, 29.53, np.nan, 56.05],
            ["POLO 5", "UMEI Rosalina de Araújo Costa (Pré-escolar)", 19, 1170, 1316, 2456, np.nan, 4942, 61.58, 69.26, 129.26, np.nan, 260.11],
            ["POLO 6", "E.M. Prof. Lucia Maria da Silveira Rocha (E.F. - 1º e 2º ciclo)", 19, 3271, 2538, 5726, np.nan, 11535, 172.16, 133.58, 301.37, np.nan, 607.11],
            ["POLO 6", "E.M. Prof. Maria Ângela Moreira Pinto (E.F. - 1º e 2º ciclo)", 18, 2402, 2510, 5027, np.nan, 9939, 133.44, 139.44, 279.28, np.nan, 552.17],
            ["POLO 6", "E.M. Padre Leonel Franca (E.F. - 1º e 2º ciclo)", 19, 3369, 3410, 3294, 3377, 13450, 177.32, 179.47, 173.37, 177.74, 707.89],
            ["POLO 6", "E.M. Helena Antipoff (E.F. - 1º e 2º ciclo)", 18, 4771, 4771, 4513, np.nan, 14055, 265.06, 265.06, 250.72, np.nan, 780.83],
            ["POLO 6", "E.M. Julia Cortines (E.F. - 1º e 2º ciclo)", 20, 9812, 9046, 8745, 9046, 36649, 490.60, 452.30, 437.25, 452.30, 1832.45],
            ["POLO 6", "E.M. Prof. Paulo de Almeida Campos (E.F. - 1º e 2º ciclo)", 18, 2622, 2850, 6270, np.nan, 11742, 145.67, 158.33, 348.33, np.nan, 652.33],
            ["POLO 7", "E.M. Eulália da Silveira Bragança (Pré-escolar)", 18, 158, np.nan, 158, np.nan, 316, 8.78, np.nan, 8.78, np.nan, 17.56],
            ["POLO 7", "E.M. Eulália da Silveira Bragança (E.F. - 1º e 2º ciclo)", 18, 2168, 2345, 4403, np.nan, 8916, 120.44, 130.28, 244.61, np.nan, 495.33],
            ["POLO 7", "E.M. Francisco Portugal Neves (E.F. - 3º e 4º ciclo)", 21, 4967, 3444, 8027, np.nan, 16438, 236.52, 164.00, 382.24, np.nan, 782.76],
            ["POLO 7", "E.M. Francisco Portugal Neves (E.J.A.)", 21, np.nan, 1108, np.nan, 1108, 2216, np.nan, 52.76, np.nan, 52.76, 105.52],
            ["POLO 7", "E.M. Heloneida Studart (Creche)/(1~3 anos)", 19, 152, 152, 325, np.nan, 629, 8.00, 8.00, 17.11, np.nan, 33.11],
            ["POLO 7", "E.M. Heloneida Studart (Pré-escolar)", 19, 445, 551, 992, np.nan, 1988, 23.42, 29.00, 52.21, np.nan, 104.63],
            ["POLO 7", "E.M. Heloneida Studart (E.F. - 1º e 2º ciclo)", 19, 2954, 2699, 5382, np.nan, 11035, 155.47, 142.05, 283.26, np.nan, 580.79],
            ["POLO 7", "E.M. Maralegre (E.F. - 1º e 2º ciclo)", 20, 3564, 5069, 6117, np.nan, 14750, 178.20, 253.45, 305.85, np.nan, 737.50],
            ["POLO 7", "E.M. Prof. Dario de Souza Castello (E.F. - 1º e 2º ciclo)", 20, 3860, 3538, 8977, np.nan, 16375, 193.00, 176.90, 448.85, np.nan, 818.75],
            ["POLO 7", "E.M. Prof. Marcos Waldemar de F. Reis (E.F. - 1º e 2º ciclo)/(Ref.: Abril)", 17, 1962, 2061, 2965, np.nan, 6988, 115.41, 121.24, 174.41, np.nan, 411.06],
            ["POLO 7", "UMEI Vale Feliz (Pré-escolar)", 18, 424, 424, 424, 424, 1696, 23.56, 23.56, 23.56, 23.56, 94.22],
            ["POLO 7", "UMEI Vale Feliz (E.F. - 1º e 2º ciclo)", 18, 1295, 1922, 2534, 68, 5819, 71.94, 106.78, 140.78, 3.78, 323.28],
            ["POLO 7", "UMEI Vale Feliz (E.J.A.)", 18, np.nan, 172, np.nan, 172, 344, np.nan, 9.56, np.nan, 9.56, 19.11],
        ],
        columns=[
            "Polo", "Escola", "Dias letivos", "Desjejum", "Lanche", "Almoço", "Janta",
            "Total de refeições", "Média/dia - Desjejum", "Média/dia - Lanche",
            "Média/dia - Almoço", "Média/dia - Janta", "Média/dia - Total",
        ],
    )
    return df


DATASETS = {
    "Escolas Municipais (E.M.)": carregar_escolas_regulares,
    "UMEIs, Creches e C.C.": carregar_umei_creches,
    "Ensino Fundamental / E.J.A. por Polo": carregar_ensino_fundamental,
}


def carregar_todos() -> dict[str, pd.DataFrame]:
    """Retorna os 3 conjuntos de dados já limpos, prontos para uso na dashboard."""
    return {nome: loader() for nome, loader in DATASETS.items()}
