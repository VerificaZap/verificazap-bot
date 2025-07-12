
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

receitaws_token = 'SEU_TOKEN_RECEITAWS'
zapi_instance = '3E4098EAF8EF11B5B5083E61E96978DB'
zapi_token = '47A7C1C9E5CB334EBC020A8D'

def consultar_cnpj(cnpj):
    url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}?token={receitaws_token}'
    resposta = requests.get(url).json()
    if resposta.get('status') == 'ERROR':
        return None, resposta.get('message')

    resumo = (
        f"✅ Empresa Verificada\n"
        f"📄 {resposta.get('nome')} ({resposta.get('fantasia')})\n"
        f"📆 Abertura: {resposta.get('abertura')}\n"
        f"🧾 CNPJ: {resposta.get('cnpj')}\n"
        f"📌 Situação: {resposta.get('situacao')}\n"
        f"💼 Atividade: {resposta.get('atividade_principal', [{}])[0].get('text')}\n"
        f"📍 Local: {resposta.get('municipio')}/{resposta.get('uf')}\n"
        f"💰 Capital: R$ {resposta.get('capital_social')}\n"
    )
    return resumo, None

def enviar_resposta(numero, texto):
    url = f'https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}/send-text'
    payload = {
        "phone": numero,
        "message": texto
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def receber_mensagem():
    data = request.json
    mensagem = data.get('message')
    numero = data.get('phone')

    if not mensagem or len(mensagem) != 14 or not mensagem.isdigit():
        enviar_resposta(numero, "❌ Envie apenas um CNPJ com 14 números, sem pontos ou traços.")
        return '', 200

    resumo, erro = consultar_cnpj(mensagem)
    if erro:
        enviar_resposta(numero, f"❌ Erro na consulta: {erro}")
    else:
        enviar_resposta(numero, resumo)

    return '', 200

@app.route('/consulta', methods=['POST'])
def consulta_cnpj():
    dados = request.get_json()
    cnpj = dados.get('cnpj')

    if not cnpj:
        return jsonify({'erro': 'CNPJ não fornecido'}), 400

    resumo, erro = consultar_cnpj(cnpj)
    if erro:
        return jsonify({'erro': erro}), 400
    return jsonify({'resumo': resumo})

if __name__ == '__main__':
    import os  
port = int(os.environ.get("PORT", 5000))  
app.run(debug=True, host="0.0.0.0", port=port)
