@echo off
REM Run tests for the chatbot service

if "%1"=="unit" (
    echo Running unit tests...
    pytest tests/unit %2 %3
) else if "%1"=="integration" (
    echo Running integration tests...
    pytest tests/integration %2 %3
) else if "%1"=="llm" (
    echo Running LLM service tests...
    pytest tests/llm-service %2 %3
) else if "%1"=="coverage" (
    echo Running all tests with coverage...
    pytest --cov=app --cov-report=term --cov-report=html
) else (
    echo Running all tests...
    pytest
)

exit /b %ERRORLEVEL%