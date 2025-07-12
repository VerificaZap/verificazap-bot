from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Simula uma resposta para consulta de CNPJ
def consultar_cnpj(cnpj):
    resumo = (
        f"✅ Empresa Verificada\n"
        f"📄 POSTO FICTÍCIO LTDA (POSTO FICTÍCIO)\n"
        f"🗖 Abertura: 10/02/2010\n"
        f"🗞 CNPJ: {cnpj}\n"
        f"📌 Situação: ATIVA\n"
        f"💼 Atividade: Comércio varejista de combustíveis\n"
        f"📍 Local: São Paulo/SP\n"
        f"💰 Capital: R$ 500.000,00\n"
    )
    return resumo, None

zapi_instance = '3E4098EAF8EF11B5B5083E61E96978DB'
zapi_token = '47A7C1C9E5CB334EBC020A8D'

# Envia mensagem para o número informado via Z-API
def enviar_resposta(numero, texto):
    url = f'https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}/send-text'
    headers = {
        "Client-Token": zapi_token,
        "Content-Type": "application/json"
    }
    payload = {"phone": numero, "message": texto}
    print(f"[ENVIANDO PARA Z-API] {numero}: {texto}")
    resposta = requests.post(url, json=payload, headers=headers)
    print(f"[Z-API RESPONSE] {resposta.status_code} - {resposta.text}")

@app.route('/webhook', methods=['POST'])
def receber_mensagem():
    try:
        print(f"[WEBHOOK] Headers: {dict(request.headers)}")
        print(f"[WEBHOOK] Body raw: {request.data}")
        data = request.get_json(force=True, silent=True) or {}
        print(f"[WEBHOOK] JSON interpretado: {data}")

        texto = ''
        if 'text' in data and isinstance(data['text'], dict):
            texto = data['text'].get('message', '')
        numero = data.get('phone', '')

        print(f"[WEBHOOK] Extrato: texto='{texto}' numero='{numero}'")

        if not texto or not numero:
            print("[WEBHOOK] Falha: texto ou número ausente.")
            return '', 400

        if len(texto) != 14 or not texto.isdigit():
            enviar_resposta(numero, "❌ Envie apenas um CNPJ com 14 números, sem pontos ou traços.")
            return '', 200

        resumo, erro = consultar_cnpj(texto)

        if erro:
            enviar_resposta(numero, f"❌ Erro na consulta: {erro}")
        else:
            enviar_resposta(numero, resumo)

        return '', 200

    except Exception as e:
        print(f"[WEBHOOK] Erro inesperado: {str(e)}")
        return '', 500

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

@app.route('/', methods=['GET'])
def homepage():
    return 'VerificaZap rodando!'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
