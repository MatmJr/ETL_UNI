from datetime import date
from fastmcp import FastMCP
from src.extract import Extract

mcp = FastMCP("meios-pagamento")
extract = Extract()


def _trimestre_para_data(trimestre: str) -> str:
    ano = int(trimestre[:4])
    q = int(trimestre[4])
    mes = [1, 4, 7, 10][q - 1]
    return date(ano, mes, 1).strftime("%Y-%m-%d")


def _n_retornos(trimestre: str) -> int:
    ano = int(trimestre[:4])
    q = int(trimestre[4])
    hoje = date.today()
    # +4 de margem para cobrir trimestres sem dados publicados ainda
    n = (hoje.year - ano) * 4 + ((hoje.month - 1) // 3 + 1 - q) + 4
    return max(n, 1)


@mcp.tool()
def buscar_meios_pagamento(trimestre: str) -> list:
    """
    Busca dados de meios de pagamento do Banco Central do Brasil.

    A API retorna registros do mais recente até o trimestre indicado. Esta função
    filtra automaticamente o registro correspondente ao trimestre solicitado.
    Se o filtro exato não encontrar resultado, retorna todos os registros disponíveis
    para que o modelo identifique o correto pelo campo 'datatrimestre'.

    Args:
        trimestre: Trimestre no formato YYYYQ (ex: '20251' para Q1 2025, '20244' para Q4 2024).

    Returns:
        Lista com o(s) registro(s) do trimestre solicitado, ou todos se não filtrar.
    """
    n = _n_retornos(trimestre)
    resultado = extract.extract_meios_pagamentos(trimestre=trimestre, n_retornos=str(n))
    todos = resultado.get("value", [])

    data_alvo = _trimestre_para_data(trimestre)
    filtrados = [r for r in todos if r.get("datatrimestre", "").startswith(data_alvo[:7])]

    return filtrados if filtrados else todos


if __name__ == "__main__":
    mcp.run()
