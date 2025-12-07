from flask import Flask, render_template, request, redirect, url_for, flash
import numpy as np
import pickle
import pandas as pd
import requests
import datetime
import sqlite3

# Load the trained model
model = pickle.load(open('Crop_Recommendation.pkl', 'rb'))

# Crop mapping dictionary
crop_mapping = {
    1: 'Sugarcane', 2: 'Jowar', 3: 'Cotton', 4: 'Rice', 5: 'Wheat',
    6: 'Groundnut', 7: 'Maize', 8: 'Tur', 9: 'Urad', 10: 'Moong',
    11: 'Gram', 12: 'Masoor', 13: 'Soybean', 14: 'Ginger', 15: 'Turmeric', 16: 'Grapes'
}

# Soil color mapping
soil_color_mapping = {
    'Black': 0, 'Red': 1, 'Alluvial': 2, 'Laterite': 3, 'Clayey': 4, 'Sandy': 5
}

# Fertilizer mapping with specific recommendations
fertilizer_mapping = {
    "Nitrogen Deficient": "Apply 50kg Urea per hectare",
    "Phosphorus Deficient": "Apply 40kg Single Super Phosphate (SSP) per hectare",
    "Potassium Deficient": "Apply 30kg Muriate of Potash (MOP) per hectare"
}

# Seasonal crop recommendations
seasonal_crops = {
    "Winter": ["Wheat", "Mustard", "Peas"],
    "Summer": ["Rice", "Maize", "Sugarcane"],
    "Monsoon": ["Paddy", "Jowar", "Bajra"]
}

def get_season():
    month = datetime.datetime.now().month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5, 6]:
        return "Summer"
    else:
        return "Monsoon"

# Crop disease mapping
crop_diseases = {
    "Sugarcane": {"diseases": ["Red Rot", "Smut", "Mosaic Disease"], "prevention": "Use disease-resistant varieties, avoid water stagnation, and apply fungicides."},
    "Jowar": {"diseases": ["Grain Mold", "Anthracnose", "Sorghum Downy Mildew"], "prevention": "Use treated seeds, rotate crops, and apply appropriate fungicides."},
    "Cotton": {"diseases": ["Bacterial Blight", "Boll Rot", "Leaf Curl Virus"], "prevention": "Use resistant varieties, avoid excessive nitrogen, and control insect vectors."},
    "Rice": {"diseases": ["Bacterial Leaf Blight", "Blast Disease", "Brown Spot"], "prevention": "Use resistant varieties, maintain proper spacing, and apply fungicides like Tricyclazole."},
    "Wheat": {"diseases": ["Rust", "Powdery Mildew", "Smut"], "prevention": "Use certified seeds, avoid excess nitrogen fertilizers, and apply Mancozeb fungicide."},
    "Groundnut": {"diseases": ["Tikka Leaf Spot", "Rust", "Aflatoxin Contamination"], "prevention": "Use disease-free seeds, avoid excessive moisture, and apply fungicides like Chlorothalonil."},
    "Maize": {"diseases": ["Turcicum Leaf Blight", "Downy Mildew", "Stalk Rot"], "prevention": "Use hybrid seeds, practice crop rotation, and ensure proper soil drainage."},
    "Tur": {"diseases": ["Wilt", "Sterility Mosaic Disease", "Leaf Spot"], "prevention": "Use resistant varieties, avoid waterlogging, and spray recommended fungicides."},
    "Urad": {"diseases": ["Yellow Mosaic Virus", "Leaf Spot", "Rust"], "prevention": "Use certified seeds, control whitefly vectors, and apply protective fungicides."},
    "Moong": {"diseases": ["Yellow Mosaic Virus", "Root Rot", "Powdery Mildew"], "prevention": "Use virus-free seeds, avoid excess nitrogen, and apply sulfur-based fungicides."},
    "Gram": {"diseases": ["Ascochyta Blight", "Wilt", "Rust"], "prevention": "Use resistant varieties, seed treatment with fungicides, and proper field sanitation."},
    "Masoor": {"diseases": ["Rust", "Wilt", "Downy Mildew"], "prevention": "Use clean seeds, maintain crop rotation, and apply Mancozeb spray."},
    "Soybean": {"diseases": ["Rust", "Bacterial Pustule", "Frogeye Leaf Spot"], "prevention": "Use disease-free seeds, avoid excessive nitrogen, and apply preventive fungicides."},
    "Ginger": {"diseases": ["Soft Rot", "Rhizome Rot", "Leaf Spot"], "prevention": "Use treated rhizomes, avoid excessive irrigation, and apply copper-based fungicides."},
    "Turmeric": {"diseases": ["Rhizome Rot", "Leaf Blotch", "Powdery Mildew"], "prevention": "Use disease-free planting material, maintain proper drainage, and apply protective fungicides."},
    "Grapes": {"diseases": ["Downy Mildew", "Powdery Mildew", "Anthracnose"], "prevention": "Ensure good air circulation, prune infected leaves, and spray Bordeaux mixture."}
}

# Function to fetch weather data
def get_weather(city):
    API_KEY = "b9cefed30927f505b255e35d8593b583"  # Replace with your Weatherstack API Key
    url = f"http://api.weatherstack.com/current?access_key={API_KEY}&query={city}"
    response = requests.get(url).json()

    if "current" in response:
        return {
            "temperature": response["current"].get("temperature"),
            "humidity": response["current"].get("humidity"),
            "weather_desc": response["current"]["weather_descriptions"][0]
        }
    else:
        return None

app = Flask(__name__)
app.secret_key = "your_very_secret_key"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        city = request.form['city']  # Get city from user
        weather_data = get_weather(city)  # Fetch weather data

        if not weather_data:
            return render_template('index.html', prediction_text="Invalid city name!", weather_info="Weather data not available.")

        temperature = float(request.form['temperature'])  # Manual temperature input
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        potassium = float(request.form['potassium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        soil_color = request.form['soil_color']
        
        # Encode soil color
        soil_color_encoded = soil_color_mapping.get(soil_color, -1)
        
        # Create a NumPy array for model prediction
        features = np.array([[soil_color_encoded, nitrogen, phosphorus, potassium, ph, rainfall, temperature]])
        prediction_number = model.predict(features)[0]
        prediction_crop = crop_mapping.get(prediction_number, 'Unknown Crop')

        # Fetch disease information
        if prediction_crop in crop_diseases:
            disease_info = crop_diseases[prediction_crop]
            disease_text = f"Common Diseases: {', '.join(disease_info['diseases'])}"
            prevention_text = f"Prevention Tips: {disease_info['prevention']}"
        else:
            disease_text = "No disease data available."
            prevention_text = ""

        # Seasonal crop recommendation
        season = get_season()
        recommended_seasonal_crops = seasonal_crops[season]
        seasonal_crop_text = f"Suggested Seasonal Crops: {', '.join(recommended_seasonal_crops)}"

        weather_info = f"Weather in {city}: {weather_data['weather_desc']}, {weather_data['temperature']}°C, Humidity: {weather_data['humidity']}%"

        return render_template(
            'index.html',
            prediction_text=f"Recommended Crop: {prediction_crop}",
            fertilizer_text=f"Suggested Fertilizers: {fertilizer_mapping}",
            seasonal_crop_text=seasonal_crop_text,
            weather_info=weather_info,
            disease_text=disease_text,
            prevention_text=prevention_text
        )
    except Exception as e:
        return render_template('index.html', prediction_text=f'Error: {str(e)}')


if __name__ == '__main__':
    app.run(debug=True)
