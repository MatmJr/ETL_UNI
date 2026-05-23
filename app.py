import json
import os
import asyncio
import streamlit as st
from openai import OpenAI
from fastmcp import Client
from mcp_server import mcp
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_async(coro):
    """Executa corrotina em thread separada para não conflitar com o event loop do Streamlit."""
    with __import__("concurrent.futures", fromlist=["ThreadPoolExecutor"]).ThreadPoolExecutor() as pool:
        return pool.submit(asyncio.run, coro).result()


async def _list_tools():
    async with Client(mcp) as client:
        return await client.list_tools()


async def _call_tool(name: str, args: dict):
    async with Client(mcp) as client:
        return await client.call_tool(name, args)


def to_openai_tool(t) -> dict:
    return {
        "type": "function",
        "function": {
            "name": t.name,
            "description": t.description or "",
            "parameters": t.inputSchema,
        },
    }


SYSTEM_PROMPT = """Você é um analista de meios de pagamento do Banco Central do Brasil.

## Uso da tool
- Formato do trimestre: YYYYQ  (ex: '20251' = Q1 2025, '20244' = Q4 2024)
- Use 'datatrimestre' para confirmar o período do registro retornado.

## Dados retornados
Os valores já estão em unidades absolutas:
- Campos "valor*"      → R$ (reais)        ex: valorPix = 9_300_000_000 = R$ 9,3 bilhões
- Campos "quantidade*" → transações         ex: quantidadePix = 20_500_000_000 = 20,5 bilhões de transações

## Formatação das respostas
Apresente sempre em linguagem natural com escala legível:
- Acima de 1 trilhão  → "R$ X,X trilhões"
- Entre 1 bi e 1 tri  → "R$ X,X bilhões"
- Abaixo de 1 bilhão  → "R$ X,X milhões"
- Use a mesma escala para quantidades (bilhões, milhões, milhares de transações).

## Meios de pagamento disponíveis
Pix, TED, TEC, DOC, Cheque, Boleto, Cartão de Crédito, Cartão de Débito,
Cartão Pré-pago, Transferência Intrabancária, Convênios, Débito Direto, Saques.
"""


def chat(pergunta: str) -> str:
    mcp_tools = run_async(_list_tools())
    openai_tools = [to_openai_tool(t) for t in mcp_tools]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": pergunta},
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=openai_tools,
    )

    msg = response.choices[0].message
    messages.append(msg)

    if msg.tool_calls:
        for tc in msg.tool_calls:
            resultado = run_async(_call_tool(tc.function.name, json.loads(tc.function.arguments)))
            content = resultado.content[0].text if resultado and resultado.content else "sem resultado"
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": content,
            })

        final = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return final.choices[0].message.content

    return msg.content


st.title("Meios de Pagamento — Banco Central")

pergunta = st.text_input("Pergunta", placeholder="Ex: Qual o valor do Pix no 1º trimestre de 2025?")

if st.button("Enviar") and pergunta:
    with st.spinner("Consultando..."):
        resposta = chat(pergunta)
    st.write(resposta)
