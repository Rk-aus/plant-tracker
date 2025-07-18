from io import BytesIO
import pytest
from app import create_app


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
    assert "image" in response.json["error"].lower()


def test_add_plant_missing_name(client):
    data = {
        # Missing "plant_name_en"
        "plant_name_ja": "ヒマワリ",
        "plant_class_en": "Asteraceae",
        "plant_class_ja": "キク科",
        "image": (BytesIO(b"fake image"), "file.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code == 400
    assert "plant_name_en" in response.json["error"].lower()


def test_add_plant_invalid_image_type(client):
    data = {
        "plant_name_en": "WeirdPlant",
        "plant_name_ja": "ヘンな植物",
        "plant_class_en": "Unknown",
        "plant_class_ja": "不明",
        "image": (BytesIO(b"not an image"), "fake.txt"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code in [400, 415]
    assert "image" in response.json["error"].lower()


def test_add_plant_missing_api_key(client):
    data = {
        "plant_name_en": "Tulip",
        "plant_name_ja": "チューリップ",
        "plant_class_en": "Liliaceae",
        "plant_class_ja": "ユリ科",
        "image": (BytesIO(b"image"), "tulip.jpg"),
    }

    response = client.post("/plants", data=data, content_type="multipart/form-data")

    assert response.status_code == 401
    assert "api key" in response.json["error"].lower()


def test_add_plant_invalid_api_key(client):
    data = {
        "plant_name_en": "Rose",
        "plant_name_ja": "バラ",
        "plant_class_en": "Rosaceae",
        "plant_class_ja": "バラ科",
        "image": (BytesIO(b"rose image"), "rose.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "wrong_key"},
    )

    assert response.status_code == 403
    assert "api key" in response.json["error"].lower()


def test_add_plant_duplicate(client):
    def make_data():
        return {
            "plant_name_en": "Mint",
            "plant_name_ja": "ミント",
            "plant_class_en": "Lamiaceae",
            "plant_class_ja": "シソ科",
            "image": (BytesIO(b"image"), "mint.jpg"),
        }

    response1 = client.post(
        "/plants",
        data=make_data(),
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )
    response2 = client.post(
        "/plants",
        data=make_data(),
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response2.status_code == 409


def test_add_plant_with_invalid_date_format(client):
    data = {
        "plant_name_en": "Daisy",
        "plant_name_ja": "ヒナギク",
        "plant_class_en": "Asteraceae",
        "plant_class_ja": "キク科",
        "plant_date": "15-03-2023",  # Invalid format
        "image": (BytesIO(b"image"), "daisy.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code == 400
    assert "date" in response.json["error"].lower()


def test_add_plant_with_large_image(client):
    large_image = BytesIO(b"x" * (1024 * 1024 * 2))  # 2MB dummy image
    data = {
        "plant_name_en": "Bigleaf",
        "plant_name_ja": "大きな葉",
        "plant_class_en": "Bigaceae",
        "plant_class_ja": "ビガ科",
        "image": (large_image, "bigleaf.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code == 201


def test_add_plant_with_whitespace_only_fields(client):
    data = {
        "plant_name_en": "   ",  # Just spaces
        "plant_name_ja": "　",  # Full-width space
        "plant_class_en": "Rosaceae",
        "plant_class_ja": "バラ科",
        "image": (BytesIO(b"image"), "white.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code == 400
    assert "plant_name_en" in response.json["error"].lower()


def test_add_plant_sql_injection_attempt(client):
    data = {
        "plant_name_en": "'); DROP TABLE plants; --",
        "plant_name_ja": "攻撃植物",
        "plant_class_en": "Evilaceae",
        "plant_class_ja": "アクマ科",
        "image": (BytesIO(b"evil bytes"), "evil.jpg"),
    }

    response = client.post(
        "/plants",
        data=data,
        content_type="multipart/form-data",
        headers={"x-api-key": "skip_2018_0415"},
    )

    assert response.status_code in [400, 201]
