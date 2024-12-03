import pytest
from unittest.mock import patch, Mock
from app import app, fetch_characters, cache




@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            cache.clear()
        yield client

@patch('app.httpx.get')
def test_fetch_characters_returns_correct_data(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': [{'id': 1, 'name': 'Rick Sanchez', 'episode': ['https://rickandmortyapi.com/api/episode/1'], 'origin': {'name': 'Earth'}, 'location': {'name': 'Earth'}}],
        'info': {'pages': 1}
    }
    mock_get.return_value = mock_response

    characters, total_pages = fetch_characters(1)

    assert len(characters) == 1
    assert characters[0]['name'] == 'Rick Sanchez'
    assert total_pages == 1

@patch('app.httpx.get')
def test_fetch_characters_handles_multiple_pages(mock_get):
    mock_response_page_1 = Mock()
    mock_response_page_1.json.return_value = {
        'results': [{'id': 1, 'name': 'Rick Sanchez', 'episode': ['https://rickandmortyapi.com/api/episode/1'], 'origin': {'name': 'Earth'}, 'location': {'name': 'Earth'}}],
        'info': {'pages': 2}
    }
    mock_response_page_2 = Mock()
    mock_response_page_2.json.return_value = {
        'results': [{'id': 2, 'name': 'Morty Smith', 'episode': ['https://rickandmortyapi.com/api/episode/2'], 'origin': {'name': 'Earth'}, 'location': {'name': 'Earth'}}],
        'info': {'pages': 2}
    }
    mock_get.side_effect = [mock_response_page_1, mock_response_page_2]

    characters, total_pages = fetch_characters(1, per_page=2)

    assert len(characters) == 2
    assert characters[0]['name'] == 'Rick Sanchez'
    assert characters[1]['name'] == 'Morty Smith'
    assert total_pages == 2

@patch('app.httpx.get')
def test_fetch_characters_handles_no_results(mock_get, client):
    with app.app_context():
        cache.clear()  # Clear cache before the test
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': [],
        'info': {'pages': 1}
    }
    mock_get.return_value = mock_response

    characters, total_pages = fetch_characters(1)

    assert len(characters) == 0
    assert total_pages == 1

@patch('app.httpx.get')
def test_index_route_renders_correct_template(mock_get, client):
    mock_response_characters = Mock()
    mock_response_characters.json.return_value = {
        'results': [{'id': 1, 'name': 'Rick Sanchez', 'episode': ['https://rickandmortyapi.com/api/episode/1'], 'origin': {'name': 'Earth'}, 'location': {'name': 'Earth'}}],
        'info': {'pages': 1}
    }
    mock_response_locations = Mock()
    mock_response_locations.json.return_value = {
        'info': {'count': 1}
    }
    mock_response_episodes = Mock()
    mock_response_episodes.json.return_value = {
        'info': {'count': 1}
    }
    mock_response_episode = Mock()
    mock_response_episode.json.return_value = {
        'name': 'Pilot'
    }
    mock_get.side_effect = [mock_response_characters, mock_response_locations, mock_response_episodes, mock_response_episode]

    response = client.get('/')

    assert response.status_code == 200
    assert b'Rick Sanchez' in response.data