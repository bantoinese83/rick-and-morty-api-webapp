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

@cache.memoize(timeout=300)
def fetch_total_counts():
    response_characters = httpx.get(f"{API_BASE_URL}/character")
    response_characters.raise_for_status()
    total_characters = response_characters.json()['info']['count']

    response_locations = httpx.get(f"{API_BASE_URL}/location")
    response_locations.raise_for_status()
    total_locations = response_locations.json()['info']['count']

    response_episodes = httpx.get(f"{API_BASE_URL}/episode")
    response_episodes.raise_for_status()
    total_episodes = response_episodes.json()['info']['count']

    return total_characters, total_locations, total_episodes

@app.route("/")
def index():
    total_pages = 1
    page = request.args.get('page', 1, type=int)
    name = request.args.get('name')
    status = request.args.get('status')
    species = request.args.get('species')
    gender = request.args.get('gender')
    loading = True
    characters = None
    locations = None
    episodes = None
    try:
        characters, total_pages = fetch_characters(page, name=name, status=status, species=species, gender=gender)
        total_characters, total_locations, total_episodes = fetch_total_counts()
        server_status = True
        loading = False
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        print(f"An error occurred: {e}")
        characters = []
        total_characters = 0
        total_locations = 0
        total_episodes = 0
        server_status = False

    return render_template(
        "index.html",
        characters=characters,
        total_characters=total_characters,
        total_locations=total_locations,
        total_episodes=total_episodes,
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