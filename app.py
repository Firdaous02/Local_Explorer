from flask import Flask, render_template, request, jsonify
import requests
import openai
from datetime import datetime
import json
import re

app = Flask(__name__)

#GEOLOCATION_API_KEY = "c35a267b91d84a12ad287e192b3868c6"
WEATHER_API_KEY = "a0aa9fb25cde4fe77e244112130cbc3a"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY
OPENCAGE_API_KEY = "cb75a1dca26045d696013cb5cf1e75f2"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_suggestions", methods=["POST"])
def get_suggestions():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    #time_of_day = data.get("time_of_day")

    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    # Récupération des données météo
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return jsonify({"error": "Failed to retrieve weather data"}), weather_response.status_code

    weather_data = weather_response.json()
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    city = weather_data["name"]
    country = weather_data["sys"]["country"]

    # Determine the time of day
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        time_of_day = "morning"
    elif 12 <= current_hour < 18:
        time_of_day = "afternoon"
    elif 18 <= current_hour < 22:
        time_of_day = "evening"
    else:
        time_of_day = "night"

    messages = [
        {"role": "system", "content": "You are an assistant that provides activity suggestions based on weather and time of day."},
        {"role": "user", "content": (
            f"Based on the following details, suggest 3 activities: \n"
            f"Weather: {weather_description}, Temperature: {temperature}°C, Time of day: {time_of_day}, Location: {city}, {country}. \n"
            f"Output the result as a JSON array. Each object should include the keys 'place', 'address', 'activity', and 'description'. \n"
            f"Make sure the output is valid JSON without extra text."
            f"Include both indoor and outdoor options, and make them varied."
        )}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        json_gpt_response = response['choices'][0]['message']['content'].strip()
        print("Réponse brute de GPT:", json_gpt_response)

        places = extract_address_from_json(json_gpt_response)
        places_with_coordinates = get_places_coordinates(places, OPENCAGE_API_KEY)


        return jsonify({"suggestions": json_gpt_response, "places_with_coordinates": places_with_coordinates, "weather": weather_description, "temperature": temperature})
    except Exception as e:
        return jsonify({"error": f"Failed to generate activity suggestions: {str(e)}"}), 500


def extract_address_from_json(response):
    try:
        cleaned_response = re.sub(r"^```[a-z]*\n", "", response.strip(), flags=re.MULTILINE)
        cleaned_response = cleaned_response.strip("```").strip()
        
        print("Réponse nettoyée:", cleaned_response)
        
        data = json.loads(cleaned_response)
        print("Data décodée depuis JSON:", data)
        
        if not isinstance(data, list):
            print("La réponse JSON attendue est une liste.")
            return []
        
        addresses = [item['address'] for item in data if 'address' in item]
        print("Adresses extraites:", addresses)
        return addresses
    except json.JSONDecodeError as e:
        print("Erreur de décodage JSON:", e)
        return []
    except KeyError as e:
        print("Erreur KeyError lors de l'extraction des adresses:", e)
        return []



def get_coordinates_from_opencage(place_name, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={place_name}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Data from OpenCage:", data)
        if data['results']:
            location = data['results'][0]['geometry']
            print("location['lat']:", location['lat'])
            print("location['lng']:", location['lng'])
            return location['lat'], location['lng']
    return None, None

def get_places_coordinates(places, api_key):
    places_with_coordinates = []
    for place in places:
        lat, lng = get_coordinates_from_opencage(place, api_key)
        if lat and lng:
            places_with_coordinates.append({
                "place": place,
                "latitude": lat,
                "longitude": lng
            })
        print("Places with coordinates:", places_with_coordinates)
    return places_with_coordinates

if __name__ == "__main__":
    app.run(debug=True)