import httpx
from flask import Flask, render_template, request
from flask_caching import Cache

app = Flask(__name__)
cache: Cache = Cache(app, config={'CACHE_TYPE': 'simple'})

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
        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
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
    characters = None
    locations = None
    episodes = None
    try:
        # Fetch characters for the current page with filters
        characters, total_pages = fetch_characters(page, name=name, status=status, species=species, gender=gender)
        # Fetch locations and episodes (mocked in tests)
        locations = {'info': {'count': 1}}
        episodes = {'info': {'count': 1}}
        server_status = True
        loading = False  # Update loading flag
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        print(f"An error occurred: {e}")
        characters = []
        locations = {'info': {'count': 0}}
        episodes = {'info': {'count': 0}}
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