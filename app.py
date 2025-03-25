from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_client_ip():
    # Obtém o cabeçalho X-Forwarded-For (usado por proxies)
    forwarded_ips = request.headers.get('X-Forwarded-For', '')
    if forwarded_ips:
        client_ip = forwarded_ips.split(',')[0].strip()
    else:
        client_ip = request.remote_addr
    return client_ip

@app.route('/')  # Rota raiz
@app.route('/mapa')  # Rota alternativa
def mostrar_mapa():
    # Obtém o IP do cliente
    client_ip = get_client_ip()
    
    # Coordenadas padrão (Copacabana) caso a localização falhe
    lat = '-22.970722'
    lng = '-43.182365'
    location_info = "Localização padrão (Copacabana)"
    
    # Tenta obter a localização real
    try:
        if not client_ip.startswith(('10.', '172.', '192.168.', '127.')):
            response = requests.get(f"https://ipapi.co/{client_ip}/json/").json()
            if "latitude" in response and "longitude" in response:
                lat = response["latitude"]
                lng = response["longitude"]
                location_info = f"{response.get('city', 'Cidade desconhecida')}, {response.get('country_name', 'País desconhecido')}"
            else:
                location_info = "Erro: Dados de localização incompletos"
        else:
            location_info = "IP privado detectado, usando localização padrão"
    except Exception as e:
        location_info = f"Erro ao obter localização: {str(e)}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Seu Local no Mapa</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            #map {{ 
                height: 500px; 
                width: 100%;
                border: 2px solid #0078d4;
                border-radius: 10px;
            }}
            .info {{ margin: 10px 0; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>🌍 Seu Local no Mapa</h1>
        <p class="info">IP detectado: {client_ip}</p>
        <p class="info">Localização: {location_info}</p>
        <p class="info">Coordenadas: Lat {lat}, Long {lng}</p>
        <div id="map"></div>

        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
            try {{
                var map = L.map('map').setView([{lat}, {lng}], 15);
                
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxZoom: 19,
                    attribution: '© OpenStreetMap'
                }}).addTo(map);
                
                L.marker([{lat}, {lng}]).addTo(map)
                    .bindPopup("{location_info}")
                    .openPopup();
                    
                console.log("Mapa carregado com sucesso!");
            }} catch (e) {{
                console.error("Erro no mapa:", e);
                document.getElementById('map').innerHTML = 
                    '<p class="error">Erro ao carregar o mapa. Verifique o console.</p>';
            }}
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)