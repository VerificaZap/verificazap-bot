from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

@app.route('/consulta_receita', methods=['GET'])
def consulta_receita():
    cnpj_raw = request.args.get('mensagem', '')
    cnpj = re.sub(r'\D', '', cnpj_raw)  # Remove tudo que não for número

    if len(cnpj) != 14:
        return jsonify({"erro": "CNPJ inválido"}), 400

    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
    # Se tiver token: url += "?token=SEU_TOKEN"

    try:
        r = requests.get(url)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"erro": "Erro ao consultar ReceitaWS", "detalhe": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)


   
