from flask import Flask, request
import requests
import os

app = Flask(__name__)

def escape_quotes(text):
    """Remove aspas problemáticas para JavaScript"""
    return text.replace('"', '').replace("'", "")

@app.route('/mapa_moteis', methods=['GET'])
def mapa_moteis():
    try:
        # Coordenadas padrão (São Paulo)
        lat = request.args.get('lat', '-23.5505')
        lng = request.args.get('lng', '-46.6333')
        
        # Consulta simplificada ao OpenStreetMap
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node[amenity=hotel][name~"motel"](around:3000,{lat},{lng});
        out;
        """
        
        response = requests.get(overpass_url, params={'data': query}, timeout=5)
        motels = response.json().get('elements', [])[:3]  # Limita a 3 resultados

        # Gera marcadores de forma segura
        markers_js = ""
        for motel in motels:
            name = escape_quotes(motel.get('tags', {}).get('name', 'Motel'))
            mlat = motel.get('lat', 0)
            mlon = motel.get('lon', 0)
            markers_js += f"""
            L.marker([{mlat}, {mlon}]).addTo(map)
                .bindPopup("{name}");
            """

        # HTML completo com fallbacks seguros
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Motéis Próximos</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <style>
                #map {{ height: 400px; width: 100%; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                var map = L.map('map').setView([{lat}, {lng}], 14);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                L.marker([{lat}, {lng}]).addTo(map).bindPopup("Você está aqui");
                {markers_js}
            </script>
        </body>
        </html>
        """

    except Exception:
        return """
        <html>
        <body>
            <h3>Serviço temporariamente indisponível</h3>
            <p>Tente novamente mais tarde.</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)