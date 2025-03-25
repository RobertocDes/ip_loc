from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_client_ip():
    # Obtém o cabeçalho X-Forwarded-For (usado por proxies como o Render)
    forwarded_ips = request.headers.get('X-Forwarded-For', '')
    if forwarded_ips:
        # Pega o primeiro IP da lista (IP original do cliente)
        client_ip = forwarded_ips.split(',')[0].strip()
    else:
        # Fallback para IP direto (se não houver proxy)
        client_ip = request.remote_addr
    
    return client_ip

@app.route('/my-location')
def get_location():
    client_ip = get_client_ip()
    
    # Verifica se o IP é público (não é privado ou localhost)
    if client_ip.startswith(('10.', '172.', '192.168.', '127.')):
        return jsonify({
            "error": "Não foi possível detectar um IP público válido.",
            "your_ip": client_ip
        }), 400
    
    try:
        response = requests.get(f"https://ipapi.co/{client_ip}/json/").json()
        return jsonify({
            "your_ip": client_ip,
            "location": {
                "city": response.get("city"),
                "country": response.get("country_name"),
                "latitude": response.get("latitude"),
                "longitude": response.get("longitude"),
                "region": response.get("region")
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)