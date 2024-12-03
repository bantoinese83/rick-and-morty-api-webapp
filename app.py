import httpx
from flask import Flask, render_template, request
from flask_caching import Cache

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

API_BASE_URL = "https://rickandmortyapi.com/api"

@cache.memoize(timeout=300)
def fetch_characters(page, per_page=16, name=None, status=None, species=None, gender=None):
    data = {}
    characters = []
    current_page = page
    params = {
        "page": current_page,
        "name": name,
        "status": status,
        "species": species,
        "gender": gender
    }
    while len(characters) < per_page:
        response = httpx.get(f"{API_BASE_URL}/character", params=params)
        response.raise_for_status()
        data = response.json()
        characters.extend(data['results'])
        if len(characters) >= per_page or current_page >= data['info']['pages']:
            break
        current_page += 1
        params["page"] = current_page
    return characters[:per_page], data['info']['pages']

@app.route("/")
def index():
    total_pages = 1
    page = request.args.get('page', 1, type=int)
    name = request.args.get('name')
    status = request.args.get('status')
    species = request.args.get('species')
    gender = request.args.get('gender')
    loading = True  # Initialize loading flag
    characters = locations = episodes = None
    try:
        # Fetch characters for the current page with filters
        characters, total_pages = fetch_characters(page, name=name, status=status, species=species, gender=gender)

        locations_response = httpx.get(f"{API_BASE_URL}/location")
        locations_response.raise_for_status()
        locations = locations_response.json()

        episodes_response = httpx.get(f"{API_BASE_URL}/episode")
        episodes_response.raise_for_status()
        episodes = episodes_response.json()

        # Fetch episode names for each character
        for character in characters:
            first_episode_url = character['episode'][0]
            episode_response = httpx.get(first_episode_url)
            episode_response.raise_for_status()
            episode = episode_response.json()
            character['first_seen_in'] = episode['name']

        server_status = True
        loading = False  # Update loading flag
    except httpx.RequestError as e:
        print(f"An error occurred while requesting data: {e}")
        server_status = False
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        server_status = False
    except ValueError as e:
        print(f"JSON decoding failed: {e}")
        server_status = False

    return render_template(
        "index.html",
        characters=characters,
        locations=locations,
        episodes=episodes,
        server_status=server_status,
        loading=loading,
        page=page,
        total_pages=total_pages,
        name=name,
        status=status,
        species=species,
        gender=gender
    )

if __name__ == "__main__":
    app.run(debug=True)