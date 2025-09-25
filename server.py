from flask import Flask, request, Response, jsonify
import json

app = Flask(__name__)

# Lista de ferramentas (MCP exige um "tool list")
TOOLS = [
    {
        "name": "consultarClientes",
        "description": "Busca clientes no CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "dados": {"type": "object"}
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

# Endpoint SSE para o ChatGPT listar ferramentas
@app.route("/sse")
def sse():
    def event_stream():
        yield f"event: tool_list\n"
        yield f"data: {json.dumps({'tools': TOOLS})}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

# Endpoint para o ChatGPT mandar ações (POST)
@app.route("/messages", methods=["POST"])
def messages():
    try:
        data = request.json
        print("Mensagem recebida:", data)

        # Exemplo de resposta genérica
        resposta = {
            "content": [
                {
                    "type": "text",
                    "text": f"Recebi a ação: {data}"
                }
            ]
        }
        return jsonify(resposta)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "MCP server do CRM Base44 está no ar. Use /sse e /messages."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
