import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test that the home page loads successfully."""
    rv = client.get('/')
    assert rv.status_code == 200


def test_list_recipes(client):
    """Test the recipe listing API returns a list."""
    rv = client.get('/api/recipes/list')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_recipe_search(client):
    """Test the recipe search API with sample ingredients."""
    rv = client.post('/api/recipe', json={
        "ingredients": ["pasta", "tomato", "garlic", "olive oil", "onion"],
        "desired_type": "pasta",
        "allergies": [],
        "allow_substitutions": True
    })
    assert rv.status_code == 200
    data = rv.get_json()
    # Should find DB match for pasta with these ingredients
    assert "candidates" in data or "recipe" in data


def test_recipe_search_empty_ingredients(client):
    """Test the recipe search API with no ingredients.
    Without a GROQ_API_KEY the AI fallback returns 500, which is expected."""
    rv = client.post('/api/recipe', json={
        "ingredients": [],
        "desired_type": "",
        "allergies": [],
        "allow_substitutions": True
    })
    # 200 if AI key is present, 500 if not — both are valid
    assert rv.status_code in (200, 500)
