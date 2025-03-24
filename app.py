from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

def is_valid_ip(ip):
    """Verifica se o IP é público (não local/privado)"""
    if not ip:
        return False
    # Lista de IPs privados/localhost
    private_prefixes = ('127.', '10.', '172.16.', '192.168.', '::1')
    return not ip.startswith(private_prefixes)

@app.route('/get_location', methods=['GET'])
def get_location():
    try:
        # 1. Pega o IP do parâmetro da URL (se fornecido)
        user_ip = request.args.get('ip', '').strip()
        
        # 2. Se não houver IP na URL, pega do cabeçalho HTTP (X-Forwarded-For)
        if not user_ip:
            forwarded_ips = request.headers.get('X-Forwarded-For', '').split(',')
            user_ip = next((ip.strip() for ip in forwarded_ips if is_valid_ip(ip)), None)
        
        # 3. Se ainda não houver IP válido, usa o IP remoto (com verificação)
        if not user_ip:
            user_ip = request.remote_addr if is_valid_ip(request.remote_addr) else None
        
        # 4. Se nenhum IP válido for encontrado, retorna erro
        if not user_ip:
            return jsonify({"error": "Não foi possível determinar seu IP público"}), 400

        # 5. Consulta a API de geolocalização
        api_key = os.getenv("IPGEOLOCATION_API_KEY")
        if not api_key:
            return jsonify({"error": "Configuração de API inválida"}), 500

        api_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={user_ip}&fields=city,latitude,longitude"
        response = requests.get(api_url, timeout=3)
        response.raise_for_status()
        
        return jsonify(response.json())

    except requests.exceptions.RequestException:
        return jsonify({"error": "Serviço de geolocalização temporariamente indisponível"}), 502
    except Exception:
        return jsonify({"error": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)