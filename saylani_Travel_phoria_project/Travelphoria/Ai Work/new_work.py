import random
import string
import datetime
import requests
import google.generativeai as genai

# Gemini API Key Configuration
genai.configure(api_key="AIzaSyArVJ1R42HiNILtcticOivWfg4u9FKtrJw")
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-lite")

currency_codes = {
    "united states": "USD",
    "pakistan": "PKR",
    "india": "INR",
    "united kingdom": "GBP",
    "europe": "EUR",
    "france": "EUR",
    "germany": "EUR",
    "uae": "AED",
    "china": "CNY",
    "japan": "JPY",
    "canada": "CAD",
    "australia": "AUD",
    "saudi arabia": "SAR",
    "turkey": "TRY",
}

# Fetch location destination ID from Booking.com-like API (via Amadeus Mock)
def get_destination_id(city_name):
    try:
        response = requests.get(
            "https://autocomplete.travelpayouts.com/places2",
            params={"term": city_name, "locale": "en", "types[]": "city"}
        )
        data = response.json()
        if data:
            return data[0]['id']
        return None
    except:
        return None

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_osm_link(place, country):
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{place}, {country}", "format": "json", "limit": 1},
            headers={"User-Agent": "MyTravelApp/1.0 (asad@example.com)"}
        )
        data = resp.json()
        if data:
            lat, lon = data[0]["lat"], data[0]["lon"]
            return f"[{place}](https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=14/{lat}/{lon})"
        return f"{place} (location not found)"
    except Exception:
        return f"{place} (OSM error)"

def get_place_image(place, country):
    try:
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original",
            "titles": f"{place}, {country}"
        }
        res = requests.get(search_url, params=params)
        pages = res.json().get("query", {}).get("pages", {})
        for page in pages.values():
            return page.get("original", {}).get("source", "Image not found")
        return "Image not found"
    except:
        return "Image fetch error"

def get_user_inputs():
    name = input("Enter your name: ")
    from_country = input("Enter your current country: ").strip().lower()
    to_country = input("Enter the country you want to visit: ").strip().lower()
    budget = int(input("Enter your total budget in USD: "))
    start_day = input("Enter start day (YYYY-MM-DD): ")
    end_day = input("Enter end day (YYYY-MM-DD): ")
    unique_id = generate_unique_id()

    from_currency = currency_codes.get(from_country, "USD")
    to_currency = currency_codes.get(to_country, "USD")

    return {
        "name": name,
        "from_country": from_country,
        "to_country": to_country,
        "budget": budget,
        "start_day": start_day,
        "end_day": end_day,
        "unique_id": unique_id,
        "from_currency": from_currency,
        "to_currency": to_currency
    }

def create_prompt(user_data):
    return f"""
You're a travel planner AI assistant.

User Info:
- Name: {user_data['name']}
- From: {user_data['from_country'].title()} ({user_data['from_currency']})
- To: {user_data['to_country'].title()} ({user_data['to_currency']})
- Budget: ${user_data['budget']} USD
- Travel Dates: {user_data['start_day']} to {user_data['end_day']}
- Unique ID: {user_data['unique_id']}

Your tasks:
1. Select 2–3 best cities in {user_data['to_country'].title()}.
2. For each city, suggest top attractions & preferences.
3. Divide daily plan into Morning, Afternoon, and Evening for each day.
4. Suggest different places each day.
5. Suggest the best hotels (name + price + booking link) per city within budget.
6. Suggest 1 flight from {user_data['from_country'].title()} to {user_data['to_country'].title()} and 1 return flight (with estimated prices and booking link).
7. Flight and hotel links should auto-fill real parameters. Use: `https://www.skyscanner.com/transport/flights/{{from_code}}/{{to_code}}/{{date}}`
8. Keep full trip within budget and break down daily cost.
9. Give clean, short, beautiful response.
10. For each place mentioned, return only the place names (to pass into OSM + image API).
"""

def print_package(user_data, response, osm_places):
    print("\n--- TravelPhoria Itinerary Package ---")
    print("👤 Name:", user_data['name'])
    print("🄚 User ID:", user_data['unique_id'])
    print("🌍 From:", user_data['from_country'].title(), f"({user_data['from_currency']})")
    print("✈️ To:", user_data['to_country'].title(), f"({user_data['to_currency']})")
    print("💰 Budget:", user_data['budget'], "USD")
    print("🗓 Dates:", user_data['start_day'], "to", user_data['end_day'])
    print("\n📦 Your Personalized Itinerary:")
    print(response)
    print("\n🌐 Places with Maps & Photos:")
    for place in osm_places:
        osm_link = get_osm_link(place, user_data['to_country'])
        image_url = get_place_image(place, user_data['to_country'])
        print(f"- {osm_link}")
        print(f"  🖼️ Image: {image_url}\n")

def main():
    user_data = get_user_inputs()
    prompt = create_prompt(user_data)
    response = model.generate_content(prompt)
    text = response.text

    # Extract place names from Gemini output (for demo, static list)
    osm_places = ["Eiffel Tower", "Louvre Museum", "Montmartre"]

    # Example city ID fetch (for real hotel API)
    for city in osm_places:
        city_id = get_destination_id(city)
        print(f"City: {city}, Destination ID: {city_id}")

    print_package(user_data, text, osm_places)

if __name__ == "__main__":
    main()
