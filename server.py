from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

# Lista de ferramentas MCP
tools = [
    {
        "name": "consultarClientes",
        "description": "Busca clientes no CRM",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}}
    },
    {
        "name": "atualizarCliente",
        "description": "Atualiza um cliente no CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "dados": {"type": "object"}
            }
        }
    },
    {
        "name": "consultarInteracoes",
        "description": "Lista interações de um cliente",
        "inputSchema": {"type": "object", "properties": {"client_id": {"type": "string"}}}
    },
    {
        "name": "consultarTarefas",
        "description": "Lista tarefas do CRM",
        "inputSchema": {"type": "object", "properties": {"client_id": {"type": "string"}}}
    },
    {
        "name": "consultarVisitas",
        "description": "Lista visitas agendadas",
        "inputSchema": {"type": "object", "properties": {"client_id": {"type": "string"}}}
    },
    {
        "name": "consultarContatosLoja",
        "description": "Lista contatos de uma loja",
        "inputSchema": {"type": "object", "properties": {"client_id": {"type": "string"}}}
    }
]

# Endpoint MCP: lista as ferramentas
@app.route("/sse", methods=["GET"])
def sse():
    payload = {"type": "tool_list", "tools": tools}
    return jsonify(payload)

# Endpoint MCP: processa chamadas do ChatGPT
@app.route("/messages", methods=["POST"])
def messages():
    data = request.get_json()
    print("Mensagem recebida do ChatGPT:", data)

    # Exemplo de resposta genérica
    response = {
        "type": "message",
        "content": [
            {"type": "text", "text": "Recebi sua solicitação e em breve irei responder."}
        ]
    }
    return jsonify(response)

@app.route("/")
def home():
    return "🚀 MCP server do CRM Base44 está no ar! Use /sse e /messages."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
