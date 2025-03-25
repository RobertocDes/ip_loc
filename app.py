from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/my-location', methods=['GET'])
def get_my_location():
    # Pega o IP do cliente que fez a requisição
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Se estiver rodando localmente (127.0.0.1), use um IP de teste ou retorne erro
    if user_ip == '127.0.0.1':
        return jsonify({"error": "Não foi possível detectar seu IP real (você está em localhost)."}), 400
    
    try:
        # Consulta o ipapi.co
        response = requests.get(f"https://ipapi.co/{user_ip}/json/").json()
        
        return jsonify({
            "your_ip": user_ip,
            "location": {
                "city": response.get("city"),
                "region": response.get("region"),
                "country": response.get("country_name"),
                "latitude": response.get("latitude"),
                "longitude": response.get("longitude")
            }
        })
    except Exception as e:
        return jsonify({"error": f"Falha ao consultar geolocalização: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)