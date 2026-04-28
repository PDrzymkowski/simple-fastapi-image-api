
url = '/images'

def test_200__list_empty(client):
    response = client.get(url)
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["page"] == 1
    assert body["size"] == 20


def test_200__returns_image(client, sample_image):
    response = client.get(url)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == sample_image["id"]

def test_200__title_filter__match(client, sample_image):
    response = client.get("/images?title=Sample")
    assert response.status_code == 200
    assert response.json()["total"] == 1

def test_200__title_filter__no_match(client, sample_image):
    response = client.get("/images?title=xyz_no_match")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test200__pagination(client, make_image_file):
    # Upload 3 images
    for i in range(3):
        client.post(
            "/images/upload",
            data={"title": f"Image {i}", "width": "50", "height": "50"},
            files={"file": (f"img{i}.jpg", make_image_file(), "image/jpeg")},
        )

    response = client.get(f"{url}?page=1&size=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["size"] == 2

    response2 = client.get(f"{url}?page=2&size=2")
    assert len(response2.json()["items"]) == 1
