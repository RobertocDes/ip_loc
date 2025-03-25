from flask import Flask, request
import requests

app = Flask(__name__)

GOOGLE_API_KEY = "SUA_CHAVE_AQUI"

def get_client_ip():
    forwarded_ips = request.headers.get('X-Forwarded-For', '')
    if forwarded_ips:
        client_ip = forwarded_ips.split(',')[0].strip()
    else:
        client_ip = request.remote_addr
    return client_ip

def get_nearby_motels(lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 50000,  # 50km conforme você ajustou
        "type": "motel",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params).json()
    
    if response.get("status") == "OK" and len(response.get("results", [])) >= 2:
        motels = response["results"]
        return motels[1]  # Segundo motel
    return None

@app.route('/')
@app.route('/mapa')
def mostrar_mapa():
    client_ip = get_client_ip()
    
    # Inicializa com padrão
    lat = -22.970722
    lng = -43.182365
    location_info = "Localização padrão (Copacabana)"
    motel_info = "Nenhum motel encontrado"

    # Tenta obter a localização do usuário
    try:
        # Verifica se o IP parece privado
        if not client_ip.startswith(('10.', '172.', '192.168.', '127.')):
            response = requests.get(f"https://ipapi.co/{client_ip}/json/").json()
            if "latitude" in response and "longitude" in response and response.get("latitude") is not None:
                lat = float(response["latitude"])
                lng = float(response["longitude"])
                location_info = f"Sua localização: {response.get('city', 'Cidade desconhecida')}, {response.get('country_name', 'País desconhecido')}"
            else:
                location_info = "Erro: Dados de localização inválidos retornados pela API"
            
            # Busca motel próximo
            motel = get_nearby_motels(lat, lng)
            if motel:
                motel_lat = motel["geometry"]["location"]["lat"]
                motel_lng = motel["geometry"]["location"]["lng"]
                motel_name = motel["name"]
                motel_info = f"Segundo motel mais próximo: {motel_name}"
                lat = motel_lat
                lng = motel_lng
            else:
                motel_info = "Não foi possível encontrar o segundo motel mais próximo (50km)"
        else:
            location_info = "IP privado detectado, usando padrão"
    except Exception as e:
        location_info = f"Erro ao obter localização: {str(e)}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Segundo Motel Mais Próximo</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            #map {{ height: 500px; width: 100%; border: 2px solid #0078d4; border-radius: 10px; }}
            .info {{ margin: 10px 0; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>🌍 Segundo Motel Mais Próximo</h1>
        <p class="info">IP detectado: {client_ip}</p>
        <p class="info">{location_info}</p>
        <p class="info">{motel_info}</p>
        <p class="info">Coordenadas exibidas: Lat {lat}, Long {lng}</p>
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
                    .bindPopup("{motel_info}")
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