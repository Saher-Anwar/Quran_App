"""Tests for Verse API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_verse_success(client: AsyncClient, sample_verse_data):
    """Test creating a verse successfully."""
    # Act
    response = await client.post("/api/verses/", json=sample_verse_data)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["surah_number"] == sample_verse_data["surah_number"]
    assert data["verse_number"] == sample_verse_data["verse_number"]
    assert data["text_arabic"] == sample_verse_data["text_arabic"]
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_verse_duplicate(client: AsyncClient, sample_verse_data):
    """Test that creating a duplicate verse returns 400."""
    # Arrange - Create verse first time
    await client.post("/api/verses/", json=sample_verse_data)

    # Act - Try to create same verse again
    response = await client.post("/api/verses/", json=sample_verse_data)

    # Assert
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_verse_invalid_surah_number(client: AsyncClient):
    """Test that invalid surah number is rejected."""
    # Arrange
    invalid_data = {
        "surah_number": 115,  # Invalid: only 114 surahs
        "verse_number": 1,
        "text_arabic": "test",
    }

    # Act
    response = await client.post("/api/verses/", json=invalid_data)

    # Assert
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_verse_by_id_success(client: AsyncClient, sample_verse_data):
    """Test retrieving a verse by ID."""
    # Arrange - Create a verse first
    create_response = await client.post("/api/verses/", json=sample_verse_data)
    verse_id = create_response.json()["id"]

    # Act
    response = await client.get(f"/api/verses/{verse_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == verse_id
    assert data["text_arabic"] == sample_verse_data["text_arabic"]


@pytest.mark.asyncio
async def test_get_verse_by_id_not_found(client: AsyncClient):
    """Test that getting non-existent verse returns 404."""
    # Act
    response = await client.get("/api/verses/99999")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_verse_by_reference_success(client: AsyncClient, sample_verse_data):
    """Test retrieving a verse by surah and verse number."""
    # Arrange - Create a verse first
    await client.post("/api/verses/", json=sample_verse_data)

    # Act
    response = await client.get(
        f"/api/verses/reference/{sample_verse_data['surah_number']}/{sample_verse_data['verse_number']}"
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["surah_number"] == sample_verse_data["surah_number"]
    assert data["verse_number"] == sample_verse_data["verse_number"]


@pytest.mark.asyncio
async def test_get_verse_by_reference_not_found(client: AsyncClient):
    """Test that getting non-existent verse by reference returns 404."""
    # Act
    response = await client.get("/api/verses/reference/1/999")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_arabic_text_with_diacritics_preserved(client: AsyncClient, sample_verse_data):
    """Test that Arabic text with diacritics is stored and retrieved correctly."""
    # Arrange & Act
    create_response = await client.post("/api/verses/", json=sample_verse_data)
    verse_id = create_response.json()["id"]
    get_response = await client.get(f"/api/verses/{verse_id}")

    # Assert
    assert get_response.json()["text_arabic"] == sample_verse_data["text_arabic"]
    # Verify diacritics are present
    assert "ِ" in get_response.json()["text_arabic"]  # Kasra diacritic
