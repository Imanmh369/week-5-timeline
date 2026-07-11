import requests
import json
import re

def get_year(date_str):
    """Extracts the first 4-digit year found in string."""
    match = re.search(r'\d{4}', str(date_str))
    return int(match.group()) if match else 2000

def get_era(year):
    """Categorizes artwork into era buckets."""
    if year >= 1950: return "Contemporary"
    if year >= 1900: return "Modern"
    if year >= 1850: return "Impressionism"
    return "Classic"

def fetch_and_process():
    # Fetch 600 items from the Cleveland Museum of Art API
    params = {'limit': 600, 'has_image': 1}
    url = "https://openaccess-api.clevelandart.org/api/artworks"
    
    print("Fetching data from API...")
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return

    raw_data = response.json().get('data', [])
    processed = []

    for item in raw_data:
        year = get_year(item.get("creation_date", "2000"))
        img_data = item.get("images", {}).get("web", {}).get("url", "")
        
        # Safely handle the creators list to avoid IndexError
        creators_list = item.get("creators", [])
        artist_name = "Unknown"
        if isinstance(creators_list, list) and len(creators_list) > 0:
            artist_name = creators_list[0].get("description", "Unknown")
            
        # FILTER: Only include if we have a valid image and a known artist
        if img_data and artist_name != "Unknown":
            processed.append({
                "title": item.get("title", "Untitled"),
                "year": year,
                "era": get_era(year),
                "image_url": img_data,
                "artist": artist_name
            })
            
    # Write the cleaned data to JSON
    with open('artists.json', 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=4)
        print(f"Success! {len(processed)} artworks with known artists saved to artists.json.")

if __name__ == "__main__":
    fetch_and_process()