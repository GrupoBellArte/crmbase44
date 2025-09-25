from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Lista de ferramentas que o ChatGPT vai enxergar
TOOLS = [
    {
        "name": "consultarClientes",
        "description": "Busca clientes no CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
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
    }
]

@app.route("/")
def home():
    return "✅ MCP server do CRM Base44 está no ar. Use /sse e /messages."

# Endpoint SSE para listar as ferramentas
@app.route("/sse", methods=["GET"])
def sse():
    def stream():
        yield "event: tool_list\n"
        yield f"data: { {'tools': TOOLS} }\n\n"
    return Response(stream(), mimetype="text/event-stream")

# Endpoint para processar chamadas do ChatGPT
@app.route("/messages", methods=["POST"])
def messages():
    data = request.json
    tool = data.get("tool")
    params = data.get("params", {})

    # Simulação de respostas — aqui depois você liga na API do Base44
    if tool == "consultarClientes":
        resposta = {"clientes": [{"id": "123", "nome": "João Silva"}]}
    elif tool == "atualizarCliente":
        resposta = {"status": "sucesso", "id": params.get("id"), "dados": params.get("dados")}
    else:
        resposta = {"erro": f"Ferramenta {tool} não reconhecida."}

    return jsonify(resposta)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
