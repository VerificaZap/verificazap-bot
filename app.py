from flask import Flask, request, jsonify
import requests
import re
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "VerificaZap API Online"

@app.route('/consulta_receita', methods=['GET'])
def consulta_receita():
    cnpj_raw = request.args.get('mensagem', '')
    cnpj = re.sub(r'\D', '', cnpj_raw)

    if len(cnpj) != 14:
        return jsonify({"erro": "CNPJ inválido"}), 400

    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    try:
        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"erro": "Erro ao consultar ReceitaWS", "detalhe": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
