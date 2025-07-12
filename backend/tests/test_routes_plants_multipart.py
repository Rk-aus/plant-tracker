from io import BytesIO
import pytest
from app import create_app


# Fixture to initialize test client
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add_plant_with_image(client):
    data = {
        "plant_name_en": "Sunflower",
        "plant_name_ja": "ヒマワリ",
        "plant_class_en": "Asteraceae",
        "plant_class_ja": "キク科",
        "image": (BytesIO(b"fake image bytes"), "sunflower.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code == 201
    assert response.json["message"] == "Plant added"


def test_add_plant_missing_image(client):
    data = {
        "plant_name_en": "Lily",
        "plant_name_ja": "ユリ",
        "plant_class_en": "Liliaceae",
        "plant_class_ja": "ユリ科",
        # image is missing
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code == 400
    assert "image" in response.json["error"]
