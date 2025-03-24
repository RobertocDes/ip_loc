from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/get_location', methods=['GET'])
def get_location():
    try:
        # 1. Prioriza o IP do usuário do TypeBot (não do servidor Render)
        user_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        
        # 2. Se não houver IP (TypeBot em embed), usa o IP remoto
        if not user_ip:
            user_ip = request.remote_addr
            
        # 3. Evita retornar IPs locais/privados (ex.: do Render)
        if user_ip in ('127.0.0.1', '::1') or user_ip.startswith(('10.', '172.', '192.')):
            return jsonify({"error": "Localização indisponível"}), 400

        # 4. Consulta a API de geolocalização
        api_key = os.getenv("IPGEOLOCATION_API_KEY")
        if not api_key:
            return jsonify({"error": "Configuração inválida"}), 500

        api_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={user_ip}&fields=city,latitude,longitude"
        response = requests.get(api_url, timeout=3)
        response.raise_for_status()
        
        return jsonify(response.json())

    except requests.exceptions.RequestException:
        return jsonify({"error": "Serviço de geolocalização indisponível"}), 502
    except Exception:
        return jsonify({"error": "Erro interno"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)