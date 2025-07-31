import pytest
from uuid import uuid4

from app.schemas.lab_service import LabServiceCreate, TestDefinitionCreate

@pytest.mark.asyncio
async def test_create_lab_service(client):
    payload = {
        "name": "Basic Blood Panel",
        "description": "Basic tests for blood analysis",
        "price": 499.99,
        "test_definitions": [
            {
                "name": "Hemoglobin",
                "unit": "g/dL",
                "reference_range": "13.5-17.5"
            },
            {
                "name": "WBC Count",
                "unit": "cells/mcL",
                "reference_range": "4500-11000"
            }
        ]
    }
    response = await client.post("/api/v1/lab-services/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Basic Blood Panel"
    assert len(data["test_definitions"]) == 2

@pytest.mark.asyncio
async def test_get_lab_services_by_lab(client):
    lab_id = "87654321-4321-4321-8321-210987654321"  # from fake_current_user
    response = await client.get(f"/api/v1/lab-services/by-lab/{lab_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_lab_service(client):
    # Create one first
    create_resp = await client.post("/api/v1/lab-services/", json={
        "name": "Lipid Panel",
        "description": "Cholesterol check",
        "price": 300,
        "test_definitions": []
    })
    service_id = create_resp.json()["id"]

    update_resp = await client.patch(f"/api/v1/lab-services/{service_id}", json={"price": 350})
    assert update_resp.status_code == 200
    assert float(update_resp.json()["price"]) == 350

@pytest.mark.asyncio
async def test_delete_lab_service(client):
    create_resp = await client.post("/api/v1/lab-services/", json={
        "name": "Glucose Test",
        "price": 200,
        "test_definitions": []
    })
    service_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/lab-services/{service_id}")
    assert delete_resp.status_code == 204
