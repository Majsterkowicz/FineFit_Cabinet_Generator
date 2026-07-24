"""Testy warstwy REST API (przez TestClient z izolowanym magazynem)."""


def _new_project(client, name="Projekt API"):
    response = client.post("/api/projects", json={"project_name": name})
    assert response.status_code == 201
    return response.json()["project_id"]


def _new_section(client, project_id, name="Sekcja"):
    response = client.post(
        f"/api/projects/{project_id}/sections",
        json={"section_name": name},
    )
    assert response.status_code == 201
    return response.json()["section_id"]


# --- Config ---------------------------------------------------------------


def test_config_lists_cabinet_types(client):
    data = client.get("/api/config").json()
    names = {entry["name"] for entry in data["cabinet_types"]}
    assert "dolna" in names
    assert "board_thickness" in data


# --- Projekty -------------------------------------------------------------


def test_project_create_get_delete_cycle(client):
    project_id = _new_project(client)

    assert client.get(f"/api/projects/{project_id}").status_code == 200

    deleted = client.delete(f"/api/projects/{project_id}")
    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": project_id}

    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_delete_missing_project_returns_404(client):
    assert client.delete("/api/projects/P999").status_code == 404


def test_create_project_empty_name_returns_400(client):
    response = client.post("/api/projects", json={"project_name": ""})
    assert response.status_code == 422  # walidacja Pydantic (min_length)


# --- Sekcje ---------------------------------------------------------------


def test_section_create_rename_delete(client):
    project_id = _new_project(client)
    section_id = _new_section(client, project_id, "Ściana lewa")

    renamed = client.patch(
        f"/api/projects/{project_id}/sections/{section_id}",
        json={"section_name": "Ściana prawa"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["section_name"] == "Ściana prawa"

    # Regresja: sekcja z prawidłowym ID jest usuwalna (dawniej puste ID -> 405).
    deleted = client.delete(f"/api/projects/{project_id}/sections/{section_id}")
    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": section_id}


# --- Szafki ---------------------------------------------------------------


def test_cabinet_create_update_delete(client):
    project_id = _new_project(client)
    section_id = _new_section(client, project_id)

    payload = dict(cabinet_type="dolna", width=600, height=720,
                   depth=560, shelves=1, fronts=2)

    created = client.post(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets",
        json=payload,
    )
    assert created.status_code == 201
    cabinet_id = created.json()["cabinet_id"]

    updated = client.put(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets/{cabinet_id}",
        json={**payload, "width": 800},
    )
    assert updated.status_code == 200
    assert updated.json()["width"] == 800

    deleted = client.delete(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets/{cabinet_id}"
    )
    assert deleted.status_code == 200


def test_cabinet_unknown_type_returns_400(client):
    project_id = _new_project(client)
    section_id = _new_section(client, project_id)
    response = client.post(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets",
        json=dict(cabinet_type="nieznana", width=600, height=720,
                  depth=560, shelves=1, fronts=2),
    )
    assert response.status_code == 400


# --- Technologia ----------------------------------------------------------


def test_cutting_list_has_rows_and_summary(client):
    project_id = _new_project(client)
    section_id = _new_section(client, project_id)
    client.post(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets",
        json=dict(cabinet_type="dolna", width=600, height=720,
                  depth=560, shelves=1, fronts=2),
    )

    data = client.get(f"/api/projects/{project_id}/cutting-list").json()
    assert data["rows"]
    assert "total_parts" in data["summary"]


def test_pricing_endpoint_returns_total(client):
    project_id = _new_project(client)
    section_id = _new_section(client, project_id)
    client.post(
        f"/api/projects/{project_id}/sections/{section_id}/cabinets",
        json=dict(cabinet_type="dolna", width=600, height=720,
                  depth=560, shelves=1, fronts=2),
    )

    data = client.get(f"/api/projects/{project_id}/pricing").json()
    assert data["total"] > 0
    assert data["currency"]
    assert data["materials"] and data["hardware"]


# --- Ustawienia i ceny projektu -------------------------------------------


def test_settings_get_and_put(client):
    data = client.get("/api/settings").json()
    assert "cabinet_types" in data and "construction" in data

    data["currency"] = "EUR"
    saved = client.put("/api/settings", json=data)
    assert saved.status_code == 200
    assert saved.json()["currency"] == "EUR"
    assert client.get("/api/settings").json()["currency"] == "EUR"


def test_project_prices_get_and_put(client):
    project_id = _new_project(client)

    prices = client.get(f"/api/projects/{project_id}/prices").json()
    assert "material_prices" in prices

    updated = client.put(
        f"/api/projects/{project_id}/prices", json={"edging_price": 7.5})
    assert updated.status_code == 200
    assert updated.json()["edging_price"] == 7.5
