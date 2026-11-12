"""Capítulo 6 - tool calling: uma volta feita à mão."""
from banco import carregar_manual, conectar
from ferramentas import FERRAMENTAS, executar
from llm import conversar

conn = conectar()
carregar_manual(conn)

for pergunta in ["Qual a situação do pedido 000123?", "E a do pedido 999999?"]:
    print(f"> {pergunta}")
    mensagens = [{"role": "user", "content": pergunta}]

    # 1. O modelo NÃO executa nada: ele pede.
    r = conversar(mensagens, ferramentas=FERRAMENTAS, etapa="cap06")
    print(f"  parada: {r.parada}")
    mensagens.append(r.mensagem())

    # 2. O nosso código decide, executa e devolve o resultado.
    for c in r.chamadas:
        saida, erro = executar(conn, c.nome, c.args)
        print(f"  o modelo pediu: {c.nome}({c.args}) -> {saida}  [erro: {erro}]")
        mensagens.append({"role": "tool", "id": c.id, "content": saida, "erro": erro})

    # 3. Com o resultado em mãos, o modelo redige a resposta.
    final = conversar(mensagens, ferramentas=FERRAMENTAS, etapa="cap06")
    if final.parada == "ferramenta":   # modelos que encadeiam pedem mais uma ferramenta
        print(f"  o modelo quer outra ferramenta: {[c.nome for c in final.chamadas]} "
              "(uma volta só não basta; o laço do capítulo 7 resolve)\n")
    else:
        print(f"  resposta: {final.texto}\n")
