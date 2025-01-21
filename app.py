from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Clés API
GEOLOCATION_API_KEY = "c35a267b91d84a12ad287e192b3868c6"
WEATHER_API_KEY = "a0aa9fb25cde4fe77e244112130cbc3a"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_location", methods=["POST"])
def get_location():
    location_data = request.json.get("ip_address", "")
    if not location_data:
        return jsonify({"error": "Location data (latitude,longitude) is required"}), 400
    
    latitude, longitude = map(float, location_data.split(','))  # Convertit les coordonnées en float
    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={GEOLOCATION_API_KEY}&latitude={latitude}&longitude={longitude}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to retrieve location data"}), response.status_code

@app.route("/get_weather", methods=["POST"])
def get_weather():
    # Récupère les données latitude et longitude du client
    lat = request.json.get("latitude")
    lon = request.json.get("longitude")
    
    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    # Requête à l'API OpenWeatherMap
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url)
    
    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        return jsonify(weather_data)
    else:
        return jsonify({"error": "Failed to retrieve weather data"}), weather_response.status_code

if __name__ == "__main__":
    app.run(debug=True)
