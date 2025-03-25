from flask import Flask, request, jsonify
import requests
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Chave de API - Crie uma conta gratuita em https://ipapi.co/
IPAPI_KEY = "sua_chave_aqui"  # Opcional para mais requisições

def get_client_ip():
    """Obtém o IP real do cliente, mesmo atrás de proxies"""
    if 'X-Forwarded-For' in request.headers:
        ips = request.headers['X-Forwarded-For'].split(',')
        return ips[0].strip()
    return request.remote_addr

def get_coordinates(ip):
    """Obtém latitude e longitude do IP usando ipapi.co"""
    try:
        url = f"https://ipapi.co/{ip}/json/"
        if IPAPI_KEY:
            url += f"?key={IPAPI_KEY}"
            
        response = requests.get(url).json()
        return {
            "lat": float(response.get("latitude")),
            "lng": float(response.get("longitude")),
            "city": response.get("city", "Desconhecido")
        }
    except Exception as e:
        print(f"Erro ao geolocalizar IP {ip}: {str(e)}")
        return None

def find_nearby_motels(lat, lng, radius=10):
    """Busca motéis próximos usando OpenStreetMap Nominatim"""
    try:
        # URL da API Overpass (OpenStreetMap)
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["tourism"="motel"](around:{radius*1000},{lat},{lng});
          way["tourism"="motel"](around:{radius*1000},{lat},{lng});
          relation["tourism"="motel"](around:{radius*1000},{lat},{lng});
        );
        out center;
        """
        response = requests.get(overpass_url, params={'data': query}).json()
        
        motels = []
        for element in response.get("elements", []):
            if "tags" in element and "name" in element["tags"]:
                if "center" in element:
                    lat = element["center"]["lat"]
                    lon = element["center"]["lon"]
                else:
                    lat = element["lat"]
                    lon = element["lon"]
                
                motels.append({
                    "name": element["tags"]["name"],
                    "lat": lat,
                    "lng": lon,
                    "distance": calculate_distance(lat, lon, lat, lng)
                })
        
        # Ordena por distância
        return sorted(motels, key=lambda x: x["distance"])[:10]  # Limita a 10 resultados
        
    except Exception as e:
        print(f"Erro ao buscar motéis: {str(e)}")
        return []

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcula distância em km entre duas coordenadas (Haversine)"""
    R = 6371.0  # Raio da Terra em km
    
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

@app.route('/')
def show_map():
    try:
        # 1. Obtém IP do usuário
        user_ip = get_client_ip()
        
        # 2. Obtém coordenadas
        location = get_coordinates(user_ip)
        if not location:
            return "Erro ao geolocalizar seu IP", 400
        
        # 3. Busca motéis próximos (raio de 10km)
        motels = find_nearby_motels(location["lat"], location["lng"])
        
        # 4. Gera mapa
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Motéis próximos em {location['city']}</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <style>
                #map {{ height: 600px; width: 100%; }}
                .header {{ padding: 15px; background: #f0f0f0; }}
                h1 {{ margin: 0; color: #333; }}
                .info {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Motéis próximos em {location['city']}</h1>
                <div class="info">
                    <p>Seu IP: {user_ip}</p>
                    <p>Sua localização aproximada: Latitude {location['lat']:.6f}, Longitude {location['lng']:.6f}</p>
                </div>
            </div>
            <div id="map"></div>
            
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                // Configuração do mapa
                var map = L.map('map').setView([{location['lat']}, {location['lng']}], 13);
                
                // Camada do mapa
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }}).addTo(map);
                
                // Marcador da localização do usuário
                L.marker([{location['lat']}, {location['lng']}]).addTo(map)
                    .bindPopup('Sua Localização<br>Lat: {location['lat']:.6f}<br>Lng: {location['lng']:.6f}')
                    .openPopup();
                
                // Marcadores dos motéis
                {generate_motel_markers(motels)}
                
                // Círculo do raio de busca
                L.circle([{location['lat']}, {location['lng']}], {{
                    color: 'blue',
                    fillColor: '#30f',
                    fillOpacity: 0.1,
                    radius: 10000  // 10km em metros
                }}).addTo(map);
            </script>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>Erro</h1><p>{str(e)}</p>", 500

def generate_motel_markers(motels):
    """Gera JavaScript para os marcadores dos motéis"""
    if not motels:
        return "/* Nenhum motel encontrado */"
    
    js_code = ""
    for motel in motels:
        js_code += f"""
        L.marker([{motel['lat']}, {motel['lng']}], {{
            icon: L.icon({{
                iconUrl: 'https://cdn-icons-png.flaticon.com/512/2209/2209652.png',
                iconSize: [32, 32]
            }})
        }}).addTo(map)
            .bindPopup('<b>{motel['name']}</b><br>Distância: {motel['distance']:.1f} km');
        """
    return js_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)