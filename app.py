from flask import Flask, request
import requests
import os
import logging

app = Flask(__name__)

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_nearby_motels(lat, lng):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 50000,
        "keyword": "motel",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params).json()
    
    if response.get("status") == "OK" and len(response.get("results", [])) >= 1:
        motels = response["results"]
        return motels[0]
    return None

@app.route('/')
@app.route('/mapa')
def mostrar_mapa():
    logger.info("Requisição recebida em /mapa")
    
    lat = -22.970722  # Padrão (Copacabana)
    lng = -43.182365
    location_info = "Localização padrão (Copacabana)"
    motel_name = "Nenhum"

    try:
        # Usa https://ipapi.co/json para pegar localização diretamente
        response = requests.get("https://ipapi.co/json/", timeout=5).json()
        logger.info(f"Resposta da ipapi.co: {response}")
        if "latitude" in response and "longitude" in response and response.get("latitude") is not None:
            lat = float(response["latitude"])
            lng = float(response["longitude"])
            location_info = f"Sua localização: {response.get('city', 'Cidade desconhecida')}, {response.get('country_name', 'País desconhecido')}"
        else:
            location_info = "Erro: Dados de localização inválidos da API ipapi.co"
            logger.warning("Dados de latitude/longitude não encontrados na resposta da ipapi.co")
        
        motel = get_nearby_motels(lat, lng)
        if motel:
            motel_lat = motel["geometry"]["location"]["lat"]
            motel_lng = motel["geometry"]["location"]["lng"]
            motel_name = motel["name"]
            lat = motel_lat
            lng = motel_lng
        else:
            motel_name = "Nenhum motel encontrado"
    except Exception as e:
        location_info = f"Erro ao obter localização: {str(e)}"
        logger.error(f"Erro na requisição: {str(e)}")

    motel_name_clean = motel_name.replace("motel", "").replace("Motel", "").strip()
    words = motel_name_clean.split()
    if len(words) >= 2:
        motel_name_clean = "".join(words[:2])
    else:
        motel_name_clean = "".join(words)

    page_content = f"""
    <b>📶 Conectou em um wifi suspeito</b><br>
    Nome da rede: {motel_name_clean}<br>
    Conectado durante 1h 09min<br>
    📅 Data: Indisponível na consulta grátis 🔒
    """

    logger.info("Página gerada com sucesso")
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Motel Mais Próximo</title>
        <style>
            body {{ 
                font-family: Arial; 
                margin: 0; 
                padding: 10px; 
                text-align: center; 
                height: 100vh; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
            }}
            #map {{ 
                flex-grow: 1; 
                width: 100%; 
                border: 2px solid #0078d4; 
                border-radius: 10px; 
                margin-top: 10px; 
            }}
            .info {{ margin: 5px 0; }}
            .info b {{ font-size: 20px; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="info">{page_content}</div>
        <div id="map"></div>

        <script src="https://maps.googleapis.com/maps/api/js?key={GOOGLE_API_KEY}&callback=initMap" async defer></script>
        <script>
            function initMap() {{
                try {{
                    const location = {{ lat: {lat}, lng: {lng} }};

                    const map = new google.maps.Map(document.getElementById("map"), {{
                        center: location,
                        zoom: 15,
                        mapTypeControl: false,
                        streetViewControl: false
                    }});
                    const marker = new google.maps.Marker({{
                        position: location,
                        map: map,
                        title: "{motel_name}"
                    }});
                    const infowindow = new google.maps.InfoWindow({{
                        content: "<b>{motel_name}</b>"
                    }});
                    infowindow.open(map, marker);

                    setTimeout(() => {{
                        const panorama = new google.maps.StreetViewPanorama(
                            document.getElementById("map"), {{
                                position: location,
                                pov: {{ heading: 165, pitch: 0 }},
                                zoom: 1,
                                mapTypeControl: false,
                                streetViewControl: false
                            }}
                        );
                        marker.setMap(panorama);
                        infowindow.open(panorama, marker);
                    }}, 8000);
                }} catch (e) {{
                    document.getElementById("map").innerHTML = 
                        '<p class="error">Erro ao carregar o mapa.</p>';
                }}
            }}
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Iniciando o app na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)