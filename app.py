from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import requests
import openai
from datetime import datetime
import json
import re
from dotenv import load_dotenv
import os
from models import db, User

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Configuration de l'application
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialiser la base de données
db.init_app(app)

# Configurer les clés API
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')
openai.api_key = OPENAI_API_KEY

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/suggestion")
def suggestion():
    if 'user_id' not in session:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    return render_template("suggestion.html")


@app.route('/get_started')
def get_started():
    if 'user_id' in session:
        return redirect(url_for('suggestion'))
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('suggestion'))
        else:
            flash('Incorrect username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return redirect(url_for('suggestion'))
        except:
            db.session.rollback()
            flash('Username already exists. Try another one.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/dislike', methods=['POST'])
def dislike():
    if 'user_id' not in session:
        return jsonify({"error": "You need to log in first!"}), 401

    data = request.json
    activity = data.get('activity')
    place = data.get('place')

    if not activity or not place:
        return jsonify({"error": "Both 'activity' and 'place' are required"}), 400

    user = db.session.get(User, session['user_id'])

    disliked_activities = json.loads(user.disliked_activities)
    disliked_places = json.loads(user.disliked_places)

    if activity not in disliked_activities:
        disliked_activities.append(activity)

    if place not in disliked_places:
        disliked_places.append(place)

    user.disliked_activities = json.dumps(disliked_activities)
    user.disliked_places = json.dumps(disliked_places)

    db.session.commit()

    return jsonify({
        "message": "Activity and place added to disliked lists",
        "disliked_activities": disliked_activities,
        "disliked_places": disliked_places
    }), 200

@app.route("/get_suggestions", methods=["POST"])
def get_suggestions():
    if 'user_id' not in session:
        return jsonify({"error": "You need to log in first!"}), 401

    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    user = db.session.get(User, session['user_id'])
    disliked_activities = user.disliked_activities
    disliked_places = user.disliked_places

    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={WEATHER_API_KEY}&units=metric"
    weather_response = requests.get(weather_url)

    if weather_response.status_code != 200:
        return jsonify({"error": "Failed to retrieve weather data"}), weather_response.status_code

    weather_data = weather_response.json()
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    city = weather_data["name"]
    country = weather_data["sys"]["country"]

    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        time_of_day = "morning"
    elif 12 <= current_hour < 18:
        time_of_day = "afternoon"
    elif 18 <= current_hour < 22:
        time_of_day = "evening"
    else:
        time_of_day = "night"

    exclusion_text = ""
    if disliked_activities or disliked_places:
        exclusion_text = f"Exclude the following disliked activities: {disliked_activities} and disliked places: {disliked_places}."

    messages = [
        {"role": "system", "content": "You are an assistant that provides activity suggestions based on weather and time of day."},
        {"role": "user", "content": (
            f"Based on the following details, suggest 3 activities: \n"
            f"Weather: {weather_description}, Temperature: {temperature}°C, Time of day: {time_of_day}, Location: {city}, {country}. \n"
            f"Output the result as a JSON array. Each object should include the keys 'place', 'address', 'activity', and 'description'. \n"
            f"Make sure the output is valid JSON without extra text."
            f"Include both indoor and outdoor options, and make them varied."
            f"{exclusion_text}"
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
        suggestions_with_coordinates = get_places_coordinates(json_gpt_response, OPENCAGE_API_KEY)

        return jsonify({"suggestions": suggestions_with_coordinates, "weather": weather_description, "temperature": temperature})
    except Exception as e:
        return jsonify({"error": f"Failed to generate activity suggestions: {str(e)}"}), 500

def clean_gpt_response(response):
    try:
        cleaned_response = re.sub(r"^```[a-z]*\n", "", response.strip(), flags=re.MULTILINE)
        cleaned_response = cleaned_response.strip("```").strip()
        data = json.loads(cleaned_response)
        return data
    except json.JSONDecodeError as e:
        print("Erreur de décodage JSON:", e)
        return []
    except KeyError as e:
        print("Erreur KeyError lors de l'extraction:", e)
        return []

def get_coordinates_from_opencage(place_name, api_key):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={place_name}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            location = data['results'][0]['geometry']
            return location['lat'], location['lng']
    return None, None

def get_places_coordinates(response, api_key):
    suggestions = clean_gpt_response(response)
    places_with_coordinates = []
    for suggestion in suggestions:
        query = f"{suggestion['place']}, {suggestion['address']}"
        lat, lng = get_coordinates_from_opencage(query, api_key)
        if lat and lng:
            places_with_coordinates.append({
                "place": suggestion['place'],
                "address": suggestion['address'],
                "activity": suggestion['activity'],
                "description": suggestion['description'],
                "latitude": lat,
                "longitude": lng
            })
    return places_with_coordinates

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)