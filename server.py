from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Ferramentas expostas ao ChatGPT
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
    return "✅ MCP server do CRM Base44 está rodando. Use /sse e /messages."

# SSE → ChatGPT descobre as ferramentas
@app.route("/sse", methods=["GET"])
def sse():
    def stream():
        yield "event: tool_list\n"
        yield f"data: { {'tools': TOOLS} }\n\n"
    return Response(stream(), mimetype="text/event-stream")

# Messages → ChatGPT chama aqui quando usa uma ferramenta
@app.route("/messages", methods=["POST"])
def messages():
    data = request.json or {}
    tool = data.get("tool")
    params = data.get("params", {})

    try:
        if tool == "consultarClientes":
            # Simulação
            resposta = {"clientes": [{"id": "123", "nome": "João Silva"}]}

        elif tool == "atualizarCliente":
            resposta = {
                "status": "sucesso",
                "id": params.get("id"),
                "dados": params.get("dados")
            }

        else:
            resposta = {"erro": f"Ferramenta {tool} não reconhecida."}

        return jsonify(resposta)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
