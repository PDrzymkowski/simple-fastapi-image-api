url = "/images/{}"

def test_get_by_id(client, sample_image):
    response = client.get(url.format(sample_image['id']))
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == sample_image["id"]
    assert body["title"] == sample_image["title"]
    assert body["url"] == sample_image["url"]
    assert body["width"] == sample_image["width"]
    assert body["height"] == sample_image["height"]


def test_get_by_id_not_found(client):
    _id = "00000000-0000-0000-0000-000000000000"
    response = client.get(url.format(_id))
    assert response.status_code == 404
    assert response.json()["detail"] == f"Image {_id} not found"
