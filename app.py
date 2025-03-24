from flask import Flask, request, jsonify
import requests
import os  # Adicione esta linha

app = Flask(__name__)

@app.route('/get_location', methods=['GET'])
def get_location():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    api_key = os.getenv("IPGEOLOCATION_API_KEY")  # Lê a chave do ambiente
    api_url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip={user_ip}"
    response = requests.get(api_url)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
