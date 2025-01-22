from flask import Flask, render_template, request, jsonify
import requests
import openai
from datetime import datetime

app = Flask(__name__)

GEOLOCATION_API_KEY = "c35a267b91d84a12ad287e192b3868c6"
WEATHER_API_KEY = "a0aa9fb25cde4fe77e244112130cbc3a"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY


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
            f"Based on the following weather conditions and time, suggest 3 activities: \n"
            f"Weather: {weather_description}, Temperature: {temperature}°C, Time of day: {time_of_day}. \n"
            f"Respond in this format:\n"
            f"1. [First activity]\n"
            f"2. [Second activity]\n"
            f"3. [Third activity]\n"
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
        suggestions = response['choices'][0]['message']['content'].strip()
        return jsonify({"suggestions": suggestions, "weather": weather_description, "temperature": temperature})
    except Exception as e:
        return jsonify({"error": f"Failed to generate activity suggestions: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)