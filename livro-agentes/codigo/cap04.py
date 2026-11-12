"""Capítulo 4 - o manual vai para o banco vetorial."""
from banco import buscar, carregar_manual, conectar

conn = conectar()
print("trechos no arquivo do manual:", carregar_manual(conn))
print("linhas na tabela:", conn.execute("SELECT count(*) FROM trechos").fetchone()[0], "\n")

for pergunta in ["como libero um pedido travado?",
                 "esqueci minha senha do sistema",
                 "a nota não transmite"]:
    print(f"> {pergunta}")
    for conteudo, fonte, semelhanca in buscar(conn, pergunta, k=2):
        print(f"  {semelhanca:.3f} [{fonte}] {conteudo[:80]}")
    print()
