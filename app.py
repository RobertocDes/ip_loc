from flask import Flask, request
import requests
import os

app = Flask(__name__)

@app.route('/mapa_moteis', methods=['GET'])
def mapa_moteis():
    # Obtém as coordenadas (padrão: São Paulo)
    lat = request.args.get('lat', '-23.5505')
    lng = request.args.get('lng', '-46.6333')
    
    # Consulta motéis no OpenStreetMap (raio de 3km)
    overpass_query = f"""
    [out:json];
    node[amenity=hotel][name~"motel|Motel"](around:3000,{lat},{lng});
    out center;
    """
    
    try:
        response = requests.get(
            "https://overpass-api.de/api/interpreter",
            params={'data': overpass_query},
            timeout=5
        )
        motels = response.json().get('elements', [])

        # HTML do mapa (agora sem comentários nas f-strings!)
        html = f"""
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
                        for motel in motels[:5]
                    )}
                </ul>
            </div>
            
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                var map = L.map('map').setView([{lat}, {lng}], 14);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; OpenStreetMap'
                }}).addTo(map);
                
                L.marker([{lat}, {lng}]).addTo(map).bindPopup("Sua localização");
                
                {"".join(
                    f'L.marker([{motel.get("lat", motel["center"]["lat"])},'
                    f'{motel.get("lon", motel["center"]["lon"])}]).addTo(map)'
                    f'.bindPopup("{motel["tags"].get("name", "Motel").replace("\"", "\\"")}");'
                    for motel in motels[:5]
                )}
            </script>
        </body>
        </html>
        """
        return html
    
    except Exception as e:
        return """
        <html>
        <body>
            <h3>Erro ao carregar o mapa</h3>
            <p>Tente novamente mais tarde.</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)