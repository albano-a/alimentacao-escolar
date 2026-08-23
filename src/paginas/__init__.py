"""Uma página por arquivo: cada opção do menu 'Página' na barra lateral mora aqui.

PAGINAS é a lista única de nomes/renderizadores — tanto a barra lateral quanto
o main.py leem daqui, então adicionar uma página é só criar o arquivo e somar
uma linha neste dicionário.
"""

from . import fnde, resumo_escola, visao_geral

PAGINAS = {
    "Visão geral": visao_geral.renderizar,
    "Resumo por escola": resumo_escola.renderizar,
    "Conformidade FNDE": fnde.renderizar,
}
