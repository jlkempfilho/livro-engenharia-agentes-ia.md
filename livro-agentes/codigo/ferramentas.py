"""ferramentas.py - o que o modelo pode pedir para o nosso código fazer (capítulo 6)."""
import json

from banco import buscar_hibrida as buscar
from rag import FONTES_CONFIAVEIS

# Dados fictícios. Num sistema real, aqui entraria a consulta ao ERP.
PEDIDOS = {
    "000123": {"status": "bloqueado por crédito", "valor": 15400.00, "cliente": "Mercado Sol"},
    "000124": {"status": "faturado", "valor": 890.50, "cliente": "Padaria Lua"},
    "000125": {"status": "bloqueado por estoque", "valor": 3200.00, "cliente": "Empório Mar"},
}

FERRAMENTAS = [
    {"nome": "consultar_pedido",
     "descricao": "Consulta status, valor e cliente de um pedido de venda pelo número de "
                  "6 dígitos. Use sempre que o usuário citar um número de pedido.",
     "parametros": {"type": "object",
                    "properties": {"numero": {"type": "string",
                                              "description": "número do pedido, 6 dígitos"}},
                    "required": ["numero"], "additionalProperties": False}},
    {"nome": "buscar_manual",
     "descricao": "Busca procedimentos no manual de TI e do ERP. Use para dúvidas de "
                  "como fazer algo ou para descobrir como resolver um bloqueio ou erro.",
     "parametros": {"type": "object",
                    "properties": {"consulta": {"type": "string",
                                                "description": "o que procurar"}},
                    "required": ["consulta"], "additionalProperties": False}},
]


def executar(conn, nome, args):
    """Executa a ferramenta pedida. Devolve (texto_do_resultado, houve_erro)."""
    if nome == "consultar_pedido":
        numero = str(args.get("numero", ""))
        if not (numero.isdigit() and len(numero) == 6):      # validação é do código
            return json.dumps({"erro": "número de pedido inválido: use 6 dígitos"}), True
        pedido = PEDIDOS.get(numero)
        if pedido is None:
            return json.dumps({"erro": "pedido não encontrado"}), True
        resultado = dict(pedido)
        if "bloqueado" in pedido["status"]:
            # Passo previsível não fica à mercê do modelo: o código já anexa o procedimento.
            achados = buscar(conn, f"pedido {pedido['status']}", k=1, fontes=FONTES_CONFIAVEIS)
            resultado["procedimento_do_manual"] = achados[0][0]
        return json.dumps(resultado, ensure_ascii=False), False
    if nome == "buscar_manual":
        trechos = buscar(conn, str(args.get("consulta", "")), k=3, fontes=FONTES_CONFIAVEIS)
        return json.dumps([c for c, _, _ in trechos], ensure_ascii=False), False
    return json.dumps({"erro": f"ferramenta desconhecida: {nome}"}), True
