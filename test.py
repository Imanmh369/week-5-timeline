import requests
import json
import re

CULTURE_LOCATIONS = {
    "French": {"country": "France", "lat": 46.2276, "lon": 2.2137},
    "Italian": {"country": "Italy", "lat": 41.8719, "lon": 12.5674},
    "American": {"country": "USA", "lat": 37.0902, "lon": -95.7129},
    "German": {"country": "Germany", "lat": 51.1657, "lon": 10.4515},
    "Spanish": {"country": "Spain", "lat": 40.4637, "lon": -3.7492},
    "British": {"country": "UK", "lat": 55.3781, "lon": -3.4360},
    "Dutch": {"country": "Netherlands", "lat": 52.1326, "lon": 5.2913}
}

def get_year(date_str):
    date_str = str(date_str)
    if "B.C" in date_str.upper():
        match = re.search(r'\d+', date_str)
        return -int(match.group()) if match else -2000
    match = re.search(r'\d{4}', date_str)
    return int(match.group()) if match else None

def get_era(year):
    if year is None: return "Unknown"
    if year < 0: return "Ancient"
    if year < 1850: return "Classic"
    if year < 1900: return "Impressionism"
    if year < 1950: return "Modern"
    return "Contemporary"

def get_country(culture_field):
    """Checks the culture string against our mapping."""
    culture_str = " ".join(culture_field) if isinstance(culture_field, list) else str(culture_field)
    for key, info in CULTURE_LOCATIONS.items():
        if key.lower() in culture_str.lower():
            return info
    return {"country": "Unknown", "lat": 0, "lon": 0}

def get_life_dates(creator_desc):
    matches = re.findall(r'(\d{4})[-–](\d{4})', creator_desc)
    if matches:
        return int(matches[0][0]), int(matches[0][1])
    return None, None

def fetch_and_process():
    params = {'limit': 900, 'has_image': 1}
    url = "https://openaccess-api.clevelandart.org/api/artworks"
    
    response = requests.get(url, params=params)
    if response.status_code != 200: return

    raw_data = response.json().get('data', [])
    processed = []

    for item in raw_data:
        # Calculate year and era first
        year = get_year(item.get("creation_date", ""))
        era = get_era(year)
        
        # FILTER: Skip items with Unknown era
        if era == "Unknown": continue
        
        creators = item.get("creators", [])
        if not creators: continue
        
        desc = creators[0].get("description", "Unknown")
        birth, death = get_life_dates(desc)
        img_url = item.get("images", {}).get("web", {}).get("url", "")
        
        # Get location info
        loc = get_country(item.get("culture", ""))
        
        if img_url:
            processed.append({
                "title": item.get("title", "Untitled"),
                "year": year,
                "era": era,
                "image_url": img_url,
                "artist": desc.split(" (")[0],
                "birthYear": birth,
                "deathYear": death,
                "country": loc["country"],
                "lat": loc["lat"],
                "lon": loc["lon"]
            })
            
    with open('artists.json', 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=4)
    print(f"Success! {len(processed)} artworks processed.")

if __name__ == "__main__":
    fetch_and_process()