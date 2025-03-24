from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuração segura para produção (não usa .env no Render)
@app.route('/get_location', methods=['GET'])
def get_location():
    try:
        # Pega o IP do usuário (considerando proxies)
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in user_ip:  # Caso tenha múltiplos IPs (ex.: Cloudflare)
            user_ip = user_ip.split(',')[0].strip()

        # Chave da API lida das variáveis de ambiente do Render
        api_key = os.getenv("IPGEOLOCATION_API_KEY")
        if not api_key:
            return jsonify({"error": "Chave da API não configurada"}), 500

        # Chamada para a API de geolocalização (apenas campos necessários)
        api_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={user_ip}&fields=city,latitude,longitude"
        response = requests.get(api_url, timeout=5)  # Timeout de 5 segundos
        response.raise_for_status()  # Verifica erros HTTP

        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erro na API de geolocalização: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    # Configuração para produção (Render usa a porta definida em $PORT)
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)