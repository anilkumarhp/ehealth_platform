@echo off
echo Running unit tests...
pytest tests/unit -v

echo.
echo Running integration tests...
echo Note: Integration tests require Redis and gRPC server to be running
pytest tests/integration -v

echo.
echo Running all tests with coverage...
pytest --cov=app tests/