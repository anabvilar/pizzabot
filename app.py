from flask import Flask, request, jsonify, render_template, session
from openai import AzureOpenAI
import mysql.connector
import os
import json
from dotenv import load_dotenv

# Carrega as chaves secretas salvas no arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = "pizzabot2026"

# Inicializa o cliente conectado ao Azure AI Foundry
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-02-15-preview", 
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

SYSTEM_PROMPT = """
Você é um atendente virtual de uma pizzaria chamada Pizza Bot.
Seu objetivo é coletar as informações do pedido de forma amigável e natural.

Você deve coletar obrigatoriamente:
- Nome do cliente
- Telefone
- Endereço de entrega
- Tamanho da pizza: pequena, média ou grande
- Sabor da pizza (ofereça opções: Margherita, Calabresa, Frango com Catupiry, Portuguesa, Quatro Queijos)
- Tipo de borda: tradicional, recheada com catupiry ou sem borda
- Observações (opcional)

Quando tiver TODOS os dados obrigatórios coletados, responda estruturadamente com um JSON no seguinte formato e nada mais além dele:

{
  "pedido_completo": true,
  "nome_cliente": "...",
  "telefone": "...",
  "endereco": "...",
  "tamanho": "...",
  "sabor": "...",
  "borda": "...",
  "observacoes": "..."
}

Enquanto ainda estiver no processo de coleta, responda normalmente em formato de texto, de forma simpática e objetiva. Não peça todas as informações de uma única vez.
"""

def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def salvar_pedido(dados):
    conn = conectar_banco()
    cursor = conn.cursor()
    sql = """
        INSERT INTO pedidos (nome_cliente, telefone, endereco, tamanho, sabor, borda, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    valores = (
        dados["nome_cliente"], dados["telefone"], dados["endereco"],
        dados["tamanho"], dados["sabor"], dados["borda"], dados.get("observacoes", "")
    )
    cursor.execute(sql, valores)
    conn.commit()
    pedido_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return pedido_id

@app.route("/")
def index():
    session["historico"] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    dados = request.get_json()
    mensagem_usuario = dados.get("mensagem", "")
    historico = session.get("historico", [])

    historico.append({"role": "user", "content": mensagem_usuario})

    resposta = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"), 
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + historico,
        temperature=0.7
    )
    conteudo = resposta.choices[0].message.content

    try:
        dados_pedido = json.loads(conteudo)
        if dados_pedido.get("pedido_completo"):
            pedido_id = salvar_pedido(dados_pedido)
            session["historico"] = []
            return jsonify({
                "resposta": f"Pedido registrado com sucesso! Seu número de pedido é #{pedido_id}. Sua pizza logo sairá do forno! 🍕",
                "pedido_finalizado": True
            })
    except (json.JSONDecodeError, KeyError):
        pass

    historico.append({"role": "assistant", "content": conteudo})
    session["historico"] = historico
    session.modified = True
    return jsonify({"resposta": conteudo, "pedido_finalizado": False})

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin/pedidos")
def listar_pedidos():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pedidos ORDER BY criado_em DESC")
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # TRECHO CORRIGIDO ABAIXO (Indentações alinhadas com 4 espaços por nível)
    for p in pedidos:
        if p.get("criado_em"):
            p["criado_em"] = p["criado_em"].strftime("%d/%m/%Y %H:%M")
            
    return jsonify(pedidos)

@app.route("/admin/pedidos/<int:pedido_id>/status", methods=["POST"])
def atualizar_status(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status")
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, pedido_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"mensagem": "Status atualizado com sucesso!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)