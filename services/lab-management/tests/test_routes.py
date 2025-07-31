import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_available_routes(client: AsyncClient):
    """Test what routes are available."""
    # Test the OpenAPI docs endpoint to see available routes
    response = await client.get("/api/v1/openapi.json")
    if response.status_code == 200:
        openapi_spec = response.json()
        paths = list(openapi_spec.get("paths", {}).keys())
        print("Available paths:", paths)
    
    # Test direct endpoint access
    response = await client.get("/api/v1/test-orders/for-patient/my-orders")
    print(f"my-orders endpoint status: {response.status_code}")
    
    # Test if the main API router is working
    response = await client.get("/api/v1/lab-services/by-lab/87654321-4321-4321-8321-210987654321")
    print(f"lab-services endpoint status: {response.status_code}")
    
    assert True  # Just for debugging