from flask import Flask, request, Response, jsonify
import json

app = Flask(__name__)

# Definição das ferramentas disponíveis
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

# Endpoint para ChatGPT listar ferramentas
@app.route("/sse")
def sse():
    def event_stream():
        yield f"event: tool_list\n"
        yield f"data: {json.dumps({'tools': TOOLS})}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

# Endpoint para ChatGPT mandar ações
@app.route("/messages", methods=["POST"])
def messages():
    try:
        data = request.json
        print("Mensagem recebida:", json.dumps(data, indent=2))

        # Simulação de execução da ferramenta
        tool_name = data.get("tool", "desconhecido")
        arguments = data.get("arguments", {})

        resposta = {
            "content": [
                {
                    "type": "text",
                    "text": f"A ferramenta {tool_name} foi chamada com argumentos {arguments}"
                }
            ]
        }
        return jsonify(resposta)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Página inicial
@app.route("/")
def home():
    return "MCP server do CRM Base44 está no ar. Use /sse e /messages."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
