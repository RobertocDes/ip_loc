from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/mapa_moteis', methods=['GET'])
def mapa_moteis():
    # Obtém as coordenadas do usuário (ou padrão: São Paulo)
    lat = request.args.get('lat', '-23.5505')
    lng = request.args.get('lng', '-46.6333')
    
    # Consulta motéis no OpenStreetMap (raio de 3km)
    overpass_query = f"""
    [out:json];
    node[amenity=hotel][name~"motel|Motel"](around:3000,{lat},{lng});
    out center;
    """
    
    try:
        # Faz a requisição para a API Overpass
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={'data': overpass_query},
            timeout=5
        )
        motels = response.json().get('elements', [])
        
        # Gera o HTML com mapa interativo
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Motéis Próximos</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <style>
                #map {{ 
                    height: 400px; 
                    width: 100%;
                    border-radius: 10px;
                    margin-bottom: 15px;
                }}
                .motel-info {{ 
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="motel-info">
                <h3>Motéis próximos:</h3>
                <ul>
                    {"".join(
                        f'<li><strong>{motel["tags"].get("name", "Motel")}</strong><br>'
                        f'{motel["tags"].get("addr:street", "Endereço não disponível")}</li>'
                        for motel in motels[:5]  # Limita a 5 resultados
                    )}
                </ul>
            </div>
            
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                // Mapa centralizado na localização do usuário
                var map = L.map('map').setView([{lat}, {lng}], 14);
                
                // Camada do OpenStreetMap
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }}).addTo(map);
                
                // Marcador do usuário
                L.marker([{lat}, {lng}]).addTo(map)
                    .bindPopup("Sua localização");
                
                // Marcadores dos motéis
                {"" if not motels else "".join(
                    f'L.marker([{motel.get("lat", motel["center"]["lat"])},'
                    f'{motel.get("lon", motel["center"]["lon"])}]).addTo(map)'
                    f'.bindPopup("{motel["tags"].get("name", "Motel")}");'
                    for motel in motels[:5]  # Limita a 5 marcadores
                )}
            </script>
        </body>
        </html>
        """
    
    except Exception as e:
        return f"""
        <html>
        <body>
            <h3>Erro ao carregar o mapa</h3>
            <p>Por favor, tente novamente mais tarde.</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)