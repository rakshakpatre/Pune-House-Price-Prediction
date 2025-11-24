import streamlit as st
st.markdown("""
<style>

body {
    background-color: #0d0d0d !important;
}

div.stButton > button:first-child {
    background: linear-gradient(90deg,#b8860b,#ffd700);
    color: black;
    font-weight: 800;
    font-size: 18px;
    padding: 12px 20px;
    border-radius: 12px;
    border: none;
    width: 50   %;
    transition: 0.2s ease;
}
div.stButton > button:first-child:hover {
    background: linear-gradient(90deg,#ffcc00,#ffde7b);
    transform: scale(1.03);
}

.result-box-luxury {
    background: linear-gradient(135deg,#000000,#2c2c2c);
    padding: 22px;
    border-radius: 14px;
    color: #ffd700;
    font-size: 28px;
    font-weight: 900;
    text-align: center;
    border: 2px solid #d4af37;
    box-shadow: 0 0 25px rgba(255,215,0,0.25);
}

.location-card {
    background: #111;
    color: white;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 8px;
    border: 1px solid #d4af37;
    font-size: 18px;
    font-weight: 600;
    box-shadow: 0px 0px 6px rgba(212,175,55,0.4);
}
.location-card:hover {
    background: #1a1a1a;
    transform: scale(1.01);
}

.section-title {
    color: #ffd700;
    font-weight: 900;
    font-size: 24px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

import pandas as pd
import pathlib
import pickle

# ----------------------------
# PAGE CONFIGURATION
# ----------------------------
st.set_page_config(
    page_title="🏡 Pune House Price Prediction",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Load Model & Columns
# ----------------------------
BASE_DIR = pathlib.Path.cwd()

MODEL_PATH = BASE_DIR / "rf_model.pkl"
COLUMNS_PATH = BASE_DIR / "model_columns.pkl"

with open(MODEL_PATH, "rb") as f:
    rf_model = pickle.load(f)

with open(COLUMNS_PATH, "rb") as f:
    model_columns = pickle.load(f)

# ----------------------------
# Sidebar Input Section
# ----------------------------
st.sidebar.title("Enter House Details")

# Load data to extract dropdowns dynamically
@st.cache_data
def load_data():
    df = pd.read_csv("Pune_House_Data.csv")
    df = df.dropna()
    df['bhk'] = df['size'].apply(lambda x: int(x.split(' ')[0]) if isinstance(x, str) else x)
    df['site_location'] = df['site_location'].apply(lambda x: x.strip())
    return df

df = load_data()

locations = sorted(df['site_location'].unique())
area_types = sorted(df['area_type'].unique())
availabilities = sorted(df['availability'].unique())



location = st.sidebar.selectbox("Location", locations)
bhk = st.sidebar.number_input("BHK (Bedrooms)", 1, 10, 2)
bath = st.sidebar.number_input("Bathrooms", 1, 10, 2)
balcony = st.sidebar.number_input("Balconies", 0, 5, 1)
sqft = st.sidebar.number_input("Total Square Feet", 100, 20000, 1000)
area_type = st.sidebar.selectbox("Area Type", area_types)
availability = st.sidebar.selectbox("Availability", availabilities)

# ----------------------------
# Prediction Function
# ----------------------------
def predict_price(location, bhk, bath, balcony, sqft, area_type, availability):
    x = pd.DataFrame(columns=model_columns)
    x.loc[0] = 0

    x.at[0, 'bhk'] = bhk
    x.at[0, 'bath'] = bath
    x.at[0, 'balcony'] = balcony
    x.at[0, 'new_total_sqft'] = sqft

    for col, val in [
        (f'site_location_{location}', 1),
        (f'area_type_{area_type}', 1),
        (f'availability_{availability}', 1),
    ]:
        if col in x.columns:
            x.at[0, col] = val

    return round(rf_model.predict(x)[0], 2)

def recommend_similar_locations(location, price, sqft):
    price_in_rupees = price * 100000
    price_per_sqft = price_in_rupees / sqft

    lower = price_per_sqft * 0.90
    upper = price_per_sqft * 1.10

    # Convert to numeric to avoid float/string error
    df['total_sqft'] = pd.to_numeric(df['total_sqft'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['total_sqft', 'price'], inplace=True)

    df['price_per_sqft'] = (df['price'] * 100000) / df['total_sqft']

    similar = df[(df['price_per_sqft'] >= lower) & (df['price_per_sqft'] <= upper)]

    similar_locations = similar['site_location'].drop_duplicates()
    similar_locations = similar_locations[similar_locations != location].head(5)

    return list(similar_locations)



# ----------------------------
# Main Title & Button
# ----------------------------
st.markdown("<h1 style='text-align: center;'>🏡 Pune House Price Prediction</h1>", unsafe_allow_html=True)

def get_google_maps_link(location):
    base_url = "https://www.google.com/maps/search/"
    return f"{base_url}{location.replace(' ', '+')}+Pune"


if st.button("Predict Price"):

    price = predict_price(location, bhk, bath, balcony, sqft, area_type, availability)

    st.markdown(f"""
        <div class='result-box-luxury'>
            Estimated Price: ₹ {price} Lakhs
        </div>
    """, unsafe_allow_html=True)

   
    similar_locations = recommend_similar_locations(location, price, sqft)

    st.markdown("<div class='section-title'>📍 Similar Price Locations</div>", unsafe_allow_html=True)

    if similar_locations:
        for loc in similar_locations:
            st.markdown(f"<div class='location-card'>🏡 {loc}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='location-card' style='border-color:#ff4d4d;color:#ff4d4d;'>
            ❗ No similar premium locations found — try adjusting values
        </div>""", unsafe_allow_html=True)

     # Google Maps Link
    maps_url = get_google_maps_link(location)
    st.markdown(f"""
        <a href="{maps_url}" target="_blank">
            <button style="
                background: #ffd700;
                color: black;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 18px;
                border-radius: 8px;
                border: none;
                margin-top: 12px;
                margin-bottom: 12px;
                cursor: pointer;
            ">
                📍 View Location on Google Maps
            </button>
        </a>
    """, unsafe_allow_html=True)



# ----------------------------
# Optional Input Details
# ----------------------------
with st.expander("📋 Show Input Details"):
    st.write({
        "Location": location,
        "BHK": bhk,
        "Bathrooms": bath,
        "Balconies": balcony,
        "Total Sqft": sqft,
        "Area Type": area_type,
        "Availability": availability,
    })
