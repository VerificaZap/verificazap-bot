from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# DADOS FIXOS PARA TESTE (simulação)
def consultar_cnpj(cnpj):
    resumo = (
        f"✅ Empresa Verificada\n"
        f"📄 POSTO FICTÍCIO LTDA (POSTO FICTÍCIO)\n"
        f"📆 Abertura: 10/02/2010\n"
        f"🧾 CNPJ: {cnpj}\n"
        f"📌 Situação: ATIVA\n"
        f"💼 Atividade: Comércio varejista de combustíveis\n"
        f"📍 Local: São Paulo/SP\n"
        f"💰 Capital: R$ 500.000,00\n"
    )
    return resumo, None

# DADOS FIXOS DA Z-API
zapi_instance = '3E4098EAF8EF11B5B5083E61E96978DB'
zapi_token = '47A7C1C9E5CB334EBC020A8D'

def enviar_resposta(numero, texto):
    url = f'https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}/send-text'
    payload = {
        "phone": numero,
        "message": texto
    }
    print(f"Enviando para {numero}: {texto}")
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def receber_mensagem():
    try:
        # Tenta pegar o JSON mesmo se o cabeçalho estiver errado
        data = request.get_json(force=True, silent=True) or {}
        print(f"[WEBHOOK] Dados recebidos brutos: {request.data}")
        print(f"[WEBHOOK] JSON interpretado: {data}")

        mensagem = data.get('message')
        numero = data.get('phone')

        if not mensagem or not numero:
            print("[WEBHOOK] Falha: 'message' ou 'phone' ausente.")
            return '', 400

        if len(mensagem) != 14 or not mensagem.isdigit():
            enviar_resposta(numero, "❌ Envie apenas um CNPJ com 14 números, sem pontos ou traços.")
            return '', 200

        resumo, erro = consultar_cnpj(mensagem)
        if erro:
            enviar_resposta(numero, f"❌ Erro na consulta: {erro}")
        else:
            enviar_resposta(numero, resumo)

        return '', 200

    except Exception as e:
        print(f"[WEBHOOK] Erro no processamento: {str(e)}")
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
